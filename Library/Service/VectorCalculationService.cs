namespace Library.Service
{
    public static class VectorCalculationService
    {
        public static double CosineSimilarity(Dictionary<int, double> sparseVectorA, Dictionary<int, double> sparseVectorB)
        {
            var dotProduct = DotProduct(sparseVectorA, sparseVectorB);
            var lengthA = VectorLength(sparseVectorA);
            var lengthB = VectorLength(sparseVectorB);
            return dotProduct / lengthA * lengthB;
        }

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

        private static double VectorLength(Dictionary<int, double> sparseVector)
        {
            double sum = 0;
            foreach (var kvp in sparseVector)
            {
                var value = kvp.Value;
                sum += value * value;
            }
            return Math.Sqrt(sum);
        }

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
