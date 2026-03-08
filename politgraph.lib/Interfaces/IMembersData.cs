using politgraph.lib.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace politgraph.lib.Interfaces
{
    public interface IMembersData
    {
        Task<List<MemberModel>> GetMembersAsync();
        Task<List<string>> GetPartiesAsync();
        Task<List<EdgeModel>> GetEdgesAsync();
        Task<MemberModel> GetMemberAsync(int id);
    }
}