using System.Text.Json.Serialization;

namespace Library.Model
{
    public class Member
    {
        public int Id { get; }

        [JsonPropertyName("firstname")]
        public string FirstName { get; }

        [JsonPropertyName("lastname")]
        public string LastName { get; }

        [JsonPropertyName("updated_at")]
        public string UpdatedAt { get; }

        public string Name { get; }

        public Dictionary<int, double> Vector { get; set; } = new();
        public List<Affair> Affairs { get; set; } = new();

        public Member(int id, string firstName, string lastName, string updatedAt)
        {
            Id = id;
            FirstName = firstName;
            LastName = lastName;
            UpdatedAt = updatedAt;
            Name = $"{FirstName} {LastName}";
        }

        public override string ToString()
        {
            return $"{Name} - {Id}";
        }
    }

}
