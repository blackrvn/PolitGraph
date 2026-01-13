using Library.Model;
using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace Library.Service
{

    public class ParliamentServiceClient
    {
        private readonly HttpClient _httpClient;
        public ParliamentServiceClient()
        {
            _httpClient = new();
            _httpClient.BaseAddress = new Uri("https://api.openparldata.ch/v1/");
            _httpClient.DefaultRequestHeaders.Accept.Clear();
            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        }
        public async Task<List<Affair>?> GetMemberDataAsync(string memberName)
        {
            var memberId = (await GetMemberIdAsync(memberName))?.Id;
            if (memberId == null)
            {
                return null;
            }
            var affairOverview = await _httpClient.GetFromJsonAsync<DataContainer<ObjectId>>($"persons/{memberId}/affairs?limit=300");
            var affairs = new List<Affair>();
            foreach (var affair in affairOverview?.Items ?? [])
            {
                var affairDetail = await _httpClient.GetFromJsonAsync<Affair>($"affairs/{affair.Id}?expand=texts");
                if (affairDetail != null)
                {
                    affairs.Add(affairDetail);
                }
            }
            return affairs;
        }

        public async Task<Member?> GetMemberIdAsync(string memberName)
        {
            var result = await _httpClient.GetFromJsonAsync<DataContainer<Member>>($"persons/?search={memberName}&search_mode=exact&active=true");
            // Return the first matching member or null if not found
            return result?.Items.FirstOrDefault();
        }


    }
}
