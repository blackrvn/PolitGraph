using System.Text.Json.Serialization;

namespace Library.Model
{
    public class Member
    {
        public int Id { get; }
        [property: JsonPropertyName("firstname")]
        public string FirstName { get; }
        [property: JsonPropertyName("lastname")]
        public string LastName { get; }
        public string Name { get; }
        public Dictionary<int, double> Vector { get; set; }

        public List<Affair> Affairs { get; set; } = new();

        public Member(int id, string firstName, string lastName)
        {
            Id = id;
            FirstName = firstName;
            LastName = lastName;
            Name = $"{FirstName} {LastName}"; // fullname property nicht immer in der selben Form.
        }
    }
}
