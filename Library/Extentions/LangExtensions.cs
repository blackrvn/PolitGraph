namespace Library.Extentions
{
    public static class LangExtensions
    {
        public static string De(this IDictionary<string, string>? dict)
            => dict != null && dict.TryGetValue("de", out var v) ? v : "NaN";
    }
}
