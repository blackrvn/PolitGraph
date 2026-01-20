using Python.Runtime;

namespace Library.Service
{
    public sealed class Dyson : IDisposable
    {
        dynamic nlpWorker;

        /// <summary>
        /// Bridge to the python workers
        /// </summary>
        public Dyson()
        {
            // TODO: Robuste Struktur entwerfen, die auch deployed werden kann
            #region ChatGpt
            //Erstellt durch ChatGpt 5.2 am 20.01.2026

            var pythonDllPath = "C:\\Users\\iblto\\AppData\\Local\\Programs\\Python\\Python313\\python313.dll";
            var pythonBase = @"C:\Users\iblto\AppData\Local\Programs\Python\Python313";
            var venvSitePkgs = @"C:\Users\iblto\source\repos\blackrvn\PolitGraph\politgraph.py\env\Lib\site-packages";
            var workerDir = @"C:\Users\iblto\source\repos\blackrvn\PolitGraph\politgraph.py";
            var appBase = AppContext.BaseDirectory;

            Runtime.PythonDLL = pythonDllPath;

            var paths = new[]
            {
                Path.Combine(pythonBase, "python313.zip"),
                Path.Combine(pythonBase, "DLLs"),
                Path.Combine(pythonBase, "Lib"),
                pythonBase,
                venvSitePkgs,
                workerDir,
                appBase
            };

            PythonEngine.PythonPath = string.Join(Path.PathSeparator, paths);
            PythonEngine.Initialize();
            using (Py.GIL())
            {
                dynamic worker = Py.Import("nlp_worker");
                nlpWorker = worker.load_nlp();
            }
            #endregion
        }

        public void Dispose()
        {
            try
            {
                PythonEngine.Shutdown();
            }
            catch (PlatformNotSupportedException ex)
            {
                // Shutdown nutzt BinaryFormatter -> nicht mehr unterstützt in .net 9.0.
                // Aktueller workaround ist ein leerer catch-block
            }
        }

        public string[] Lemmatize(string text)
        {
            using (Py.GIL())
            {
                dynamic worker = Py.Import("lemmatize_worker");
                dynamic result = worker.lemmatize(text, nlpWorker);
                return result.As<string[]>();
            }
        }
    }
}
