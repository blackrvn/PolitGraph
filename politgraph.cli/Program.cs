using Library.Model;
using Library.Service;


if (args.Length != 2)
{
    Console.WriteLine("Usage: Program <Last Name First Name> <Last Name First Name>");
    return;
}
var parliamentService = new ParliamentServiceClient();

string nameOne = args[0];
string nameTwo = args[1];

var affairsOne = parliamentService.GetMemberDataAsync(nameOne).Result;
var affairsTwo = parliamentService.GetMemberDataAsync(nameTwo).Result;

if (affairsOne == null)
{
    Console.WriteLine($"Member '{nameOne}' not found.");
    return;
}
if (affairsTwo == null)
{
    Console.WriteLine($"Member '{nameTwo}' not found.");
    return;
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

PrintAffairs(nameOne, affairsOne);
PrintAffairs(nameTwo, affairsTwo);