using Library.Model;
using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace Library.Service
{
    /// <summary>
    /// Service client for interacting with the Swiss Parliament Open Data API.
    /// </summary>
    /// <remarks>
    /// API Documentation: <see cref="Constants.API"/>
    /// </remarks>
    public class ParliamentServiceClient
    {
        private readonly HttpClient _httpClient;
        /// <summary>
        /// <inheritdoc cref="ParliamentServiceClient"/>
        /// </summary>
        public ParliamentServiceClient()
        {
            _httpClient = new();
            _httpClient.BaseAddress = new Uri(Constants.API);
            _httpClient.DefaultRequestHeaders.Accept.Clear();
            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        }

        /// <summary>
        /// Returns the affairs for a given member id.
        /// </summary>
        /// <remarks>
        /// Calls the <see cref="GetMemberAsync(string)"/> method to retrieve the member ID first,"/>
        /// </remarks>
        /// <param name="memberName"></param>
        /// <returns></returns>
        public async Task<List<Affair>?> GetMemberDataAsync(int memberId)
        {
            // TODO: Imlement paging to retrieve all affairs if more than 300
            var affairIDs = await _httpClient.GetFromJsonAsync<DataContainer<ObjectId>>($"persons/{memberId}/affairs?limit=300");
            var affairs = new List<Affair>();
            foreach (var affair in affairIDs?.Items ?? [])
            {
                var affairDetail = await _httpClient.GetFromJsonAsync<AffairDTO>($"affairs/{affair.Id}?expand=texts&lang=de&lang_format=flat");
                if (affairDetail != null)
                {
                    affairs.Add(new(affairDetail));
                }
            }
            return affairs;
        }

        /// <summary>
        /// Returns the member for a given member name.
        /// </summary>
        /// <remarks>
        /// Uses search_mode=exact to get an exact match.
        /// Uses active=true to only search for active members.
        /// </remarks>
        /// <param name="memberName">
        /// The name of the requested member
        /// </param>
        /// <returns>
        /// Return the first matching member or null if not found
        /// </returns>
        public async Task<Member?> GetMemberAsync(string memberName)
        {
            string[] names = memberName.Split(' ');
            if(names.Length == 2)
            {
                var firstName = names[0];
                var lastName = names[1];
                var result = await _httpClient.GetFromJsonAsync<DataContainer<Member>>($"persons/?firstname={firstName}&lastname={lastName}&search_mode=exact&body_key=CHE");
                return result?.Items.FirstOrDefault() ?? null;
            }
            return null;

        }


    }
}
