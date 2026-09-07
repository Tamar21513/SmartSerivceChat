public class Subscription
{
    public int SubscriptionId { get; set; }
    public string Name { get; set; } = "";
    public int DurationDays { get; set; }
    public int Priority { get; set; }
    public int Price { get; set; }
    public string Description { get; set; } = "";
    public string SubscriptionType { get; set; } = "";
    public bool IsActive { get; set; }
}