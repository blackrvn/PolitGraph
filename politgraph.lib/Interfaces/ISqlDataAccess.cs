using System.Collections.Generic;
using System.Threading.Tasks;

namespace politgraph.lib.Interfaces
{
    public interface ISqlDataAccess
    {
        string ConnectionStringName { get; set; }

        Task<List<T>> LoadDataAsync<T, U>(string sql, U parameters);
    }
}