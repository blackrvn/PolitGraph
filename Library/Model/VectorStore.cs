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
        /// Index of the affair in the TF-IDF matrix
        /// </summary>
        private readonly Dictionary<int, int> _affairIndex = new();

        public double[][] Matrix { get; private set; }

        public VectorStore(IList<Member> members)
        {

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
