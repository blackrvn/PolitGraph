namespace Library.Service
{
    public static class VectorCalculationService
    {
        /// <summary>
        /// Computes the cosine similarity of the given sparse vectors
        /// </summary>
        /// <param name="sparseVectorA"></param>
        /// <param name="sparseVectorB"></param>
        /// <returns></returns>
        public static double CosineSimilarity(Dictionary<int, double> sparseVectorA, Dictionary<int, double> sparseVectorB)
        {
            var dotProduct = DotProduct(sparseVectorA, sparseVectorB);
            var lengthA = EuclideanNorm(sparseVectorA);
            var lengthB = EuclideanNorm(sparseVectorB);
            return dotProduct / lengthA * lengthB;
        }

        /// <summary>
        /// Computes the dot-product of the given sparse vectors
        /// </summary>
        /// <param name="sparseVectorA"></param>
        /// <param name="sparseVectorB"></param>
        /// <returns></returns>
        private static double DotProduct(Dictionary<int, double> sparseVectorA, Dictionary<int, double> sparseVectorB)
        {
            double dotProduct = 0;
            foreach (var kvp in sparseVectorA)
            {
                var index = kvp.Key;
                var value = kvp.Value;
                if (sparseVectorB.TryGetValue(index, out double result))
                {
                    dotProduct += value * result;
                }

            }
            return dotProduct;
        }
        /// <summary>
        /// Calculates an euclidean norm factor of the given sparse vector
        /// </summary>
        /// <param name="sparseVector">
        /// Sparse vector
        /// <code>
        /// Key: index
        /// Value: weight
        /// </code>
        /// </param>
        /// <returns></returns>
        public static double EuclideanNorm(Dictionary<int, double> sparseVector)
        {
            double sum = 0;
            foreach (var kvp in sparseVector)
            {
                var value = kvp.Value;
                sum += value * value;
            }
            return Math.Sqrt(sum);
        }

        /// <summary>
        /// Normalizes the given sparse vector<br/>
        /// Uses <see cref="EuclideanNorm(Dictionary{int, double})"/>
        /// </summary>
        /// <param name="vector"></param>
        /// <returns></returns>
        public static Dictionary<int, double> Normalize(Dictionary<int, double> vector)
        {
            var norm = EuclideanNorm(vector);
            foreach (var kvp in vector)
            {
                vector[kvp.Key] = kvp.Value / norm;
            }
            return vector;
        }

        /// <summary>
        /// Computes a mean of the given sparse vectors<br/>
        /// </summary>
        /// <param name="sparseVectors"></param>
        /// <returns></returns>
        public static Dictionary<int, double> SparseVectorMean(List<Dictionary<int, double>> sparseVectors)
        {
            // Build a set, containing every word index
            var wordSet = sparseVectors.SelectMany(v => v.Keys);
            var mean = new Dictionary<int, double>();
            foreach (var wordIndex in wordSet)
            {
                double sum = 0;
                foreach (var vector in sparseVectors)
                {
                    if (vector.TryGetValue(wordIndex, out var value))
                    {
                        sum += value;
                    }
                }
                mean[wordIndex] = sum / sparseVectors.Count;
            }
            return mean;
        }
    }
}
