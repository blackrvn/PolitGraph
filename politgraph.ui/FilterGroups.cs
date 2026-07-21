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

        // Die Rohdaten verwenden uneinheitliche Partei-Bezeichnungen (Kürzel vs.
        // ausgeschriebener Name, alte/fusionierte Parteinamen). Diese werden hier
        // auf die kanonische Fraktions-Gruppe abgebildet, damit sie nicht
        // fälschlich in "Andere" landen. Vergleich erfolgt case-insensitiv.
        private static readonly IReadOnlyDictionary<string, string> PartyAliases =
            new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                // SP
                ["SP"] = "SP",
                ["SPS"] = "SP",
                ["PS"] = "SP",
                ["Sozialdemokratische Partei"] = "SP",
                ["Sozialdemokratische Partei der Schweiz"] = "SP",

                // SVP
                ["SVP"] = "SVP",
                ["UDC"] = "SVP",
                ["Schweizerische Volkspartei"] = "SVP",

                // FDP-Liberale
                ["FDP"] = "FDP-Liberale",
                ["FDP-Liberale"] = "FDP-Liberale",
                ["FDP.Die Liberalen"] = "FDP-Liberale",
                ["FDP. Die Liberalen"] = "FDP-Liberale",
                ["PLR"] = "FDP-Liberale",
                ["Die Liberalen"] = "FDP-Liberale",

                // M-E (Fraktion Mitte: Die Mitte, ehem. CVP/BDP)
                ["M-E"] = "M-E",
                ["Die Mitte"] = "M-E",
                ["Mitte"] = "M-E",
                ["CVP"] = "M-E",
                ["Christlichdemokratische Volkspartei"] = "M-E",
                ["BDP"] = "M-E",
                ["Bürgerlich-Demokratische Partei"] = "M-E",

                // glp
                ["glp"] = "glp",
                ["GLP"] = "glp",
                ["Grünliberale"] = "glp",
                ["Grünliberale Partei"] = "glp",

                // GRÜNE
                ["GRÜNE"] = "GRÜNE",
                ["Grüne"] = "GRÜNE",
                ["Grüne Partei der Schweiz"] = "GRÜNE",
                ["GPS"] = "GRÜNE",
                ["Les Verts"] = "GRÜNE",
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
            if (string.IsNullOrWhiteSpace(party))
                return _defaultGroup;

            var key = party.Trim();
            if (PartyGroups.Contains(key))
                return key;
            if (PartyAliases.TryGetValue(key, out var group))
                return group;
            return _defaultGroup;
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
