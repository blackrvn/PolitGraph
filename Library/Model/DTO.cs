using System.Text.Json.Serialization;

namespace Library.Model
{
    public record class Text(
        int Id,
        [property: JsonPropertyName("text")] Dictionary<string, string> Content
        );
    public record class Member(
        int Id,
        [property: JsonPropertyName("fullname")] string Name
        );
    public record class ObjectId(int Id);
    public record class DataContainer<Type>([property: JsonPropertyName("data")] List<Type> Items);
    public record class Affair(
        int Id,
        [property: JsonPropertyName("title")] Dictionary<string, string> Titles,
        [property: JsonPropertyName("texts")] DataContainer<Text>? Texts
        )
    {
        public override string ToString()
        {
            var sb = new System.Text.StringBuilder();
            sb.AppendLine($"Affair ID: {Id}");
            if (Titles.TryGetValue("de", out var titleDe))
            {
                sb.AppendLine($"Title (DE): {titleDe}");
            }
            sb.AppendLine($"Number of Texts: {Texts?.Items.Count}");
            return sb.ToString();
        }
    }
}
