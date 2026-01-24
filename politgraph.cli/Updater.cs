using Library.Model;
using Library.Service;
using System.Diagnostics;

namespace politgraph.cli
{
    internal class Updater
    {
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

        public bool Update(Member member)
        {
            _client.AssignMemberDataAsync(member).Wait();
            _storageService.AddOrUpdateMember(member);
            _storageService.Save();
            using (Process process = Process.Start(PATH))
            {
                process.WaitForExit();
            }
            _storageService.LoadData();
            return true;
        }

        public bool Update()
        {
            var members = _client.GetMembersAsync().Result;
            if (members != null)
            {
                _storageService.Save();
                using (Process process = Process.Start(PATH))
                {
                    process.WaitForExit();
                }
                _storageService.LoadData();
                return true;
            }
            return false;
        }

    }
}
