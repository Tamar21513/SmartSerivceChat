public class Report
{
    public int ReportId { get; set; }
    public int UserId { get; set; }
    public DateTime CreatedAt { get; set; }
    public string ReportContent { get; set; } = "";
}