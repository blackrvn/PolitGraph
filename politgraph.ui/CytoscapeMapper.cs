using politgraph.lib.Models;
using System.Text.Json;

namespace politgraph.ui
{
    public static class CytoscapeMapper
    {


        public static CytoscapePayload ToCytoscape(
            IEnumerable<MemberModel> nodes,
            IEnumerable<EdgeModel> edges)
        {
            var payload = new CytoscapePayload();
            foreach (var member in nodes)
            {
                var node = new CytoscapeNode
                {
                    Data = new CytoscapeNodeData
                    {
                        Id = member.MemberId,
                        Label = $"{member.FirstName} {member.LastName}",
                        Party = member.Party!,
                        PartyGroup = FilterGroups.PartyGroups.TryGetValue(member.Party!, out var partyGroup) ? partyGroup : "Andere",
                        State = member.Active ? "Aktiv" : "Inaktiv"
                    }
                };
                payload.Elements.Nodes.Add(node);
            }
            foreach (var edge in edges)
            {
                var e = new CytoscapeEdge
                {
                    Data = new CytoscapeEdgeData
                    {
                        Id = edge.EdgeId,
                        Source = edge.SourceMemberId,
                        Target = edge.TargetMemberId,
                        Weight = edge.Weight
                    }
                };
                payload.Elements.Edges.Add(e);
            }
            return payload;
        }

        public static string ToJson(CytoscapePayload payload)
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
                WriteIndented = true,
            };
            return JsonSerializer.Serialize(payload, options);
        }
    }
}
