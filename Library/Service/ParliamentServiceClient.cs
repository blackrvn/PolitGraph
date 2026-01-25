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
        /// Gets all members from the parliament API. <br/>
        /// </summary>
        /// <returns>
        /// Returns a dictionary of all members with their IDs as keys or null if no members found. <br/>
        /// Return only members on national level (body_key=CHE).
        /// </returns>
        public async Task<Dictionary<int, Member>?> GetMembersAsync()
        {
            var members = new Dictionary<int, Member>();

            var membersIds = await _httpClient.GetFromJsonAsync<DataContainer<ObjectId>>($"persons/?body_key=CHE");
            foreach (var memberId in membersIds?.Items!)
            {
                var member = await GetMemberAsync(memberId.Id);
                if (member != null)
                {
                    await AssignMemberDataAsync(member);
                    members.Add(member.Id, member);
                }
            }
            return members;
        }

        /// <summary>
        /// Assigns the affairs of a member to the given member object.
        /// </summary>
        /// <param name="member"></param>
        public async Task AssignMemberDataAsync(Member member)
        {
            // TODO: Imlement paging to retrieve all affairs if more than 300
            var affairIDs = await _httpClient.GetFromJsonAsync<DataContainer<ObjectId>>($"persons/{member.Id}/affairs?limit=300");
            var affairs = new List<Affair>();
            foreach (var affair in affairIDs?.Items!)
            {
                var affairDetail = await _httpClient.GetFromJsonAsync<AffairDTO>($"affairs/{affair.Id}?expand=texts&lang=de&lang_format=flat");
                if (affairDetail != null)
                {
                    affairs.Add(new(affairDetail));
                }
            }
            member.Affairs = affairs;

        }



        /// <summary>
        /// Returns the member for a given member name.
        /// </summary>
        /// <remarks>
        /// Uses search_mode=exact to get an exact match.
        /// Uses body_key=CHE to only search on a national level.
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
            if (names.Length == 2)
            {
                var firstName = names[0];
                var lastName = names[1];
                var result = await _httpClient.GetFromJsonAsync<DataContainer<Member>>($"persons/?firstname={firstName}&lastname={lastName}&search_mode=exact&body_key=CHE");
                return result?.Items.FirstOrDefault() ?? null;
            }
            return null;

        }

        /// <summary>
        /// Return the member for a given member id.
        /// </summary>
        /// <remarks>
        /// Uses body_key=CHE to only search on a national level.
        /// </remarks>
        /// <param name="memberId"></param>
        /// <returns>
        /// Return the member or null if not found
        /// </returns>
        public async Task<Member?> GetMemberAsync(int memberId)
        {
            var result = await _httpClient.GetFromJsonAsync<DataContainer<Member>>($"persons/?{memberId}&body_key=CHE");
            return result?.Items.FirstOrDefault() ?? null;
        }


    }
}
