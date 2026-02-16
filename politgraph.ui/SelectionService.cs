using politgraph.lib.Models;

namespace politgraph.ui
{
    public class SelectionService : ISelectionService
    {
        private MemberModel? _selection;
        public MemberModel? Selection => _selection;
        public event Action? OnSelectionChanged;

        public void SetSelection(MemberModel? member)
        {
            _selection = member;
            OnSelectionChanged?.Invoke();
        }
    }
}
