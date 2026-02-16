namespace politgraph.lib.Models
{
    public class EdgeModel
    {
        public int EdgeId { get; set; }
        public int SourceMemberId { get; set; }
        public int TargetMemberId { get; set; }
        public double Weight { get; set; }

    }
}
