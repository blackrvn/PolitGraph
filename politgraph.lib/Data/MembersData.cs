using politgraph.lib.Interfaces;
using politgraph.lib.Models;
using System.Collections.Generic;
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

        public Task<List<MemberModel>> GetMember()
        {
            string query = "SELECT * FROM member";
            return _db.LoadData<MemberModel, dynamic>(query, new { });
        }
    }


}
