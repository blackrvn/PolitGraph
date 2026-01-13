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
            var result = await _httpClient.GetFromJsonAsync<Result<Affair>>($"persons/{memberId}/affairs");
            return result?.Data;
        }

        public async Task<Member?> GetMemberIdAsync(string memberName)
        {
            var result = await _httpClient.GetFromJsonAsync<Result<Member>>($"persons/?search={memberName}&search_mode=exact");
            // Return the first matching member or null if not found
            return result?.Data.FirstOrDefault();
        }


    }
}
