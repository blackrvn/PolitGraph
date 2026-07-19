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
            ["SP"] = "#e14b4b",
            ["SVP"] = "#1D5936",
            ["FDP-Liberale"] = "#3f6fd6",
            ["M-E"] = "#e0913f",
            ["glp"] = "#8f5285",
            ["GRÜNE"] = "#57a05a",
            ["Andere"] = "#aeb6c9"
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
