using System.IO.Compression;
using System.Text;
using System.Text.Json;

namespace Roadium.Signer;

internal static class SelfTests
{
    internal const string FixturePassword = "Fixture ' \" $() ` ; password! 2026";
    public static int Run(string directory)
    {
        Directory.CreateDirectory(directory);
        var checks = new List<string>();
        try
        {
            Check(() => SigningService.ValidatePassword("same", "same"), "matching password", checks);
            Reject(() => SigningService.ValidatePassword("", ""), "empty password", checks);
            Reject(() => SigningService.ValidatePassword("same", "different"), "mismatch", checks);
            foreach (var character in new[] { '\r', '\n', '\0' })
                Reject(() => SigningService.ValidatePassword("x" + character, "x" + character), "control character " + (int)character, checks);
            Check(() => SigningService.ValidatePassword(" ø ' \" $() ` ", " ø ' \" $() ` "), "spaces and Unicode preserved", checks);
            Reject(() => (new SignerSettings { Container = "--bad" }).Validate(), "invalid settings", checks);
            FlowTests(directory, checks).GetAwaiter().GetResult();
            UiCheck(directory, 1, checks);
            UiCheck(directory, 2, checks);
            WriteReport(directory, checks, null);
            return 0;
        }
        catch (Exception error) { WriteReport(directory, checks, error.GetType().Name + ": " + error.Message); return 1; }
    }

    private static async Task FlowTests(string directory, List<string> checks)
    {
        var fixture = Path.Combine(directory, "unsigned ñ fixture.aab");
        MakeBundle(fixture, false);
        var originalHash = await SigningService.HashAsync(fixture);
        var target = Path.Combine(directory, "success.aab");
        var password = " spaces ø ' \" $() ` ; end ";
        var fake = new FakeRunner { Password = password };
        var service = new SigningService(new SignerSettings(), fake, "fake-docker");
        var result = await service.SignAsync(fixture, target, password, password);
        Assert(File.Exists(target) && fake.SawPassword && fake.Cleaned && fake.SawStart, "success, stopped-container start, secret transport and cleanup", checks);
        Assert(result.SourceSha256 == originalHash && await SigningService.HashAsync(fixture) == originalHash, "original unchanged", checks);
        Assert(result.SignedSha256 != originalHash, "signed output differs", checks);
        Reject(() => SigningService.ValidateBundle(target), "already signed rejected", checks);
        Reject(() => SigningService.ValidateBundle(Path.Combine(directory, "bad.txt")), "non-aab rejected", checks);
        await RejectAsync(() => service.SignAsync(fixture, target, password, password), "existing output rejected", checks);
        await RejectAsync(() => service.SignAsync(fixture, fixture, password, password), "source overwrite rejected", checks);
        foreach (var code in new[] { 40, 41, 42, 43, 44, 45, 46 })
        {
            var failing = new FakeRunner { Password = password, SignExit = code };
            var failedTarget = Path.Combine(directory, "failed-" + code + ".aab");
            await RejectAsync(() => new SigningService(new SignerSettings(), failing, "fake-docker").SignAsync(fixture, failedTarget, password, password), "tool failure " + code, checks);
            Assert(!File.Exists(failedTarget) && failing.Cleaned, "no export and cleanup " + code, checks);
        }
        var racedTarget = Path.Combine(directory, "race.aab");
        var race = new FakeRunner { Password = password, CollisionTarget = racedTarget };
        await RejectAsync(() => new SigningService(new SignerSettings(), race, "fake-docker").SignAsync(fixture, racedTarget, password, password), "output race rejected", checks);
        Assert(File.ReadAllText(racedTarget) == "KEEP", "output race preserves existing file", checks);
        var tamperedTarget = Path.Combine(directory, "tampered.aab");
        var tampered = new FakeRunner { Password = password, TamperCopy = true };
        await RejectAsync(() => new SigningService(new SignerSettings(), tampered, "fake-docker").SignAsync(fixture, tamperedTarget, password, password), "export hash mismatch rejected", checks);
        Assert(!File.Exists(tamperedTarget), "tampered copy never published", checks);
        var missingDocker = new FakeRunner { InspectExit = 1 };
        await RejectAsync(() => new SigningService(new SignerSettings(), missingDocker, "fake-docker").SignAsync(fixture, Path.Combine(directory, "missing.aab"), password, password), "Docker unavailable", checks);
        Assert(!missingDocker.Created, "no mutation on Docker failure", checks);
        var mismatch = new FakeRunner();
        await RejectAsync(() => new SigningService(new SignerSettings(), mismatch, "fake-docker").SignAsync(fixture, Path.Combine(directory, "mismatch.aab"), password, "wrong"), "password mismatch before Docker", checks);
        Assert(mismatch.Calls == 0, "no Docker call on mismatched passwords", checks);
        Assert(!Directory.EnumerateFiles(directory, ".roadium-sign-*.aab").Any(), "no partial exported files", checks);
    }

    public static async Task<int> Integration(string settingsFile, string unsigned, string directory)
    {
        Directory.CreateDirectory(directory);
        var checks = new List<string>();
        try
        {
            var settings = SignerSettings.Load(settingsFile);
            if (!System.Text.RegularExpressions.Regex.IsMatch(settings.Container, @"^roadium-signer-test-[a-z0-9-]+$") ||
                settings.KeyPath != "/tmp/roadium-signer-fixture/test-upload.p12" || settings.Alias != "fixture-upload")
                throw new Exception("Integration tests require the isolated test container and disposable fixture key.");
            var unicodeTransport = " ø ' \" $() ` ; unchanged ";
            var transport = await new CommandRunner().RunAsync(Program.FindDocker(),
                ["exec", "-i", "-u", settings.User, settings.Container, "python3", "-c", "import sys,hashlib; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())"], unicodeTransport);
            var transportHash = Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(Encoding.UTF8.GetBytes(unicodeTransport)));
            Assert(transport.ExitCode == 0 && transport.Output.Trim() == transportHash, "real UTF8 password transport preserves Unicode and metacharacters", checks);
            var sourceHash = await SigningService.HashAsync(unsigned);
            var service = new SigningService(settings, new CommandRunner(), Program.FindDocker());
            var target = Path.Combine(directory, "fixture-key-signed.aab");
            await RejectAsync(() => service.SignAsync(unsigned, Path.Combine(directory, "wrong-password.aab"), "incorrect", "incorrect"), "real incorrect password rejected", checks);
            Assert(!File.Exists(Path.Combine(directory, "wrong-password.aab")), "real wrong password no output", checks);
            var result = await service.SignAsync(unsigned, target, FixturePassword, FixturePassword);
            Assert(File.Exists(target) && result.CleanupWarning == null, "real signing and strict/bundletool verification", checks);
            Assert(await SigningService.HashAsync(unsigned) == sourceHash, "real unsigned source unchanged", checks);
            SigningService.ValidateBundle(target, true);
            checks.Add("real signed ZIP signature entries");
            await RejectAsync(() => service.SignAsync(target, Path.Combine(directory, "double-sign.aab"), FixturePassword, FixturePassword), "real signed bundle rejected", checks);
            var wrongPackage = settings with { ExpectedPackage = "io.invalid.fixture" };
            await RejectAsync(() => new SigningService(wrongPackage, new CommandRunner(), Program.FindDocker()).SignAsync(unsigned, Path.Combine(directory, "wrong-package.aab"), FixturePassword, FixturePassword), "real wrong package rejected", checks);
            var missingKey = settings with { KeyPath = "/tmp/roadium-signer-fixture/missing.p12" };
            await RejectAsync(() => new SigningService(missingKey, new CommandRunner(), Program.FindDocker()).SignAsync(unsigned, Path.Combine(directory, "missing-key.aab"), FixturePassword, FixturePassword), "real missing key rejected", checks);
            var remaining = await new CommandRunner().RunAsync(Program.FindDocker(), ["exec", "-u", settings.User, settings.Container, "bash", "-c", "find /tmp -maxdepth 1 -name 'roadium-sign-*' -print"]);
            Assert(remaining.ExitCode == 0 && remaining.Output.Trim().Length == 0, "real temporary jobs removed", checks);
            WriteReport(directory, checks, null);
            return 0;
        }
        catch (Exception error) { WriteReport(directory, checks, error.GetType().Name + ": " + error.Message); return 1; }
    }

    private static void UiCheck(string directory, int scale, List<string> checks)
    {
        using var form = new SignerForm(new SignerSettings());
        form.ShowInTaskbar = false;
        form.Opacity = 0;
        form.Show();
        Application.DoEvents();
        if (scale == 2)
        {
            var originalFonts = Walk(form).Select(control => (control, font: control.Font)).ToArray();
            form.Scale(new SizeF(2, 2));
            foreach (var (control, font) in originalFonts) control.Font = new Font(font.FontFamily, font.Size * 2, font.Style);
        }
        form.CreateControl();
        _ = form.Handle;
        foreach (var control in Walk(form)) control.CreateControl();
        form.PerformLayout();
        foreach (var control in Walk(form).Where(c => c is TextBox or Button))
        {
            Assert(!string.IsNullOrWhiteSpace(control.AccessibleName), "accessible " + control.AccessibleName + " scale" + scale, checks);
            Assert(control.Parent!.ClientRectangle.Contains(control.Bounds), "contained " + control.AccessibleName + " scale" + scale + " bounds=" + control.Bounds + " parent=" + control.Parent.ClientRectangle, checks);
        }
        Assert(form.PasswordBox.UseSystemPasswordChar && form.ConfirmationBox.UseSystemPasswordChar, "both passwords masked scale" + scale, checks);
        using var image = new Bitmap(form.Width, form.Height);
        form.DrawToBitmap(image, new Rectangle(Point.Empty, form.Size));
        image.Save(Path.Combine(directory, "signer-ui-" + scale + "x.png"));
        checks.Add("hidden UI render, simulated scale " + scale);
    }
    private static IEnumerable<Control> Walk(Control root)
    {
        foreach (Control child in root.Controls) { yield return child; foreach (var nested in Walk(child)) yield return nested; }
    }
    private static void MakeBundle(string file, bool signed)
    {
        using var zip = ZipFile.Open(file, ZipArchiveMode.Create);
        foreach (var entry in signed ? new[] { "BundleConfig.pb", "base/manifest/AndroidManifest.xml", "META-INF/FIXTURE.SF", "META-INF/FIXTURE.RSA" } : new[] { "BundleConfig.pb", "base/manifest/AndroidManifest.xml" })
        { using var writer = new StreamWriter(zip.CreateEntry(entry).Open()); writer.Write("unit test fixture"); }
    }
    private static void Check(Action action, string name, List<string> checks) { action(); checks.Add(name); }
    private static void Assert(bool value, string name, List<string> checks) { if (!value) throw new Exception(name); checks.Add(name); }
    private static void Reject(Action action, string name, List<string> checks)
    { try { action(); } catch (SignerException) { checks.Add(name); return; } throw new Exception("Accepted " + name); }
    private static async Task RejectAsync(Func<Task<SignResult>> action, string name, List<string> checks)
    { try { await action(); } catch (SignerException) { checks.Add(name); return; } throw new Exception("Accepted " + name); }
    private static void WriteReport(string directory, List<string> checks, string? error)
        => File.WriteAllText(Path.Combine(directory, "results.json"), JsonSerializer.Serialize(new { passed = error == null, count = checks.Count, checks, error }, new JsonSerializerOptions { WriteIndented = true }), new UTF8Encoding(false));

    private sealed class FakeRunner : ICommandRunner
    {
        public string Password = "";
        public int Calls, SignExit, InspectExit;
        public bool SawPassword, Cleaned, Created, SawStart, TamperCopy;
        public string? CollisionTarget;
        private string? remoteSource, remoteSigned;
        public async Task<ProcessResult> RunAsync(string executable, IReadOnlyList<string> arguments, string? input = null)
        {
            Calls++;
            if (Password.Length > 0 && arguments.Any(a => a.Contains(Password, StringComparison.Ordinal))) throw new Exception("Password in argv");
            if (arguments[0] == "inspect") return new ProcessResult(InspectExit, "false\n");
            if (arguments[0] == "start") SawStart = true;
            if (arguments.Contains("mkdir")) Created = true;
            if (arguments[0] == "cp")
            {
                if (arguments[2].EndsWith("/input.aab")) remoteSource = arguments[1];
                else if (arguments[1].EndsWith("/signed.aab"))
                {
                    if (CollisionTarget != null) File.WriteAllText(CollisionTarget, "KEEP");
                    File.Copy(remoteSigned!, arguments[2]);
                    if (TamperCopy) using (var stream = File.Open(arguments[2], FileMode.Append)) stream.WriteByte(1);
                }
            }
            if (arguments.Contains("-i"))
            {
                SawPassword = input == Password + "\n";
                if (!SawPassword) throw new Exception("Password altered");
                if (SignExit != 0) return new ProcessResult(SignExit, "");
                remoteSigned = Path.Combine(Path.GetDirectoryName(remoteSource)!, "remote-signed.aab");
                MakeBundle(remoteSigned, true);
                return new ProcessResult(0, "SIGNED_SHA256:" + await SigningService.HashAsync(remoteSigned) + "\nSTAGE:verified\n");
            }
            if (arguments.Contains("rm")) Cleaned = true;
            return new ProcessResult(0, "");
        }
    }
}
