using politgraph.lib.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace politgraph.lib.Interfaces
{
    public interface IMembersData
    {
        Task<List<MemberModel>> GetMember();
    }
}