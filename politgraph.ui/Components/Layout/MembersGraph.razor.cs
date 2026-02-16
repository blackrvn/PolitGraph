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

        private EventCallback<string> SelectionChanged { get; set; }

        public MembersGraph(IJSRuntime js, IMembersData db, IFilterService filterService, ISelectionService selectionService)
        {
            _js = js;
            _db = db;
            _filterService = filterService;
            _selectionService = selectionService;
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
        public async Task OnMemberSelected(NodeSelectedArgs args)
        {
            // Id wird von JSInterop als string übergeben
            try
            {
                if (int.TryParse(args.Id, out var id))
                {
                    var member = await _db.GetMemberAsync(id);
                    _selectionService.SetSelection(member);
                    Debug.WriteLine(member);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine($"Inner: {ex.InnerException?.Message}");
                Console.WriteLine($"Stack: {ex.StackTrace}");
                Console.WriteLine($"Full: {ex}");
            }
        }

    }
}
