using Library.Model;
using Library.Service;
using politgraph.cli;

var parliamentService = new ParliamentServiceClient();

var appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
var dir = Path.Combine(appData, "politgraph");
var path = Path.Combine(dir, "members.json");

if (!Directory.Exists(dir))
{
    Directory.CreateDirectory(dir);
}

var names = args.Where(arg => !arg.StartsWith("-")).ToArray();
var options = args.Where(arg => arg.StartsWith("-")).ToArray();

var storageService = new StoreageService(path);
var updater = new Updater(storageService);

var update = options.Contains("--Update") || args.Contains("-u");


if (names.Length == 2)
{
    var comparer = new Comparer(storageService, parliamentService, updater, update);
    var nameOne = names[0];
    var nameTwo = names[1];
    if (!comparer.Compare(nameOne, nameTwo))
    {
        Console.WriteLine("Could not compare the given members. Make sure the names are correct.");
    }
}

else if (names.Length == 0 && update)
{

    if (updater.Update())
    {
        Console.WriteLine("Data updated successfully.");
    }
    else
    {
        Console.WriteLine("Could not update data.");
    }
}

else
{
    Console.WriteLine("Usage: politgraph <first name last name> <first name last name>");
    return;
}


static void PrintAffairs(string name, IList<Affair> affairs)
{
    Console.WriteLine($"---------- Affairs for {name} ----------");
    foreach (var affair in affairs)
    {
        Console.WriteLine(affair.ToString());
    }
    Console.WriteLine("----------\n");
}

