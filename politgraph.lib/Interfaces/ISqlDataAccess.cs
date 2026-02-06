using System.Collections.Generic;
using System.Threading.Tasks;

namespace politgraph.lib.Interfaces
{
    public interface ISqlDataAccess
    {
        string ConnectionStringName { get; set; }

        Task<List<T>> LoadData<T, U>(string sql, U parameters);
    }
}