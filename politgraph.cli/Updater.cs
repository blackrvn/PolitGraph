using Library.Model;
using Library.Service;
using System.Diagnostics;

namespace politgraph.cli
{
    internal class Updater
    {
        /// <summary>
        /// Path to the main executable
        /// </summary>
        private readonly string PATH;

        private readonly StoreageService _storageService;
        private readonly ParliamentServiceClient _client;
        private readonly VectorStore _vectorStore;

        public Updater(StoreageService storageService)
        {
            _storageService = storageService;
            _client = new ParliamentServiceClient();
            _vectorStore = new VectorStore();

            PATH = Path.Combine(AppContext.BaseDirectory, "main.exe");
        }

        /// <summary>
        /// Clears and rebuilds the vector store for all members in storage.
        /// </summary>
        /// <returns></returns>
        public bool UpdateVectors()
        {
            _vectorStore.Clear();
            _vectorStore.AddToCorpus(_storageService.GetAllMembers());
            _vectorStore.BuildCorpus();
            _vectorStore.Transform();
            _vectorStore.AssignVectorsToMembers();
            _storageService.Save();
            return true;
        }

        /// <summary>
        /// Updates data for a specific member.
        /// </summary>
        /// <param name="member"></param>
        /// <returns></returns>
        public bool Update(Member member)
        {

            if (_client.TryAssignMemberDataAsync(member).Result)
            {
                _storageService.AddOrUpdateMember(member);
                _storageService.Save();
                StartProcess(member.Id);
                _storageService.LoadData();
                return true;
            }
            return false;
        }

        /// <summary>
        /// Updates data for all members.
        /// </summary>
        /// <returns></returns>
        public bool Update()
        {
            var members = _client.GetMembersAsync().Result;
            if (members != null)
            {
                _storageService.Save(members);
                StartProcess();
                _storageService.LoadData();
                return true;
            }
            return false;
        }

        /// <summary>
        /// Starts the process to update lemmas.
        /// Process uses spacy to update the lemmas of the stored members
        /// </summary>
        /// <param name="memberId"></param>
        /// <returns></returns>
        private bool StartProcess(int? memberId = null)
        {
            if (memberId == null)
            {
                try
                {
                    using (Process process = Process.Start(PATH))
                    {
                        process.WaitForExit();
                    }
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    return false;
                }

            }
            else
            {
                var startInfo = new ProcessStartInfo();
                startInfo.UseShellExecute = false;
                startInfo.FileName = PATH;
                startInfo.Arguments = memberId.ToString();
                try
                {
                    using (var process = Process.Start(startInfo))
                    {
                        process.WaitForExit();
                    }
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    return false;
                }
            }
        }
    }
}
