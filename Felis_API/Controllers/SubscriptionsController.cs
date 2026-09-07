using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class SubscriptionsController : ControllerBase
{
    private readonly string connectionString =
        @"Server=TAMAR-MORIEL\SQLEXPRESS;Database=SmartServiceChatDB;Trusted_Connection=True;TrustServerCertificate=True;";

    // Returns all active subscriptions for the given type (Company or Customer).
    [HttpGet]
    public IActionResult GetSubscriptions([FromQuery] string type)
    {
        try
        {
            SubscriptionRepository repository = new SubscriptionRepository(connectionString);
            List<Subscription> subscriptions = repository.GetAllSubscriptions(type);
            return Ok(subscriptions);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Server error", error = ex.Message });
        }
    }
}