namespace politgraph.ui
{
    public class NodeSelectedArgs
    {
        public string? Id { get; set; }
        public string? Label { get; set; }
    }

    public class CheckBoxStateChangedArgs
    {
        public bool IsChecked { get; set; }
        public string? Label { get; set; }
    }
}
