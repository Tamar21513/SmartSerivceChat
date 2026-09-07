public class RegisterRequest
{
    public string AccountType { get; set; } = "";
    public string Name { get; set; } = "";
    public string Email { get; set; } = "";
    public string Password { get; set; } = "";

    public string City { get; set; } = "";
    public int? Age { get; set; }
    public string Occupation { get; set; } = "";

    public int SubscriptionId { get; set; }
}