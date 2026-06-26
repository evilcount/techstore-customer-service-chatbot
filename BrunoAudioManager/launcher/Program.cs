using System;
using System.Diagnostics;
using System.IO;
using System.Text;

namespace BrunoAudioManager.Launcher
{
    internal static class Program
    {
        private static string Quote(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }

        private static string FindScriptPath()
        {
            string executableDirectory = AppDomain.CurrentDomain.BaseDirectory;
            string[] candidates =
            {
                Path.Combine(executableDirectory, "BrunoAudioManager.ps1"),
                Path.Combine(executableDirectory, "..", "BrunoAudioManager.ps1"),
                Path.Combine(executableDirectory, "..", "..", "BrunoAudioManager.ps1"),
                Path.Combine(executableDirectory, "..", "..", "..", "BrunoAudioManager.ps1")
            };

            foreach (string candidate in candidates)
            {
                string fullPath = Path.GetFullPath(candidate);
                if (File.Exists(fullPath))
                {
                    return fullPath;
                }
            }

            throw new FileNotFoundException("BrunoAudioManager.ps1 was not found next to the launcher.");
        }

        private static int Main(string[] args)
        {
            try
            {
                string scriptPath = FindScriptPath();
                StringBuilder arguments = new StringBuilder();
                arguments.Append("-NoProfile -ExecutionPolicy Bypass -File ");
                arguments.Append(Quote(scriptPath));

                foreach (string arg in args)
                {
                    arguments.Append(' ');
                    arguments.Append(Quote(arg));
                }

                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "pwsh.exe",
                    Arguments = arguments.ToString(),
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.GetDirectoryName(scriptPath)
                };

                using (Process process = Process.Start(startInfo))
                {
                    if (process == null)
                    {
                        return 1;
                    }

                    process.WaitForExit();
                    return process.ExitCode;
                }
            }
            catch (Exception ex)
            {
                File.WriteAllText(
                    Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "BrunoAudioManager.Launcher.error.log"),
                    ex.ToString());
                return 1;
            }
        }
    }
}
