using System.Text.Json.Serialization;

namespace Library.Model
{
    public record class Member(
        int Id,
        [property: JsonPropertyName("fullname")] string Name
        );
    public record class Result<Type>(List<Type> Data);
    public record class Affair(
        int Id
        );
}
