using Library.Model;
using Library.Service;


if (args.Length != 2)
{
    Console.WriteLine("Usage: politgraph <name one> <name two>");
    return;
}
var parliamentService = new ParliamentServiceClient();

foreach (var name in args)
{
    var affairs = parliamentService.GetMemberDataAsync(name).Result;
    if (affairs == null)
    {
        Console.WriteLine($"Member '{name}' not found.");
        return;
    }

    PrintAffairs(name, affairs);
}

static void PrintAffairs(string name, IEnumerable<Affair> affairs)
{
    Console.WriteLine($"---------- Affairs for {name} ----------");
    foreach (var affair in affairs)
    {
        Console.WriteLine(affair.ToString());
    }
    Console.WriteLine("----------\n");

}
