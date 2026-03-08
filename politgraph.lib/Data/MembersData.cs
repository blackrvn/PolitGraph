using politgraph.lib.Interfaces;
using politgraph.lib.Models;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace politgraph.lib.Data
{
    public class MembersData : IMembersData
    {
        private readonly ISqlDataAccess _db;

        public MembersData(ISqlDataAccess db)
        {
            _db = db;
        }

        public async Task<List<MemberModel>> GetMembersAsync()
        {
            return await _db.LoadDataAsync<MemberModel, dynamic>("SELECT * FROM member", new { });
        }

        public async Task<List<EdgeModel>> GetEdgesAsync()
        {
            return await _db.LoadDataAsync<EdgeModel, dynamic>("SELECT * FROM edge", new { });
        }

        public async Task<List<string>> GetPartiesAsync()
        {
            return await _db.LoadDataAsync<string, dynamic>("SELECT DISTINCT party FROM member", new { });
        }

        public async Task<MemberModel> GetMemberAsync(int id)
        {
            var members = await _db.LoadDataAsync<MemberModel, dynamic>("SELECT * FROM member WHERE member_id = @Id", new { Id = id });
            return members.FirstOrDefault();
        }
    }


}
