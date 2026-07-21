using Microsoft.AspNetCore.Components;
using Microsoft.JSInterop;
using politgraph.lib.Interfaces;
using System.Diagnostics;

namespace politgraph.ui.Components.Layout
{
    public partial class MembersGraph : IAsyncDisposable
    {
        private readonly IJSRuntime _js;
        private readonly IMembersData _db;
        private readonly IFilterService _filterService;
        private readonly ISelectionService _selectionService;
        private DotNetObjectReference<MembersGraph>? _dotNetRef;

        private IJSObjectReference? Module { get; set; }
        private ElementReference GraphContainer { get; set; }

        private List<string>? Parties { get; set; }

        private EventCallback<string> SelectionChanged { get; set; }

        public MembersGraph(IJSRuntime js, IMembersData db, IFilterService filterService, ISelectionService selectionService)
        {
            _js = js;
            _db = db;
            _filterService = filterService;
            _selectionService = selectionService;
        }

        protected override async Task OnInitializedAsync()
        {
            Parties = await _db.GetPartiesAsync();
            _filterService.SetSelectedPartiesDefault(FilterGroups.GetPartyGroups());
            _filterService.SetSelectedStatesDefault(FilterGroups.GetStateGroups());
            _selectionService.OnSelectionChanged += HandleSelectionChanged;
        }

        private async void HandleSelectionChanged()
        {
            if (_selectionService.Selection == null && Module != null)
            {
                try
                {
                    await Module.InvokeVoidAsync("deselect");
                }
                catch (JSDisconnectedException) { }
            }
        }

        private bool IsPartyOn(string party) => _filterService.SelectedParties?.Contains(party) ?? true;
        private bool IsStateOn(string state) => _filterService.SelectedStates?.Contains(state) ?? true;

        private string PartyPillClass(string party) => IsPartyOn(party) ? "pill" : "pill pill--off";
        private string StatePillClass(string state) => IsStateOn(state) ? "pill" : "pill pill--off";

        private void ToggleParty(string party)
        {
            var set = _filterService.SelectedParties;
            if (set == null) return;
            if (!set.Remove(party)) set.Add(party);
        }

        private void ToggleState(string state)
        {
            var set = _filterService.SelectedStates;
            if (set == null) return;
            if (!set.Remove(state)) set.Add(state);
        }

        protected override async Task OnAfterRenderAsync(bool firstRender)
        {
            if (firstRender)
            {
                Module = await _js.InvokeAsync<IJSObjectReference>("import", "./Components/Layout/MembersGraph.razor.js");
                _dotNetRef = DotNetObjectReference.Create(this);

                var nodes = await _db.GetMembersAsync();
                var edges = await _db.GetEdgesAsync();
                var payload = CytoscapeMapper.ToJson(CytoscapeMapper.ToCytoscape(nodes, edges));

                await Module.InvokeVoidAsync("create", GraphContainer, payload, _dotNetRef);
                _filterService.AssignModule(Module);
            }
        }

        public async ValueTask DisposeAsync()
        {
            _selectionService.OnSelectionChanged -= HandleSelectionChanged;
            _dotNetRef?.Dispose();
            if (Module != null)
            {
                try
                {
                    await Module.InvokeVoidAsync("dispose");
                    await Module.DisposeAsync();
                }
                catch (JSDisconnectedException)
                {

                }
            }
            GC.SuppressFinalize(this);
        }

        [JSInvokable]
        public async Task OnMemberDeselected()
        {
            _selectionService?.SetSelection(null);
        }

        [JSInvokable]
        public async Task OnMemberSelected(NodeSelectedArgs args)
        {
            if (args.Id != null)
            {
                // Id wird von JSInterop als string übergeben
                if (int.TryParse(args.Id, out var id))
                {
                    var member = await _db.GetMemberAsync(id);
                    _selectionService.SetSelection(member);
                    Debug.WriteLine(member);
                }
            }
            else
            {
                _selectionService?.SetSelection(null);
            }
        }

    }
}
