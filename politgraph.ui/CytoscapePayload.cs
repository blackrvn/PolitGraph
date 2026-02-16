namespace politgraph.ui
{
    public sealed class CytoscapePayload
    {
        public CytoscapeElements Elements { get; init; } = new();
    }

    public sealed class CytoscapeElements
    {
        public List<CytoscapeNode> Nodes { get; init; } = new();
        public List<CytoscapeEdge> Edges { get; init; } = new();
    }

    public sealed class CytoscapeNode
    {
        public CytoscapeNodeData Data { get; init; } = default!;
    }

    public sealed class CytoscapeNodeData
    {
        public int Id { get; init; } = default!;
        public string Label { get; init; } = default!;
        public string Party { get; init; } = default!;
        public string State { get; init; } = default!;
    }

    public sealed class CytoscapeEdge
    {
        public CytoscapeEdgeData Data { get; init; } = default!;
    }

    public sealed class CytoscapeEdgeData
    {
        public int Id { get; init; } = default!;

        public int Source { get; init; } = default!;
        public int Target { get; init; } = default!;
        public double Weight { get; init; } = default!;
    }
}
