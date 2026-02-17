using politgraph.lib.Interfaces;
using politgraph.lib.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace politgraph.lib.Data
{
    public class AffairsData : IAffairsData
    {
        private readonly ISqlDataAccess _db;

        public AffairsData(ISqlDataAccess db)
        {
            _db = db;
        }

        public async Task<List<AffairModel>> GetAffairsOfMemberAsync(int id)
        {
            return await _db.LoadDataAsync<AffairModel, dynamic>("SELECT * FROM affair WHERE member_id = @Id", new { Id = id });
        }
    }
}
