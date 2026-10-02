using System.Diagnostics;
using System.Reflection;
using System.Text.Json;

namespace Roadium.Signer;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        Application.SetHighDpiMode(HighDpiMode.PerMonitorV2);
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.SetDefaultFont(new Font("Segoe UI", 11));
        if (args.Length == 2 && args[0] == "--self-test") return SelfTests.Run(args[1]);
        if (args.Length == 4 && args[0] == "--integration-test")
            return SelfTests.Integration(args[1], args[2], args[3]).GetAwaiter().GetResult();
        try
        {
            var settings = SignerSettings.Load(Path.Combine(AppContext.BaseDirectory, "signer-settings.json"));
            Application.Run(new SignerForm(settings));
            return 0;
        }
        catch (SignerException error)
        {
            MessageBox.Show(error.Message, "Roadium Bundle Signer", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    internal static string FindDocker()
    {
        var installed = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Docker", "Docker", "resources", "bin", "docker.exe");
        return File.Exists(installed) ? installed : "docker.exe";
    }
}

internal sealed class SignerForm : Form
{
    private static readonly Color Navy = ColorTranslator.FromHtml("#193E74");
    private static readonly Color WarmWhite = ColorTranslator.FromHtml("#F4F1E8");
    private readonly TextBox bundle = new() { ReadOnly = true, AccessibleName = "Unsigned Android App Bundle" };
    private readonly TextBox password = new() { UseSystemPasswordChar = true, AccessibleName = "Upload-key password" };
    private readonly TextBox confirmation = new() { UseSystemPasswordChar = true, AccessibleName = "Confirm upload-key password" };
    private readonly TextBox output = new() { ReadOnly = true, AccessibleName = "Signed bundle output location" };
    private readonly Button browse = new() { Text = "&Browse…", AccessibleName = "Browse for unsigned bundle" };
    private readonly Button saveAs = new() { Text = "Save &as…", AccessibleName = "Choose signed bundle location" };
    private readonly Button sign = new() { Text = "&Sign bundle", AccessibleName = "Sign and verify bundle" };
    private readonly Button openFolder = new() { Text = "Open output &folder", Enabled = false, AutoSize = true, AccessibleName = "Open signed bundle folder" };
    private readonly Label status = new() { Text = "Ready. Choose an unsigned bundle, then enter your saved upload-key password twice.", AutoSize = false, Dock = DockStyle.Fill, AccessibleName = "Signing status" };
    private readonly ProgressBar progress = new() { Dock = DockStyle.Fill, Visible = false, Style = ProgressBarStyle.Marquee, AccessibleName = "Signing in progress" };
    private readonly SigningService service;
    private bool busy;
    private string? completedOutput;

    internal TextBox PasswordBox => password;
    internal TextBox ConfirmationBox => confirmation;

    public SignerForm(SignerSettings settings)
    {
        service = new SigningService(settings, new CommandRunner(), Program.FindDocker());
        Text = "Roadium Bundle Signer";
        BackColor = WarmWhite;
        ForeColor = Navy;
        AutoScaleMode = AutoScaleMode.Dpi;
        AutoScaleDimensions = new SizeF(96, 96);
        ClientSize = new Size(840, 636);
        MinimumSize = new Size(820, 675);
        StartPosition = FormStartPosition.CenterScreen;
        using (var iconStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("Roadium.Icon"))
            if (iconStream != null) Icon = new Icon(iconStream);

        var layout = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(24), ColumnCount = 1, RowCount = 16 };
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        int[] heights = [72, 24, 38, 30, 24, 38, 24, 38, 24, 38, 14, 44, 10, 74, 44, 0];
        foreach (var height in heights) layout.RowStyles.Add(new RowStyle(height == 0 ? SizeType.Percent : SizeType.Absolute, height == 0 ? 100 : height));
        var logo = new PictureBox { SizeMode = PictureBoxSizeMode.Zoom, Dock = DockStyle.Left, Width = 290, AccessibleName = "Roadium Browser" };
        using (var logoStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("Roadium.Wordmark"))
            if (logoStream != null) using (var original = Image.FromStream(logoStream)) logo.Image = new Bitmap(original);
        layout.Controls.Add(logo, 0, 0);
        layout.Controls.Add(Caption("Unsigned bundle"), 0, 1);
        layout.Controls.Add(PathRow(bundle, browse), 0, 2);
        layout.Controls.Add(Caption("Uses your existing Roadium upload key. Keep Docker Desktop running."), 0, 3);
        layout.Controls.Add(Caption("Upload-key password"), 0, 4);
        layout.Controls.Add(password, 0, 5);
        layout.Controls.Add(Caption("Confirm password"), 0, 6);
        layout.Controls.Add(confirmation, 0, 7);
        layout.Controls.Add(Caption("Save signed bundle to"), 0, 8);
        layout.Controls.Add(PathRow(output, saveAs), 0, 9);
        layout.Controls.Add(sign, 0, 11);
        layout.Controls.Add(progress, 0, 12);
        layout.Controls.Add(status, 0, 13);
        layout.Controls.Add(openFolder, 0, 14);
        foreach (var text in new[] { bundle, password, confirmation, output })
        {
            text.Dock = DockStyle.Fill;
            text.Margin = new Padding(0, 2, 0, 2);
        }
        sign.Dock = DockStyle.Left;
        sign.Width = 180;
        sign.BackColor = Navy;
        sign.ForeColor = WarmWhite;
        sign.FlatStyle = FlatStyle.Flat;
        sign.FlatAppearance.BorderSize = 0;
        sign.UseVisualStyleBackColor = false;
        Controls.Add(layout);
        // Table rows establish keyboard order; nested path panels order their own children.
        logo.TabStop = false;
        bundle.TabStop = false;
        output.TabStop = false;
        browse.TabIndex = 0;
        password.TabIndex = 5;
        confirmation.TabIndex = 7;
        saveAs.TabIndex = 0;
        sign.TabIndex = 11;
        openFolder.TabIndex = 14;
        foreach (Control child in layout.Controls) child.TabIndex = layout.GetRow(child);
        browse.Click += (_, _) => BrowseBundle();
        saveAs.Click += (_, _) => ChooseOutput();
        sign.Click += async (_, _) => await SignBundle();
        openFolder.Click += (_, _) => OpenOutputFolder();
        FormClosing += (_, e) => { if (busy) e.Cancel = true; };
        AcceptButton = sign;
    }

    private static Label Caption(string text) => new() { Text = text, Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleLeft, AutoSize = false };
    private static TableLayoutPanel PathRow(TextBox text, Button button)
    {
        var row = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2, Margin = Padding.Empty };
        row.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        row.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 110));
        row.Controls.Add(text, 0, 0);
        row.Controls.Add(button, 1, 0);
        button.Dock = DockStyle.Fill;
        button.Margin = new Padding(8, 0, 0, 0);
        return row;
    }
    private void BrowseBundle()
    {
        using var dialog = new OpenFileDialog { Title = "Choose an unsigned Android App Bundle", Filter = "Android App Bundles (*.aab)|*.aab", CheckFileExists = true, Multiselect = false };
        if (dialog.ShowDialog(this) != DialogResult.OK) return;
        bundle.Text = dialog.FileName;
        output.Text = Path.Combine(Path.GetDirectoryName(dialog.FileName)!, Path.GetFileNameWithoutExtension(dialog.FileName) + "-signed.aab");
        completedOutput = null;
        openFolder.Enabled = false;
        status.Text = "Bundle selected. Enter your existing upload-key password twice.";
        password.Focus();
    }
    private void ChooseOutput()
    {
        using var dialog = new SaveFileDialog { Title = "Choose a new signed bundle filename", Filter = "Android App Bundles (*.aab)|*.aab", DefaultExt = "aab", AddExtension = true, OverwritePrompt = true, FileName = output.Text };
        if (dialog.ShowDialog(this) == DialogResult.OK)
        {
            output.Text = dialog.FileName;
            completedOutput = null;
            openFolder.Enabled = false;
        }
    }
    private async Task SignBundle()
    {
        if (busy) return;
        completedOutput = null;
        openFolder.Enabled = false;
        try
        {
            SigningService.ValidatePassword(password.Text, confirmation.Text);
            if (string.IsNullOrEmpty(bundle.Text) || string.IsNullOrEmpty(output.Text)) throw new SignerException("Choose an unsigned bundle and an output location first.");
            SetBusy(true);
            var secret = password.Text;
            var repeated = confirmation.Text;
            password.Clear();
            confirmation.Clear();
            var updates = new Progress<string>(message => status.Text = message);
            var result = await service.SignAsync(bundle.Text, output.Text, secret, repeated, updates);
            completedOutput = result.OutputPath;
            status.Text = "Signed and verified. Upload the signed .aab file to your existing Play Console app.\n" + (result.CleanupWarning ?? "Your unsigned bundle was preserved.");
        }
        catch (SignerException error) { status.Text = error.Message; }
        catch { status.Text = "Signing could not finish. Check file permissions and free disk space, then try again."; }
        finally
        {
            password.Clear();
            confirmation.Clear();
            SetBusy(false);
        }
    }
    private void SetBusy(bool value)
    {
        busy = value;
        foreach (Control control in new Control[] { browse, saveAs, bundle, output, password, confirmation, sign }) control.Enabled = !value;
        openFolder.Enabled = !value && completedOutput != null;
        progress.Visible = value;
        UseWaitCursor = value;
    }
    private void OpenOutputFolder()
    {
        if (completedOutput == null) return;
        try
        {
            var info = new ProcessStartInfo("explorer.exe") { UseShellExecute = false };
            info.ArgumentList.Add(Path.GetDirectoryName(completedOutput)!);
            Process.Start(info)?.Dispose();
        }
        catch { status.Text = "Could not open File Explorer. The signed file is at the output location shown above."; }
    }
}
