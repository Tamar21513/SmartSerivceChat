
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;

[ApiController]
[Route("api/admin")]
public class AdminController : ControllerBase
{
    private readonly string connectionString;

    // Resolves and stores the database connection string from configuration.
    public AdminController(IConfiguration configuration)
    {
        connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("DefaultConnection connection string is missing.");
    }

    // Returns all users joined with their subscription details, for the admin dashboard.
    [HttpGet("users")]
    public IActionResult GetUsers()
    {
        try
        {
            List<object> users = new List<object>();

            string query = @"
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    u.city,
                    u.age,
                    u.occupation,
                    u.role,
                    u.subscription_id,
                    u.subscription_start_date,
                    s.subscription_name,
                    s.priority AS subscription_priority
                FROM Users u
                LEFT JOIN Subscriptions s
                    ON u.subscription_id = s.subscription_id
                ORDER BY u.user_id;
            ";

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlCommand command = new SqlCommand(query, connection);
            using SqlDataReader reader = command.ExecuteReader();

            while (reader.Read())
            {
                users.Add(new
                {
                    userId = Convert.ToInt32(reader["user_id"]),
                    username = reader["username"]?.ToString() ?? "",
                    email = reader["email"]?.ToString() ?? "",
                    city = reader["city"] == DBNull.Value ? "" : reader["city"]?.ToString() ?? "",
                    age = reader["age"] == DBNull.Value ? 0 : Convert.ToInt32(reader["age"]),
                    occupation = reader["occupation"] == DBNull.Value ? "" : reader["occupation"]?.ToString() ?? "",
                    role = reader["role"]?.ToString() ?? "",
                    subscriptionId = Convert.ToInt32(reader["subscription_id"]),
                    subscriptionName = reader["subscription_name"] == DBNull.Value ? "" : reader["subscription_name"]?.ToString() ?? "",
                    subscriptionPriority = reader["subscription_priority"] == DBNull.Value ? 0 : Convert.ToInt32(reader["subscription_priority"]),
                    subscriptionStartDate = reader["subscription_start_date"] == DBNull.Value ? "" : Convert.ToDateTime(reader["subscription_start_date"]).ToString("yyyy-MM-dd")
                });
            }

            return Ok(users);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not load users.", error = ex.Message });
        }
    }

    // Updates a user's profile fields and subscription, resetting the subscription start date if it changed.
    [HttpPut("users/{id}")]
    public IActionResult UpdateUser(int id, [FromBody] AdminUserRequest request)
    {
        try
        {
            if (request.SubscriptionId <= 0)
            {
                return BadRequest(new { message = "SubscriptionId is required." });
            }

            string query = @"
                UPDATE Users
                SET
                    username = @Username,
                    email = @Email,
                    city = @City,
                    age = @Age,
                    occupation = @Occupation,
                    role = @Role,
                    subscription_id = @SubscriptionId,
                    subscription_start_date = CASE
                        WHEN subscription_id <> @SubscriptionId
                        THEN GETDATE()
                        ELSE subscription_start_date
                    END
                WHERE user_id = @UserId;
            ";

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlCommand command = new SqlCommand(query, connection);
            command.Parameters.AddWithValue("@UserId", id);
            command.Parameters.AddWithValue("@Username", request.Username.Trim());
            command.Parameters.AddWithValue("@Email", request.Email.Trim());
            command.Parameters.AddWithValue("@City", string.IsNullOrWhiteSpace(request.City) ? DBNull.Value : request.City.Trim());
            command.Parameters.AddWithValue("@Age", request.Age <= 0 ? DBNull.Value : request.Age);
            command.Parameters.AddWithValue("@Occupation", string.IsNullOrWhiteSpace(request.Occupation) ? DBNull.Value : request.Occupation.Trim());
            command.Parameters.AddWithValue("@Role", string.IsNullOrWhiteSpace(request.Role) ? "user" : request.Role.Trim());
            command.Parameters.AddWithValue("@SubscriptionId", request.SubscriptionId);

            int rowsAffected = command.ExecuteNonQuery();

            if (rowsAffected == 0)
            {
                return NotFound(new { message = "User was not found." });
            }

            return Ok(new { message = "User updated successfully." });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not update user.", error = ex.Message });
        }
    }

    // Deletes a user and their related reports and ThingsTheUserHas data in one transaction.
    [HttpDelete("users/{id}")]
    public IActionResult DeleteUser(int id)
    {
        using SqlConnection connection = new SqlConnection(connectionString);
        connection.Open();
        using SqlTransaction transaction = connection.BeginTransaction();

        try
        {
            ExecuteNonQuery(connection, transaction, "DELETE FROM Reports WHERE user_id = @Id;", id);
            ExecuteNonQuery(connection, transaction, "DELETE FROM ThingsTheUserHas WHERE user_id = @Id;", id);
            int rowsAffected = ExecuteNonQuery(connection, transaction, "DELETE FROM Users WHERE user_id = @Id;", id);

            if (rowsAffected == 0)
            {
                transaction.Rollback();
                return NotFound(new { message = "User was not found." });
            }

            transaction.Commit();
            return Ok(new { message = "User deleted successfully." });
        }
        catch (Exception ex)
        {
            transaction.Rollback();
            return StatusCode(500, new { message = "Could not delete user.", error = ex.Message });
        }
    }

    // Returns all companies joined with their subscription details and computed end date.
    [HttpGet("companies")]
    public IActionResult GetCompanies()
    {
        try
        {
            List<object> companies = new List<object>();

            string query = @"
                SELECT
                    c.company_id,
                    c.company_name,
                    c.is_active,
                    c.subscription_id,
                    c.subscription_start_date,
                    s.subscription_name,
                    s.priority AS subscription_priority,
                    s.duration_days,
                    DATEADD(DAY, s.duration_days, c.subscription_start_date) AS subscription_end_date
                FROM Company c
                LEFT JOIN Subscriptions s
                    ON c.subscription_id = s.subscription_id
                ORDER BY c.company_id;
            ";

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlCommand command = new SqlCommand(query, connection);
            using SqlDataReader reader = command.ExecuteReader();

            while (reader.Read())
            {
                companies.Add(new
                {
                    companyId = Convert.ToInt32(reader["company_id"]),
                    companyName = reader["company_name"]?.ToString() ?? "",
                    isActive = Convert.ToBoolean(reader["is_active"]),
                    subscriptionId = Convert.ToInt32(reader["subscription_id"]),
                    subscriptionName = reader["subscription_name"] == DBNull.Value ? "" : reader["subscription_name"]?.ToString() ?? "",
                    subscriptionPriority = reader["subscription_priority"] == DBNull.Value ? 0 : Convert.ToInt32(reader["subscription_priority"]),
                    durationDays = reader["duration_days"] == DBNull.Value ? 0 : Convert.ToInt32(reader["duration_days"]),
                    subscriptionStartDate = reader["subscription_start_date"] == DBNull.Value ? "" : Convert.ToDateTime(reader["subscription_start_date"]).ToString("yyyy-MM-dd"),
                    subscriptionEndDate = reader["subscription_end_date"] == DBNull.Value ? "" : Convert.ToDateTime(reader["subscription_end_date"]).ToString("yyyy-MM-dd")
                });
            }

            return Ok(companies);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not load companies.", error = ex.Message });
        }
    }

    // Updates a company's name, active status and subscription, then refreshes its category priorities.
    [HttpPut("companies/{id}")]
    public IActionResult UpdateCompany(int id, [FromBody] AdminCompanyRequest request)
    {
        try
        {
            if (request.SubscriptionId <= 0)
            {
                return BadRequest(new { message = "SubscriptionId is required." });
            }

            string query = @"
                UPDATE Company
                SET
                    company_name = @CompanyName,
                    is_active = @IsActive,
                    subscription_id = @SubscriptionId,
                    subscription_start_date = CASE
                        WHEN subscription_id <> @SubscriptionId
                        THEN GETDATE()
                        ELSE subscription_start_date
                    END
                WHERE company_id = @CompanyId;
            ";

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlCommand command = new SqlCommand(query, connection);
            command.Parameters.AddWithValue("@CompanyId", id);
            command.Parameters.AddWithValue("@CompanyName", request.CompanyName.Trim());
            command.Parameters.AddWithValue("@IsActive", request.IsActive);
            command.Parameters.AddWithValue("@SubscriptionId", request.SubscriptionId);

            int rowsAffected = command.ExecuteNonQuery();

            if (rowsAffected == 0)
            {
                return NotFound(new { message = "Company was not found." });
            }

            UpdateCompanyCategoryPriorities(connection, id);

            return Ok(new { message = "Company updated successfully." });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not update company.", error = ex.Message });
        }
    }

    // Deletes a company and its related category and data rows in one transaction.
    [HttpDelete("companies/{id}")]
    public IActionResult DeleteCompany(int id)
    {
        using SqlConnection connection = new SqlConnection(connectionString);
        connection.Open();
        using SqlTransaction transaction = connection.BeginTransaction();

        try
        {
            ExecuteNonQuery(connection, transaction, "DELETE FROM CompanyCategories WHERE company_id = @Id;", id);
            ExecuteNonQuery(connection, transaction, "DELETE FROM CompanyData WHERE company_id = @Id;", id);
            int rowsAffected = ExecuteNonQuery(connection, transaction, "DELETE FROM Company WHERE company_id = @Id;", id);

            if (rowsAffected == 0)
            {
                transaction.Rollback();
                return NotFound(new { message = "Company was not found." });
            }

            transaction.Commit();
            return Ok(new { message = "Company deleted successfully." });
        }
        catch (Exception ex)
        {
            transaction.Rollback();
            return StatusCode(500, new { message = "Could not delete company.", error = ex.Message });
        }
    }

    // Returns all subscriptions ordered by type and priority, for the admin dashboard.
    [HttpGet("subscriptions")]
    public IActionResult GetSubscriptions()
    {
        try
        {
            List<object> subscriptions = new List<object>();

            string query = @"
                SELECT
                    subscription_id,
                    subscription_name,
                    duration_days,
                    priority,
                    price,
                    description,
                    subscription_type,
                    is_active
                FROM Subscriptions
                ORDER BY subscription_type, priority;
            ";

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlCommand command = new SqlCommand(query, connection);
            using SqlDataReader reader = command.ExecuteReader();

            while (reader.Read())
            {
                subscriptions.Add(new
                {
                    subscriptionId = Convert.ToInt32(reader["subscription_id"]),
                    subscriptionName = reader["subscription_name"]?.ToString() ?? "",
                    durationDays = Convert.ToInt32(reader["duration_days"]),
                    priority = Convert.ToInt32(reader["priority"]),
                    price = Convert.ToInt32(reader["price"]),
                    description = reader["description"] == DBNull.Value ? "" : reader["description"]?.ToString() ?? "",
                    subscriptionType = reader["subscription_type"]?.ToString() ?? "",
                    isActive = Convert.ToBoolean(reader["is_active"])
                });
            }

            return Ok(subscriptions);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not load subscriptions.", error = ex.Message });
        }
    }

    // Validates and inserts a new subscription plan.
    [HttpPost("subscriptions")]
    public IActionResult AddSubscription([FromBody] AdminSubscriptionRequest request)
    {
        try
        {
            string? validationError = ValidateSubscriptionRequest(request);
            if (validationError != null)
            {
                return BadRequest(new { message = validationError });
            }

            string query = @"
                INSERT INTO Subscriptions
                    (subscription_name, duration_days, priority, price, description, subscription_type, is_active)
                OUTPUT INSERTED.subscription_id
                VALUES
                    (@SubscriptionName, @DurationDays, @Priority, @Price, @Description, @SubscriptionType, @IsActive);
            ";

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlCommand command = new SqlCommand(query, connection);
            AddSubscriptionParameters(command, request);

            int newSubscriptionId = Convert.ToInt32(command.ExecuteScalar());

            return Ok(new
            {
                message = "Subscription added successfully.",
                subscriptionId = newSubscriptionId
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not add subscription.", error = ex.Message });
        }
    }

    // Validates and updates a subscription plan, then refreshes all companies' category priorities.
    [HttpPut("subscriptions/{id}")]
    public IActionResult UpdateSubscription(int id, [FromBody] AdminSubscriptionRequest request)
    {
        try
        {
            string? validationError = ValidateSubscriptionRequest(request);
            if (validationError != null)
            {
                return BadRequest(new { message = validationError });
            }

            string query = @"
                UPDATE Subscriptions
                SET
                    subscription_name = @SubscriptionName,
                    duration_days = @DurationDays,
                    priority = @Priority,
                    price = @Price,
                    description = @Description,
                    subscription_type = @SubscriptionType,
                    is_active = @IsActive
                WHERE subscription_id = @SubscriptionId;
            ";

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlCommand command = new SqlCommand(query, connection);
            command.Parameters.AddWithValue("@SubscriptionId", id);
            AddSubscriptionParameters(command, request);

            int rowsAffected = command.ExecuteNonQuery();

            if (rowsAffected == 0)
            {
                return NotFound(new { message = "Subscription was not found." });
            }

            UpdateAllCompanyCategoryPriorities(connection);

            return Ok(new { message = "Subscription updated successfully." });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not update subscription.", error = ex.Message });
        }
    }

    // Deletes a subscription plan, refusing if any user or company is currently using it.
    [HttpDelete("subscriptions/{id}")]
    public IActionResult DeleteSubscription(int id)
    {
        try
        {
            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            string checkQuery = @"
                SELECT
                    (SELECT COUNT(*) FROM Users WHERE subscription_id = @Id) +
                    (SELECT COUNT(*) FROM Company WHERE subscription_id = @Id)
                AS UsageCount;
            ";

            using (SqlCommand checkCommand = new SqlCommand(checkQuery, connection))
            {
                checkCommand.Parameters.AddWithValue("@Id", id);

                int usageCount = Convert.ToInt32(checkCommand.ExecuteScalar());

                if (usageCount > 0)
                {
                    return BadRequest(new
                    {
                        message = "Cannot delete this subscription because users or companies are using it. Deactivate it instead."
                    });
                }
            }

            string deleteQuery = @"
                DELETE FROM Subscriptions
                WHERE subscription_id = @Id;
            ";

            using SqlCommand deleteCommand = new SqlCommand(deleteQuery, connection);
            deleteCommand.Parameters.AddWithValue("@Id", id);

            int rowsAffected = deleteCommand.ExecuteNonQuery();

            if (rowsAffected == 0)
            {
                return NotFound(new { message = "Subscription was not found." });
            }

            return Ok(new { message = "Subscription deleted successfully." });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Could not delete subscription.", error = ex.Message });
        }
    }

    // Runs a parameterized delete/update query with a single @Id parameter within a transaction.
    private static int ExecuteNonQuery(SqlConnection connection, SqlTransaction transaction, string query, int id)
    {
        using SqlCommand command = new SqlCommand(query, connection, transaction);
        command.Parameters.AddWithValue("@Id", id);
        return command.ExecuteNonQuery();
    }

    // Validates the fields of a subscription request, returning an error message or null if valid.
    private static string? ValidateSubscriptionRequest(AdminSubscriptionRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.SubscriptionName))
        {
            return "Subscription name is required.";
        }

        if (request.DurationDays <= 0)
        {
            return "Duration days must be greater than 0.";
        }

        if (request.Priority <= 0)
        {
            return "Priority must be greater than 0.";
        }

        if (request.Price < 0)
        {
            return "Price must be 0 or greater.";
        }

        if (request.SubscriptionType != "Customer" && request.SubscriptionType != "Company")
        {
            return "Subscription type must be Customer or Company.";
        }

        return null;
    }

    // Adds the common subscription field parameters to a SqlCommand.
    private static void AddSubscriptionParameters(SqlCommand command, AdminSubscriptionRequest request)
    {
        command.Parameters.AddWithValue("@SubscriptionName", request.SubscriptionName.Trim());
        command.Parameters.AddWithValue("@DurationDays", request.DurationDays);
        command.Parameters.AddWithValue("@Priority", request.Priority);
        command.Parameters.AddWithValue("@Price", request.Price);
        command.Parameters.AddWithValue("@Description", request.Description ?? "");
        command.Parameters.AddWithValue("@SubscriptionType", request.SubscriptionType);
        command.Parameters.AddWithValue("@IsActive", request.IsActive);
    }

    // Syncs a company's category priorities to match its current subscription's priority.
    private static void UpdateCompanyCategoryPriorities(SqlConnection connection, int companyId)
    {
        string query = @"
            UPDATE cc
            SET cc.priority = s.priority
            FROM CompanyCategories cc
            JOIN Company c
                ON cc.company_id = c.company_id
            JOIN Subscriptions s
                ON c.subscription_id = s.subscription_id
            WHERE cc.company_id = @CompanyId;
        ";

        using SqlCommand command = new SqlCommand(query, connection);
        command.Parameters.AddWithValue("@CompanyId", companyId);
        command.ExecuteNonQuery();
    }

    // Syncs every company's category priorities to match their subscriptions' priority.
    private static void UpdateAllCompanyCategoryPriorities(SqlConnection connection)
    {
        string query = @"
            UPDATE cc
            SET cc.priority = s.priority
            FROM CompanyCategories cc
            JOIN Company c
                ON cc.company_id = c.company_id
            JOIN Subscriptions s
                ON c.subscription_id = s.subscription_id;
        ";

        using SqlCommand command = new SqlCommand(query, connection);
        command.ExecuteNonQuery();
    }
}

public class AdminUserRequest
{
    public string Username { get; set; } = "";
    public string Email { get; set; } = "";
    public string City { get; set; } = "";
    public int Age { get; set; }
    public string Occupation { get; set; } = "";
    public string Role { get; set; } = "";
    public int SubscriptionId { get; set; }
}

public class AdminCompanyRequest
{
    public string CompanyName { get; set; } = "";
    public bool IsActive { get; set; }
    public int SubscriptionId { get; set; }
}

public class AdminSubscriptionRequest
{
    public string SubscriptionName { get; set; } = "";
    public int DurationDays { get; set; }
    public int Priority { get; set; }
    public int Price { get; set; }
    public string Description { get; set; } = "";
    public string SubscriptionType { get; set; } = "";
    public bool IsActive { get; set; } = true;
}

