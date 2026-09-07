public class Company
{
    public int CompanyId { get; set; }
    public string CompanyName { get; set; } = "";
    public string PasswordHash { get; set; } = "";
    public bool IsActive { get; set; }
    public int SubscriptionId { get; set; }
    public DateTime SubscriptionStartDate { get; set; }
}