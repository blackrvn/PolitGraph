using Microsoft.JSInterop;
using System.Collections.ObjectModel;

namespace politgraph.ui
{
    public class FilterService : IFilterService
    {
        private IJSObjectReference? Module { get; set; }

        private string _searchText = string.Empty;

        public string SearchText
        {
            get => _searchText;
            set
            {
                if (value != _searchText)
                {
                    _searchText = value;
                    SearchTextChanged();
                }
            }
        }
        public ObservableCollection<string>? SelectedParties { get; private set; } = new();
        public ObservableCollection<string>? SelectedStates { get; private set; } = new();

        private bool IsHydrating { get; set; } = false;

        public async Task SearchTextChanged()
        {
            if (Module != null && !IsHydrating)
            {
                await Module.InvokeVoidAsync("search", SearchText);
            }
        }

        public async Task FilterChanged()
        {
            if (Module != null && !IsHydrating)
            {
                await Module.InvokeVoidAsync("filter", SelectedParties, SelectedStates);
            }
        }

        public FilterService()
        {
            SelectedParties.CollectionChanged += (sender, e) => FilterChanged();
            SelectedStates.CollectionChanged += (sender, e) => FilterChanged();
        }

        public void AssignModule(IJSObjectReference module)
        {
            Module = module;
        }

        public void SetSelectedPartiesDefault(IEnumerable<string> selectedParties)
        {
            IsHydrating = true;
            SelectedParties?.Clear();
            foreach (var party in selectedParties)
            {
                SelectedParties?.Add(party);
            }
            IsHydrating = false;
        }

        public void SetSelectedStatesDefault(IEnumerable<string> selectedStates)
        {
            IsHydrating = true;
            SelectedStates?.Clear();
            foreach (var state in selectedStates)
            {
                SelectedStates?.Add(state);
            }
            IsHydrating = false;
        }
    }
}
