using System.Text.Json.Serialization;

namespace Library.Model
{

    public record class TextDTO(
        int Id,
        [property: JsonPropertyName("text_de")] string Content,
        [property: JsonPropertyName("type_de")] string Type
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
    public record class DataContainer<Type>(
        [property: JsonPropertyName("data")] List<Type> Items,
        [property: JsonPropertyName("meta")] MetaData? Meta
        )
        ;

    /// <summary>
    /// Represents one affair
    /// </summary>
    /// <param name="Id"></param>
    /// <param name="Title"></param>
    /// <param name="Texts"></param>
    public record class AffairDTO(
        int Id,
        [property: JsonPropertyName("title_de")] string Title,
        [property: JsonPropertyName("texts")] DataContainer<TextDTO>? Texts
        );

    public record class MetaData(
        [property: JsonPropertyName("total_records")] int Total,
        [property: JsonPropertyName("has_more")] bool HasMore,
        [property: JsonPropertyName("next_page")] string NextPage
        );
}
