using System.Diagnostics;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Roadium.Signer;

public sealed record SignerSettings
{
    public string Container { get; init; } = "roadium-baseline-153";
    public string User { get; init; } = "lg";
    public string KeyPath { get; init; } = "/home/lg/working_dir/roadium-signing-private/roadium-upload.p12";
    public string Alias { get; init; } = "roadium-upload";
    public string JdkBin { get; init; } = "/home/lg/working_dir/chromium/src/third_party/jdk/current/bin";
    public string Bundletool { get; init; } = "/home/lg/working_dir/chromium/src/third_party/android_build_tools/bundletool/cipd/bundletool.jar";
    public string ExpectedPackage { get; init; } = "io.github.musicpizzaman.roadium";

    public void Validate()
    {
        if (!Regex.IsMatch(Container, @"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$") ||
            !Regex.IsMatch(User, @"^[a-zA-Z0-9_][a-zA-Z0-9_.-]*$") ||
            !Regex.IsMatch(Alias, @"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$") ||
            !Regex.IsMatch(ExpectedPackage, @"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)+$") ||
            new[] { KeyPath, JdkBin, Bundletool }.Any(p => !p.StartsWith('/') || p.IndexOfAny(['\r', '\n', '\0']) >= 0))
            throw new SignerException("The signer settings are invalid. Restore signer-settings.json from the project.");
    }

    public static SignerSettings Load(string file)
    {
        try
        {
            var settings = JsonSerializer.Deserialize<SignerSettings>(File.ReadAllText(file))
                ?? throw new JsonException();
            settings.Validate();
            return settings;
        }
        catch (SignerException) { throw; }
        catch { throw new SignerException("Cannot read signer-settings.json. Keep it beside the application."); }
    }
}

public sealed class SignerException(string message) : Exception(message);
public sealed record ProcessResult(int ExitCode, string Output);
public interface ICommandRunner
{
    Task<ProcessResult> RunAsync(string executable, IReadOnlyList<string> arguments, string? input = null);
}

public sealed class CommandRunner : ICommandRunner
{
    public async Task<ProcessResult> RunAsync(string executable, IReadOnlyList<string> arguments, string? input = null)
    {
        var info = new ProcessStartInfo(executable)
        {
            UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardInput = true, RedirectStandardOutput = true, RedirectStandardError = true,
            StandardInputEncoding = new UTF8Encoding(false),
            StandardOutputEncoding = Encoding.UTF8, StandardErrorEncoding = Encoding.UTF8
        };
        foreach (var argument in arguments) info.ArgumentList.Add(argument);
        using var process = new Process { StartInfo = info };
        using var timeout = new CancellationTokenSource(TimeSpan.FromMinutes(15));
        try
        {
            process.Start();
            var stdout = process.StandardOutput.ReadToEndAsync(timeout.Token);
            var stderr = process.StandardError.ReadToEndAsync(timeout.Token);
            if (input != null) await process.StandardInput.WriteAsync(input.AsMemory(), timeout.Token);
            process.StandardInput.Close();
            await process.WaitForExitAsync(timeout.Token);
            var output = await stdout;
            await stderr; // Drain diagnostics, but never expose subprocess messages containing secrets.
            return new ProcessResult(process.ExitCode, output);
        }
        catch (OperationCanceledException)
        {
            try { process.Kill(entireProcessTree: true); } catch { }
            throw new SignerException("Signing took too long. Check Docker Desktop, then try again.");
        }
        catch
        {
            try { if (!process.HasExited) process.Kill(entireProcessTree: true); } catch { }
            throw new SignerException("Could not run the signing tools. Start Docker Desktop, then try again.");
        }
    }
}

public sealed record SignResult(string OutputPath, string SourceSha256, string SignedSha256, string? CleanupWarning);

public sealed class SigningService(SignerSettings settings, ICommandRunner runner, string dockerExecutable)
{
    public static void ValidatePassword(string password, string confirmation)
    {
        if (password.Length == 0) throw new SignerException("Enter your existing upload-key password twice.");
        if (!string.Equals(password, confirmation, StringComparison.Ordinal))
            throw new SignerException("The passwords do not match. Enter the same password in both fields.");
        if (password.IndexOfAny(['\r', '\n', '\0']) >= 0)
            throw new SignerException("The password cannot contain a line break or a null character.");
    }

    public static void ValidateBundle(string path, bool signed = false)
    {
        if (!string.Equals(Path.GetExtension(path), ".aab", StringComparison.OrdinalIgnoreCase))
            throw new SignerException("Choose an Android App Bundle (.aab).");
        try
        {
            using var zip = ZipFile.OpenRead(path);
            if (zip.GetEntry("BundleConfig.pb") == null || zip.GetEntry("base/manifest/AndroidManifest.xml") == null)
                throw new SignerException("This file is not an Android App Bundle.");
            var hasSignature = zip.Entries.Any(e => Regex.IsMatch(e.FullName, @"^META-INF/[^/]+\.(SF|RSA|DSA|EC)$", RegexOptions.IgnoreCase));
            if (hasSignature != signed)
                throw new SignerException(signed ? "The exported bundle has no signature." : "This bundle is already signed. Choose the unsigned bundle.");
        }
        catch (SignerException) { throw; }
        catch { throw new SignerException("Cannot read the bundle. Choose a readable, valid .aab file."); }
    }

    public async Task<SignResult> SignAsync(string source, string destination, string password, string confirmation, IProgress<string>? progress = null)
    {
        ValidatePassword(password, confirmation);
        settings.Validate();
        source = Path.GetFullPath(source);
        destination = Path.GetFullPath(destination);
        if (string.Equals(source, destination, StringComparison.OrdinalIgnoreCase))
            throw new SignerException("Save the signed bundle to a different file from the unsigned bundle.");
        if (!string.Equals(Path.GetExtension(destination), ".aab", StringComparison.OrdinalIgnoreCase) ||
            !Directory.Exists(Path.GetDirectoryName(destination)))
            throw new SignerException("Choose an existing folder and an output filename ending in .aab.");
        if (File.Exists(destination) || Directory.Exists(destination))
            throw new SignerException("That output already exists. Choose a new filename; existing files are never overwritten.");
        ValidateBundle(source);

        var id = Guid.NewGuid().ToString("N");
        var localJob = Path.Combine(Path.GetTempPath(), "roadium-sign-" + id);
        var remoteJob = "/tmp/roadium-sign-" + id;
        var stagedOutput = Path.Combine(Path.GetDirectoryName(destination)!, ".roadium-sign-" + id + ".aab");
        Directory.CreateDirectory(localJob);
        var remoteCreated = false;
        string? cleanupWarning = null;
        SignResult? result = null;
        try
        {
            progress?.Report("Preparing a copy of your unsigned bundle…");
            var snapshot = Path.Combine(localJob, "input.aab");
            await using (var original = new FileStream(source, FileMode.Open, FileAccess.Read, FileShare.Read, 1048576, true))
            await using (var copy = new FileStream(snapshot, FileMode.CreateNew, FileAccess.Write, FileShare.None, 1048576, true))
                await original.CopyToAsync(copy);
            ValidateBundle(snapshot);
            var sourceSha = await HashAsync(snapshot);
            var helper = Path.Combine(localJob, "sign-bundle.sh");
            using (var embedded = typeof(SigningService).Assembly.GetManifestResourceStream("RoadiumBundleSigner.sign-bundle.sh")
                ?? throw new SignerException("The signing helper is missing. Reinstall this application."))
            await using (var file = File.Create(helper)) await embedded.CopyToAsync(file);

            progress?.Report("Connecting to Docker Desktop…");
            var inspect = await Docker("inspect", "--type", "container", "--format", "{{.State.Running}}", settings.Container);
            if (inspect.ExitCode != 0)
                throw new SignerException("Cannot find the signing container. Start Docker Desktop and check that " + settings.Container + " still exists.");
            if (inspect.Output.Trim() == "false") await Require("Could not start the signing container.", "start", settings.Container);
            else if (inspect.Output.Trim() != "true") throw new SignerException("Cannot read the signing container status.");
            await Require("Could not create the temporary signing folder.", "exec", "-u", settings.User, settings.Container, "mkdir", "-m", "700", remoteJob);
            remoteCreated = true;
            await Require("Could not copy the unsigned bundle into Docker.", "cp", snapshot, settings.Container + ":" + remoteJob + "/input.aab");
            await Require("Could not copy the signing helper into Docker.", "cp", helper, settings.Container + ":" + remoteJob + "/sign-bundle.sh");
            await Require("Could not prepare the signing files.", "exec", "-u", "root", settings.Container, "chown", settings.User, remoteJob + "/input.aab", remoteJob + "/sign-bundle.sh");
            progress?.Report("Validating, signing, and verifying the bundle. This may take a few minutes…");
            var signArgs = new[] { "exec", "-i", "-u", settings.User, settings.Container, "bash", remoteJob + "/sign-bundle.sh",
                remoteJob, settings.KeyPath, settings.Alias, settings.JdkBin, settings.Bundletool, settings.ExpectedPackage, sourceSha };
            var signed = await runner.RunAsync(dockerExecutable, signArgs, password + "\n");
            if (signed.ExitCode != 0) throw new SignerException(signed.ExitCode switch
            {
                40 => "The unsigned bundle did not pass validation. It has not been exported.",
                41 => "This bundle belongs to a different app. Choose a Roadium bundle.",
                42 => "Signing failed. Check your saved upload-key password and try again.",
                43 => "Signature verification failed. No signed bundle was exported.",
                44 => "The signed bundle failed Android validation. No bundle was exported.",
                45 => "Your existing upload key is missing or unreadable in the signing container. Restore the original key before signing.",
                46 => "The JDK or bundletool is missing in the signing container.",
                _ => "The signing tools stopped before verification. Check Docker Desktop and try again."
            });
            var verifiedHash = Regex.Match(signed.Output, @"(?m)^SIGNED_SHA256:([a-f0-9]{64})\r?$");
            if (!verifiedHash.Success || !signed.Output.Contains("STAGE:verified", StringComparison.Ordinal))
                throw new SignerException("The signing tools did not confirm verification. No bundle was exported.");
            progress?.Report("Saving your verified signed bundle…");
            await Require("Could not copy the verified bundle out of Docker.", "cp", settings.Container + ":" + remoteJob + "/signed.aab", stagedOutput);
            ValidateBundle(stagedOutput, signed: true);
            var signedSha = await HashAsync(stagedOutput);
            if (!string.Equals(signedSha, verifiedHash.Groups[1].Value, StringComparison.Ordinal))
                throw new SignerException("The exported bundle did not match the verified copy. Try again.");
            try { File.Move(stagedOutput, destination, overwrite: false); }
            catch (IOException) { throw new SignerException("Could not save the signed bundle. The output may already exist; choose a new filename."); }
            result = new SignResult(destination, sourceSha, signedSha, null);
        }
        finally
        {
            if (remoteCreated)
            {
                try
                {
                    var cleanup = await Docker("exec", "-u", settings.User, settings.Container, "rm", "-rf", "--", remoteJob);
                    if (cleanup.ExitCode != 0) cleanupWarning = "Temporary Docker files could not be removed. Your signed bundle is still valid.";
                }
                catch { cleanupWarning = "Temporary Docker files could not be removed. Your signed bundle is still valid."; }
            }
            try { if (File.Exists(stagedOutput)) File.Delete(stagedOutput); } catch { }
            try { Directory.Delete(localJob, recursive: true); } catch { }
        }
        return result! with { CleanupWarning = cleanupWarning };
    }

    public static async Task<string> HashAsync(string path)
    {
        await using var file = File.OpenRead(path);
        return Convert.ToHexStringLower(await SHA256.HashDataAsync(file));
    }
    private Task<ProcessResult> Docker(params string[] args) => runner.RunAsync(dockerExecutable, args);
    private async Task Require(string message, params string[] args)
    {
        if ((await Docker(args)).ExitCode != 0) throw new SignerException(message);
    }
}
