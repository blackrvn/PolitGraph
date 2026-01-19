using System.Text.Json.Serialization;

namespace Library.Model
{

    public record class TextDTO(
        int Id,
        [property: JsonPropertyName("text")] Dictionary<string, string> Content,
        [property: JsonPropertyName("type")] Dictionary<string, string> Type
        );

    public record class ObjectId(int Id);
    /// <summary>
    /// Container Class to deserialize returned JSON.
    /// The <see cref="Constants.API"/> often returns object with the following structure:
    /// <code>
    /// "texts": {
    ///     "data": [
    ///         {
    ///             "id": 210865
    ///             ...
    ///         }
    ///     ]
    /// </code>
    /// </summary>
    /// <typeparam name="Type"></typeparam>
    /// <param name="Items"></param>
    public record class DataContainer<Type>([property: JsonPropertyName("data")] List<Type> Items);

    /// <summary>
    /// Represents one affair
    /// </summary>
    /// <param name="Id"></param>
    /// <param name="Titles"></param>
    /// <param name="Texts"></param>
    public record class AffairDTO(
        int Id,
        [property: JsonPropertyName("title")] Dictionary<string, string> Titles,
        [property: JsonPropertyName("texts")] DataContainer<TextDTO>? Texts
        );
}
