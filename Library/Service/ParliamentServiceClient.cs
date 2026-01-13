using System.Net.Http;
using System.Net.Http.Headers;

namespace PolitGraph.Service
{
    internal class ParliamentServiceClient
    {
        private readonly HttpClient _httpClient;
        public ParliamentServiceClient()
        {
            _httpClient = new();
            _httpClient.BaseAddress = new Uri("https://api.openparldata.ch/v1/");
            _httpClient.DefaultRequestHeaders.Accept.Clear();
            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        }
        public async Task<string> GetMemberDataAsync(string memberId)
        {
            var response = await _httpClient.GetAsync($"persons/{memberId}");
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }

        public async Task<string> GetMemberIdAsync(string memberName)
        {
            var response = await _httpClient.GetAsync($"persons/?search={memberName}&search_mode=exact");
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsStringAsync();
        }


    }
}
