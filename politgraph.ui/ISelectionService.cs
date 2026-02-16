using politgraph.lib.Models;

namespace politgraph.ui
{
    public interface ISelectionService
    {
        MemberModel? Selection { get; }
        event Action? OnSelectionChanged;
        void SetSelection(MemberModel? member);
    }
}