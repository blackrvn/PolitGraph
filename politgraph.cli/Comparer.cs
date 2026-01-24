using Library.Model;
using Library.Service;

namespace politgraph.cli
{
    internal class Comparer
    {
        private readonly StoreageService _storageService;
        private readonly ParliamentServiceClient _parliamentService;
        private readonly Updater _updater;
        private readonly bool _update;

        public Comparer(StoreageService storageService, ParliamentServiceClient parliamentService, Updater updater, bool update)
        {
            _storageService = storageService;
            _parliamentService = parliamentService;
            _updater = updater;
            _update = update;
            _storageService.LoadData();
        }

        /// <summary>
        /// Compares two members by their names and calculates the cosine similarity between their vectors.
        /// </summary>
        /// <param name="nameOne"></param>
        /// <param name="nameTwo"></param>
        /// <returns></returns>
        public bool Compare(string nameOne, string nameTwo)
        {

            if (!TryGetData(nameOne, out var memberOne))
            {
                return false;
            }
            if (!TryGetData(nameTwo, out var memberTwo))
            {
                return false;
            }

            _updater.UpdateVectors();

            // Neu laden, da die Instanzen in StorageService aktualisiert wurden
            if (_storageService.TryGetMember(memberOne.Id, out memberOne) &&
               _storageService.TryGetMember(memberTwo.Id, out memberTwo))
            {
                Console.WriteLine("Vectors updated successfully.");
                var sim = VectorCalculationService.CosineSimilarity(memberOne.Vector, memberTwo.Vector);
                Console.WriteLine($"Cosine-Similarity between '{memberOne.Name}' and '{memberTwo.Name}': {sim}");
                return true;
            }
            else
            {
                Console.WriteLine("Could not update vectors.");
                return false;
            }

        }

        /// <summary>
        /// Tries to get member data either from storage or by updating it from the parliament service.
        /// </summary>
        /// <param name="memberName"></param>
        /// <param name="member">
        /// The retrieved member. May be an legacy instance -> needs to be reloaded from storage after update.
        /// </param>
        /// <returns></returns>
        private bool TryGetData(string memberName, out Member member)
        {
            member = _parliamentService.GetMemberAsync(memberName).Result;
            if (member != null)
            {
                if (_storageService.TryGetMember(member.Id, out var storedMember))
                {
                    member = storedMember!;
                    return true;
                }
                else
                {
                    if (_update)
                    {
                        if (_updater.Update(member))
                        {
                            return true;
                        }
                        else
                        {
                            Console.WriteLine("Could not update data.");
                            return false;
                        }
                    }
                    else
                    {
                        Console.WriteLine($"Member '{memberName}' not found in storage.");
                        return false;
                    }

                }
            }
            else
            {
                Console.WriteLine($"Member '{memberName}' not found.");
                return false;
            }


        }
    }
}
