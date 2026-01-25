using System.Text.Json.Serialization;

namespace Library.Model
{
    public class Affair
    {
        public int Id { get; }
        public string Title { get; }
        public string TextRaw { get; }
        public string[] Lemmas { get; }

        public Dictionary<int, double> Vector { get; set; } = new();

        [JsonConstructor]
        public Affair(int id, string title, string textRaw, string[] lemmas)
        {
            Id = id;
            Title = title;
            TextRaw = textRaw;
            Lemmas = lemmas;
        }

        public Affair(AffairDTO dto)
        {
            Id = dto.Id;
            Title = dto.Title;
            TextRaw = FindSubmittedText(dto);
        }

        private string FindSubmittedText(AffairDTO dto)
        {
            var submitted = dto.Texts?.Items
                 .FirstOrDefault(t => t.Type == "Eingereichter Text");
            return submitted?.Content ?? "NaN";
        }

        public override string ToString()
        {
            return $"{Title} - {Id}";
        }
    }
}
