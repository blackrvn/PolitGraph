namespace politgraph.ui
{
    public static class FilterGroups
    {
        private static readonly string _defaultGroup = "Andere";

        private static HashSet<string> PartyGroups = new HashSet<string>()
        {
            "SP",
            "SVP",
            "FDP-Liberale",
            "M-E",
            "glp",
            "GRÜNE",
            _defaultGroup
        };

        private static HashSet<string> StateGroups = new HashSet<string>()
        {
            "Aktiv",
            "Inaktiv"
        };

        private static readonly IReadOnlyDictionary<string, string> Colors = new Dictionary<string, string>
        {
            ["SP"] = "#ff0000",
            ["SVP"] = "#007832",
            ["FDP-Liberale"] = "#0044d5",
            ["M-E"] = "#fb7203",
            ["glp"] = "#7e3874",
            ["GRÜNE"] = "#03f61a",
            ["Andere"] = "#999"
        };

        public static IEnumerable<string> GetPartyGroups()
        {
            return PartyGroups;
        }

        public static IEnumerable<string> GetStateGroups()
        {
            return StateGroups;
        }

        public static string GetPartyGroup(string party)
        {
            return PartyGroups.Contains(party) ? party : _defaultGroup;
        }

        public static string GetStateGroup(bool active)
        {
            return active ? "Aktiv" : "Inaktiv";
        }

        public static string GetColorForParty(string party)
        {
            var group = GetPartyGroup(party);
            return Colors[group];
        }
    }
}
