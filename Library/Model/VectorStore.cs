using Library.Extension;
using Library.Service;

namespace Library.Model
{
    public interface IVectorStore
    {
        public void Transform();
    }


    public class VectorStore : IVectorStore
    {
        /// <summary>
        /// Set of members in the corpus
        /// </summary>
        private readonly HashSet<Member> _members = new();

        /// <summary>
        /// Lookup map for the <see cref="_words"/> list.
        /// </summary>
        private Dictionary<string, int> _wordIndex;
        /// <summary>
        /// Final list of words, ordered lexicographically
        /// </summary>
        private List<string> _words;
        /// <summary>
        /// Set of words, that appear in a given document
        /// </summary>
        private readonly Dictionary<int, HashSet<string>> _documentWordBag = new();
        /// <summary>
        /// The sparse kvp for the given document.
        /// <code>
        /// Key 1: AffairId
        /// Value 1: Dictionary<int, double>
        /// Key 2: Index of the Word in the final word-list
        /// Value 2: TF-IDF value for the given word / index
        /// </code>
        /// </summary>
        private readonly Dictionary<int, Dictionary<int, double>> _documentSparseVectors = new();
        /// <summary>
        /// Map of all the word in the corpus.
        /// <code>Dictionary<word, Dicionary<affair, count>></code>
        /// </summary>
        private readonly Dictionary<string, Dictionary<int, int>> _features = new();
        /// <summary>
        /// Counter for the grand total of words in the given document
        /// <code>
        /// Key: AffairID
        /// Value: Counter
        /// </code>
        /// </summary>
        private readonly Dictionary<int, int> _documentTotalWordCounter = new();


        public void Clear()
        {
            _members.Clear();
            _features.Clear();
            _documentTotalWordCounter.Clear();
            _documentWordBag.Clear();
            _documentSparseVectors.Clear();
            _wordIndex = new();
            _words = new();
        }

        /// <summary>
        /// Adds multiple members to the corpus
        /// </summary>
        /// <param name="members"></param>
        public void AddToCorpus(ICollection<Member> members)
        {
            foreach (var member in members)
            {
                _members.Add(member);
            }
        }

        /// <summary>
        /// Builds the corpus from the added members
        /// </summary>
        public void BuildCorpus()
        {
            foreach (var member in _members)
            {
                for (int i = 0; i < member.Affairs.Count; i++)
                {
                    var affair = member.Affairs[i];
                    var words = affair.Lemmas;

                    foreach (var word in words)
                    {
                        if (!_features.TryGetValue(word, out var map))
                        {
                            map = new();
                            _features[word] = map;
                        }

                        map.Increment(affair.Id);
                        _documentTotalWordCounter.Increment(affair.Id);
                        if (!_documentWordBag.TryGetValue(affair.Id, out var bag))
                        {
                            bag = new();
                            _documentWordBag[affair.Id] = bag;
                        }
                        bag.Add(word);
                    }
                }
            }
            _words = _features.Keys.Order().ToList();
            _wordIndex = _words.Select((w, i) => (w, i)).ToDictionary(x => x.w, x => x.i);
        }

        /// <summary>
        /// Transforms the corpus into a matrix using TF-IDF.
        /// Uses the corpus thas has been prebuilt in <see cref="VectorStore(IList{Member})"/>
        /// </summary>
        public void Transform()
        {
            foreach (var kvp in _documentWordBag)
            {
                var affairId = kvp.Key;
                foreach (var word in kvp.Value)
                {
                    double tf = 0;
                    double idf = 0;
                    var wordCountMap = _features[word];
                    if (wordCountMap.TryGetValue(affairId, out var counter)
                        && _documentTotalWordCounter.TryGetValue(affairId, out var totalWordCounter))
                    {
                        tf = (double)counter / (double)totalWordCounter;
                    }
                    var numberDocumentContainingWord = wordCountMap.Keys.Count;
                    var numberDocuments = _documentWordBag.Keys.Count;

                    if (numberDocuments > 0)
                    {
                        idf = Math.Log2((double)numberDocuments / (double)numberDocumentContainingWord);
                    }

                    if (!_documentSparseVectors.TryGetValue(kvp.Key, out var sparseVectors))
                    {
                        sparseVectors = new();
                        _documentSparseVectors[kvp.Key] = sparseVectors;
                    }
                    sparseVectors[_wordIndex[word]] = tf * idf;
                }
            }
            foreach (var kvp in _documentSparseVectors)
            {
                VectorCalculationService.Normalize(kvp.Value);
            }
        }

        /// <summary>
        /// Assigns the calculated vectors to the members in the corpus
        /// </summary>
        public void AssignVectorsToMembers()
        {
            foreach (var member in _members)
            {
                member.Vector = GetVectorForMember(member);
            }
        }

        /// <summary>
        /// Return the sparse vectors associated with the affairs of the given member
        /// </summary>
        /// <param name="member"></param>
        /// <returns></returns>
        public List<Dictionary<int, double>> GetSparseVectors(Member member)
        {
            var ids = member.Affairs.Select(a => a.Id).ToHashSet();
            return _documentSparseVectors.Where(kvp => ids.Contains(kvp.Key)).Select(kvp => kvp.Value).ToList();

        }

        /// <summary>
        /// Calculates the mean normalized vector for the given member
        /// </summary>
        /// <param name="member"></param>
        /// <returns></returns>
        public Dictionary<int, double> GetVectorForMember(Member member)
        {
            var vectors = GetSparseVectors(member);
            var meanVector = VectorCalculationService.SparseVectorMean(vectors);
            return VectorCalculationService.Normalize(meanVector);
        }
    }

    public class TestVectorStore : IVectorStore
    {
        public void Transform()
        {
            throw new NotImplementedException();
        }
    }
}
