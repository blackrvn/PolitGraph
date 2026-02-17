using politgraph.lib.Data;
using politgraph.lib.DataAccess;
using politgraph.lib.Interfaces;
using politgraph.ui;
using politgraph.ui.Components;
using politgraph.ui.Components.Layout;


// Ermöglicht das abgeleichen von DB-Columns zu .net Models.
// DB: first_name | Model: FirstName
Dapper.DefaultTypeMap.MatchNamesWithUnderscores = true;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

builder.Services.AddSingleton<ISqlDataAccess, SqlDataAccess>();
builder.Services.AddSingleton<IFilterService, FilterService>();
builder.Services.AddSingleton<ISelectionService, SelectionService>();
builder.Services.AddTransient<IMembersData, MembersData>();
builder.Services.AddTransient<IAffairsData, AffairsData>();
builder.Services.AddTransient<AffairsData>();
builder.Services.AddTransient<MembersGraph>();


var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();


app.UseAntiforgery();

app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
