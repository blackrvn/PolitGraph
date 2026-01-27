using Library.Model;
using ShellProgressBar;
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
            _httpClient.Timeout = TimeSpan.FromSeconds(10);
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
            var semaphore = new SemaphoreSlim(10);
            var members = new Dictionary<int, Member>();

            var ids = await GetPaginatedResultAsync($"persons/?body_key=CHE&active=true");

            var pgBarOptions = new ProgressBarOptions
            {
                ProgressCharacter = '─',
                ProgressBarOnBottom = true
            };

            int done = 0;
            int max = ids.Count;
            var msg = $"[{done} / {max}] Processing members...";
            using var pbar = new ProgressBar(max, msg, pgBarOptions);

            var tasks = ids.Select(async id =>
            {
                int count;
                // Warten darauf, dass diese Task an der Reihe ist
                await semaphore.WaitAsync();
                try
                {
                    var member = await GetMemberAsync(id);
                    if (member != null)
                    {
                        return await TryAssignMemberDataAsync(member) ? member : null;
                    }
                    return null;
                }
                catch (Exception e)
                {
                    Console.WriteLine($"[{id}] failed: {e.Message}");
                    return null;
                }
                finally
                {
                    // Freigeben
                    count = semaphore.Release();
                    var current = Interlocked.Increment(ref done);
                    pbar.Tick($"[{current} / {max}] Processing members...");
                }
            });

            var results = await Task.WhenAll(tasks);

            Console.WriteLine($"Member with affairs: {results.Count(m => m != null)}");
            Console.WriteLine($"Member without affairs: {results.Count(m => m == null)}");

            foreach (var member in results.Where(x => x != null))
            {
                members[member!.Id] = member;
            }

            return members;
        }

        /// <summary>
        /// Assigns the affairs of a member to the given member object.
        /// </summary>
        /// <param name="member"></param>
        public async Task<bool> TryAssignMemberDataAsync(Member member)
        {
            var success = false;
            try
            {
                // Gibt Fehler 500, wenn die Person keine Geschäfte hat
                var ids = await GetPaginatedResultAsync($"persons/{member.Id}/affairs?limit=300");
                var affairs = new List<Affair>();

                var pgBarOptions = new ProgressBarOptions
                {
                    ProgressCharacter = '─',
                    ProgressBarOnBottom = true
                };

                int done = 0;
                int max = ids.Count;
                var msg = $"[{done} / {max}] Processing members...";

                //using var pbar = new ProgressBar(max, msg, pgBarOptions);

                foreach (var affairId in ids)
                {
                    try
                    {
                        var affairResponse = await _httpClient.GetAsync($"affairs/{affairId}?expand=texts&lang=de&lang_format=flat");
                        if (!affairResponse.IsSuccessStatusCode)
                        {
                            Console.WriteLine($"[{member.Id}][{affairId}] Could not assign data: {(int)affairResponse.StatusCode}");
                        }
                        else
                        {
                            var affairDto = await affairResponse.Content.ReadFromJsonAsync<AffairDTO>();
                            if (affairDto != null)
                            {
                                var affair = new Affair(affairDto);
                                if (affair.TextRaw != null)
                                {
                                    // Nur Geschäfte, die einen deutschen Text beinhalten hinzufügen.
                                    affairs.Add(affair);
                                }
                            }

                        }
                    }
                    catch (HttpRequestException e)
                    {
                        Console.WriteLine($"[{member.Id}][{affairId}] Could not assign data");
                        Console.WriteLine(e.InnerException);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex);
                    }
                    finally
                    {
                        var current = Interlocked.Increment(ref done);
                        //pbar.Tick($"[{current} / {max}] Processing members...");
                    }
                }

                member.Affairs = affairs;
                success = member.Affairs.Any();
                return success;
            }
            catch (HttpRequestException e)
            {
                Console.WriteLine($"[{member.Id}] Could not assign data");
                Console.WriteLine(e.InnerException);
                return success;
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                return success;
            }

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
        /// <param name="memberId"></param>
        /// <returns>
        /// Return the member or null if not found
        /// </returns>
        public async Task<Member?> GetMemberAsync(int memberId)
        {
            var result = await _httpClient.GetFromJsonAsync<Member>($"persons/{memberId}");
            return result ?? null;
        }

        private async Task<HashSet<int>> GetPaginatedResultAsync(string entryNode)
        {
            var resp = await _httpClient.GetAsync(entryNode);
            var ids = new HashSet<int>();

            if (!resp.IsSuccessStatusCode)
            {
                Console.WriteLine($"[{entryNode}] Failed: {(int)resp.StatusCode}");
            }
            else
            {
                var container = await resp.Content.ReadFromJsonAsync<DataContainer<ObjectId>>();
                var metaData = container?.Meta;

                while (true)
                {
                    foreach (var id in container?.Items.Select(x => x.Id)!)
                    {
                        ids.Add(id);
                    }
                    if (metaData?.NextPage != null)
                    {
                        resp = await _httpClient.GetAsync(metaData.NextPage);
                        if (resp.IsSuccessStatusCode)
                        {
                            container = await resp.Content.ReadFromJsonAsync<DataContainer<ObjectId>>();
                            metaData = container?.Meta;
                        }
                        else
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

            }
            return ids;


        }

    }
}
