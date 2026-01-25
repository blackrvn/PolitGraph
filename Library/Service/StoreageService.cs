using Library.Model;
using System.Text.Json;

namespace Library.Service
{
    public class StoreageService
    {
        /// <summary>
        /// Path to the storage file
        /// </summary>
        private readonly string _filePath;
        private Dictionary<int, Member> Members { get; set; }

        public StoreageService(string filePath)
        {
            _filePath = filePath;
            Members = new();
        }
        /// <summary>
        /// Saves the current members to the storage file.
        /// </summary>
        public void Save()
        {
            var json = JsonSerializer.Serialize(Members, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(_filePath, json);
        }

        /// <summary>
        /// Loads the members from the storage file.
        /// </summary>
        public void LoadData()
        {
            if (File.Exists(_filePath))
            {
                var json = File.ReadAllText(_filePath);
                Members = JsonSerializer.Deserialize<Dictionary<int, Member>>(json) ?? new();
            }
        }

        /// <summary>
        /// Returns all members in storage.
        /// </summary>
        /// <returns></returns>
        public ICollection<Member> GetAllMembers()
        {
            return Members.Values;
        }

        /// <summary>
        /// Tries to get a member by its ID.
        /// </summary>
        /// <param name="id"></param>
        /// <param name="member"></param>
        /// <returns></returns>
        public bool TryGetMember(int id, out Member member)
        {
            Members.TryGetValue(id, out member);
            return member != null;
        }

        /// <summary>
        /// Adds or updates a member in storage.
        /// </summary>
        /// <param name="member"></param>
        public void AddOrUpdateMember(Member member)
        {
            Members[member.Id] = member;
        }
    }
}
