namespace politgraph.lib.Models
{
    public class MemberModel
    {
        public int MemberId { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }

        public string? Party { get; set; }
    }
}
