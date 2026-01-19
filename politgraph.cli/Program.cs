using Library.Model;
using Library.Service;


if (args.Length != 2)
{
    Console.WriteLine("Usage: politgraph <name one> <name two>");
    return;
}
var parliamentService = new ParliamentServiceClient();
var members = new List<Member>();

foreach (var name in args)
{
    var member = parliamentService.GetMemberAsync(name).Result;
    if (member != null)
    {
        members.Add(member);
        var affairs = parliamentService.GetMemberDataAsync(member.Id).Result;
        if (affairs == null)
        {
            Console.WriteLine($"Member '{name}' not found.");
        }
        else
        {
            member.Affairs = affairs;
            //PrintAffairs(name, affairs);
        }
    }
}

var store = new VectorStore(members);
store.Transform();
var vectors1 = store.GetSparseVectors(members[0]);
var vectors2 = store.GetSparseVectors(members[1]);
var mean1 = VectorCalculationService.SparseVectorMean(vectors1);
var mean2 = VectorCalculationService.SparseVectorMean(vectors2);

Console.WriteLine(VectorCalculationService.CosineSimilarity(mean1, mean2));


static void PrintAffairs(string name, IList<Affair> affairs)
{
    Console.WriteLine($"---------- Affairs for {name} ----------");
    foreach (var affair in affairs)
    {
        Console.WriteLine(affair.ToString());
    }
    Console.WriteLine("----------\n");
}

