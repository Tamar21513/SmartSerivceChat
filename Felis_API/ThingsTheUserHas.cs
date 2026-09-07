public class ThingsTheUserHas
{
    public int ThingsTheUserHasId { get; set; }
    public int UserId { get; set; }
    public string ThingsTheUserHasTopic { get; set; } = "";

    public List<string> ThingsTheUserHasContent { get; set; } = new List<string>();
}