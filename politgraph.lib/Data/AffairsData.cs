using politgraph.lib.Interfaces;
using politgraph.lib.Models;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace politgraph.lib.Data
{
    public class AffairsData
    {
        private readonly ISqlDataAccess _db;

        public AffairsData(ISqlDataAccess db)
        {
            _db = db;
        }

        public Task<List<AffairModel>> GetAffairs()
        {
            throw new NotImplementedException();
        }
    }
}
