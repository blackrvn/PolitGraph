using Library.Extentions;

namespace Library.Model
{
    public class Affair
    {
        public int Id { get; }
        public string Title { get; }
        public string Text { get; }
        public Affair(AffairDTO dto)
        {
            Id = dto.Id;
            Title = dto.Titles.De();
            Text = FindSubmittedText(dto);

        }

        private string FindSubmittedText(AffairDTO dto)
        {
            var submitted = dto.Texts?.Items
                 .FirstOrDefault(t => t.Type.De() == "Eingereichter TextDTO");
            return submitted?.Content.De() ?? "NaN";
        }
    }
}
