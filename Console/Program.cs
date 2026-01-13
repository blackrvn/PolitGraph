using Library.Service;


if (args.Length != 2)
{
    Console.WriteLine("Usage: Program <name 1> <name 2>");
    return;
}
var parliamentService = new ParliamentServiceClient();

string name1 = args[0];
string name2 = args[1];


Console.WriteLine(parliamentService.GetMemberDataAsync(name1).Result?.FirstOrDefault());
Console.WriteLine(parliamentService.GetMemberDataAsync(name2).Result?.FirstOrDefault());
