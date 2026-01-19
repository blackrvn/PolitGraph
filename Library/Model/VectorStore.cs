using Library;

namespace Library.Model
{
    public interface IVectorStore
    {
        public double[][] Vectorize();
    }


    internal class VectorStore : IVectorStore
    {
        /// <summary>
        /// Map of all the word in the corpus.
        /// Dictionary<word, Dicionary<affairId, count>>
        /// Global count with "affairId = -1"
        /// </summary>
        private readonly Dictionary<string, Dictionary<int, int>> _wordMap = new();
        /// <summary>
        /// Counter for the grand total of words in the given document
        /// <code>
        /// Key: AffairID
        /// Value: Counter
        /// </code>
        /// </summary>
        private readonly Dictionary<int, int> _affairTotalWordCounter = new();
        /// <summary>
        /// Index of the affair in the TF-IDF matrix
        /// </summary>
        private readonly Dictionary<int, List<int>> _memberIndecies = new();

        public double[,] Matrix { get; private set; }

        public VectorStore(IList<Member> members)
        {
            foreach (var member in members)
            {
                for (int i = 0; i < member.Affairs.Count; i++)
                {
                    var affair = member.Affairs[i];
                    var indecies = _memberIndecies[member.Id] ?? new();
                    indecies.Add(i);
                    foreach (var word in affair.Text.Split(" "))
                    {
                        var map = _wordMap[word] ?? new();
                        map[affair.Id]++;
                        map[Constants.WorldWordCounterKey]++;
                        _affairTotalWordCounter[affair.Id]++;
                    }
                }
            }
            Matrix = new double[members.Count, _wordMap.Keys.Count];
        }
        public double[][] Vectorize()
        {
            throw new NotImplementedException();
        }
    }

    public class TestVectorStore : IVectorStore
    {
        public double[][] Vectorize()
        {
            throw new NotImplementedException();
        }
    }
}
