
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;

[ApiController]
[Route("api/categories")]
public class CategoriesController : ControllerBase
{
    private readonly string connectionString;

    // Resolves and stores the database connection string from configuration.
    public CategoriesController(IConfiguration configuration)
    {
        connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("DefaultConnection connection string is missing.");
    }

    // Returns all categories, ordered alphabetically.
    [HttpGet]
    public IActionResult GetCategories()
    {
        try
        {
            List<object> categories = new List<object>();

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            string query = @"
                SELECT 
                    category_id,
                    category_name
                FROM [Category]
                ORDER BY category_name ASC";

            using SqlCommand command = new SqlCommand(query, connection);
            using SqlDataReader reader = command.ExecuteReader();

            while (reader.Read())
            {
                categories.Add(new
                {
                    categoryId = Convert.ToInt32(reader["category_id"]),
                    categoryName = reader["category_name"].ToString()
                });
            }

            return Ok(categories);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                message = "Could not load categories.",
                error = ex.Message
            });
        }
    }

    // Creates a category if it doesn't already exist, or returns the existing one.
    [HttpPost]
    public IActionResult AddCategory([FromBody] CategoryRequest request)
    {
        if (request == null || string.IsNullOrWhiteSpace(request.CategoryName))
        {
            return BadRequest(new { message = "Category name is required." });
        }

        try
        {
            string categoryName = request.CategoryName.Trim();

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            int categoryId = GetOrCreateCategory(connection, null, categoryName);

            return Ok(new
            {
                categoryId,
                categoryName,
                message = "Category added successfully."
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                message = "Could not add category.",
                error = ex.Message
            });
        }
    }

    // Returns the categories assigned to a company, ordered by priority then name.
    [HttpGet("company/{companyId}")]
    public IActionResult GetCompanyCategories(int companyId)
    {
        try
        {
            List<object> categories = new List<object>();

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            string query = @"
                SELECT
                    cc.company_category_id,
                    cc.company_id,
                    cc.category_id,
                    ca.category_name,
                    cc.priority
                FROM CompanyCategories cc
                JOIN [Category] ca
                    ON cc.category_id = ca.category_id
                WHERE cc.company_id = @CompanyId
                ORDER BY cc.priority ASC, ca.category_name ASC";

            using SqlCommand command = new SqlCommand(query, connection);
            command.Parameters.AddWithValue("@CompanyId", companyId);

            using SqlDataReader reader = command.ExecuteReader();

            while (reader.Read())
            {
                categories.Add(new
                {
                    companyCategoryId = Convert.ToInt32(reader["company_category_id"]),
                    companyId = Convert.ToInt32(reader["company_id"]),
                    categoryId = Convert.ToInt32(reader["category_id"]),
                    categoryName = reader["category_name"].ToString(),
                    priority = Convert.ToInt32(reader["priority"])
                });
            }

            return Ok(categories);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                message = "Could not load company categories.",
                error = ex.Message
            });
        }
    }

    // Replaces a company's category assignments with the given list, using the company's subscription priority.
    [HttpPost("company/{companyId}")]
    public IActionResult SaveCompanyCategories(int companyId, [FromBody] SaveCompanyCategoriesRequest request)
    {
        if (request == null || request.CategoryIds == null)
        {
            return BadRequest(new { message = "Category ids are required." });
        }

        try
        {
            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlTransaction transaction = connection.BeginTransaction();

            try
            {
                int companyPriority = GetCompanySubscriptionPriority(connection, transaction, companyId);

                string deleteQuery = @"
                    DELETE FROM CompanyCategories
                    WHERE company_id = @CompanyId";

                using (SqlCommand deleteCommand = new SqlCommand(deleteQuery, connection, transaction))
                {
                    deleteCommand.Parameters.AddWithValue("@CompanyId", companyId);
                    deleteCommand.ExecuteNonQuery();
                }

                foreach (int categoryId in request.CategoryIds.Distinct())
                {
                    if (categoryId <= 0)
                    {
                        continue;
                    }

                    string insertQuery = @"
                        INSERT INTO CompanyCategories
                            (company_id, category_id, priority)
                        VALUES
                            (@CompanyId, @CategoryId, @Priority)";

                    using SqlCommand insertCommand = new SqlCommand(insertQuery, connection, transaction);
                    insertCommand.Parameters.AddWithValue("@CompanyId", companyId);
                    insertCommand.Parameters.AddWithValue("@CategoryId", categoryId);
                    insertCommand.Parameters.AddWithValue("@Priority", companyPriority);

                    insertCommand.ExecuteNonQuery();
                }

                transaction.Commit();

                return Ok(new
                {
                    message = "Company categories saved successfully.",
                    priority = companyPriority
                });
            }
            catch
            {
                transaction.Rollback();
                throw;
            }
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                message = "Could not save company categories.",
                error = ex.Message
            });
        }
    }

    // Looks up the priority of a company's subscription, defaulting to 1 if none is set.
    private int GetCompanySubscriptionPriority(SqlConnection connection, SqlTransaction transaction, int companyId)
    {
        string query = @"
            SELECT ISNULL(s.priority, 1)
            FROM Company c
            LEFT JOIN Subscriptions s
                ON c.subscription_id = s.subscription_id
            WHERE c.company_id = @CompanyId";

        using SqlCommand command = new SqlCommand(query, connection, transaction);
        command.Parameters.AddWithValue("@CompanyId", companyId);

        object? result = command.ExecuteScalar();

        if (result == null || result == DBNull.Value)
        {
            return 1;
        }

        return Convert.ToInt32(result);
    }

    // Returns the id of an existing category matching the name, or inserts a new one.
    public static int GetOrCreateCategory(SqlConnection connection, SqlTransaction? transaction, string categoryName)
    {
        if (string.IsNullOrWhiteSpace(categoryName))
        {
            throw new ArgumentException("Category name is required.", nameof(categoryName));
        }

        string cleanCategoryName = categoryName.Trim();

        string checkQuery = @"
            SELECT category_id
            FROM [Category]
            WHERE category_name = @CategoryName";

        using (SqlCommand checkCommand = new SqlCommand(checkQuery, connection, transaction))
        {
            checkCommand.Parameters.AddWithValue("@CategoryName", cleanCategoryName);

            object? existingId = checkCommand.ExecuteScalar();

            if (existingId != null && existingId != DBNull.Value)
            {
                return Convert.ToInt32(existingId);
            }
        }

        string insertQuery = @"
            INSERT INTO [Category] (category_name)
            OUTPUT INSERTED.category_id
            VALUES (@CategoryName)";

        using SqlCommand insertCommand = new SqlCommand(insertQuery, connection, transaction);
        insertCommand.Parameters.AddWithValue("@CategoryName", cleanCategoryName);

        object? newId = insertCommand.ExecuteScalar();

        if (newId == null || newId == DBNull.Value)
        {
            throw new Exception("Could not create category.");
        }

        return Convert.ToInt32(newId);
    }

    // Overload of GetOrCreateCategory without a transaction.
    public static int GetOrCreateCategory(SqlConnection connection, string categoryName)
    {
        return GetOrCreateCategory(connection, null, categoryName);
    }
}

public class CategoryRequest
{
    public string CategoryName { get; set; } = "";
}

public class SaveCompanyCategoriesRequest
{
    public List<int> CategoryIds { get; set; } = new List<int>();
}
