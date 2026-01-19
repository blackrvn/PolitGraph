namespace Library.Extension
{

    public static class DictionaryExtensions
    {

        public static void Increment<TKey>(
            this IDictionary<TKey, int> dict,
            TKey key,
            int delta = 1)
        {
            dict[key] = dict.TryGetValue(key, out var value)
                ? value + delta
                : delta;
        }
    }

}
