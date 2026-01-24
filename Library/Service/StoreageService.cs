using Library.Model;
using System.Text.Json;

namespace Library.Service
{
    public class StoreageService
    {
        private readonly string _filePath;
        private Dictionary<int, Member> Members { get; set; }

        public StoreageService(string filePath)
        {
            _filePath = filePath;
            Members = new();
        }
        public void Save()
        {
            var json = JsonSerializer.Serialize(Members, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(_filePath, json);
        }
        public void LoadData()
        {
            if (File.Exists(_filePath))
            {
                var json = File.ReadAllText(_filePath);
                Members = JsonSerializer.Deserialize<Dictionary<int, Member>>(json) ?? new();
            }
        }

        public ICollection<Member> GetAllMembers()
        {
            return Members.Values;
        }

        public bool TryGetMember(int id, out Member member)
        {
            Members.TryGetValue(id, out member);
            return member != null;
        }

        public void AddOrUpdateMember(Member member)
        {
            Members[member.Id] = member;
        }
    }
}
