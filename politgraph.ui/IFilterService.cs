using Microsoft.JSInterop;
using System.Collections.ObjectModel;

namespace politgraph.ui
{
    public interface IFilterService
    {
        string SearchText { get; set; }
        ObservableCollection<string>? SelectedParties { get; }
        ObservableCollection<string>? SelectedStates { get; }

        void SetSelectedPartiesDefault(IEnumerable<string> selectedParties);
        void SetSelectedStatesDefault(IEnumerable<string> selectedStates);

        Task FilterChanged();
        void AssignModule(IJSObjectReference module);
    }
}