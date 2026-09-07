using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using System.Data;

namespace ConnectedWithReactAndC.Controllers
{
    [ApiController]
    [Route("api/CompanyData")]
    public class CompanyDataController : ControllerBase
    {
        private readonly IConfiguration _configuration;

        // Stores the injected configuration used to resolve the connection string.
        public CompanyDataController(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public class SaveCompanyDataRequest
        {
            public int CompanyId { get; set; }
            public string CompanyName { get; set; } = "";
            public string Title { get; set; } = "";
            public string Content { get; set; } = "";
            public string Topic { get; set; } = "";

            public string KnowledgeSource { get; set; } = "";
            public string AdditionalNotes { get; set; } = "";
            public string CompanyWebsite { get; set; } = "";
            public string SupportEmail { get; set; } = "";
        }

        // Loads a company's subscription info and knowledge-base content, parsing website/email/knowledge fields out of the stored content.
        [HttpGet("{companyId:int}")]
        public IActionResult GetCompanyData(int companyId)
        {
            if (companyId <= 0)
            {
                return BadRequest("CompanyId is required.");
            }

            string? connectionString = _configuration.GetConnectionString("DefaultConnection");

            if (string.IsNullOrWhiteSpace(connectionString))
            {
                return StatusCode(500, "DefaultConnection was not found.");
            }

            try
            {
                using SqlConnection connection = new SqlConnection(connectionString);
                connection.Open();

                string query = @"
                    SELECT
                        c.company_id,
                        c.company_name,
                        c.subscription_id,
                        s.subscription_name,
                        s.priority AS subscription_priority,
                        cd.data_id,
                        cd.title,
                        cd.content,
                        cd.topic
                    FROM Company c
                    LEFT JOIN Subscriptions s
                        ON c.subscription_id = s.subscription_id
                    LEFT JOIN CompanyData cd
                        ON c.company_id = cd.company_id
                    WHERE c.company_id = @CompanyId;
                ";

                using SqlCommand command = new SqlCommand(query, connection);
                command.Parameters.Add("@CompanyId", SqlDbType.Int).Value = companyId;

                int resultCompanyId;
                string resultCompanyName;
                int resultSubscriptionId;
                string resultSubscriptionName;
                int resultSubscriptionPriority;
                int resultDataId;
                string resultTitle;
                string resultContent;
                string resultTopic;

                using (SqlDataReader reader = command.ExecuteReader())
                {
                    if (!reader.Read())
                    {
                        return NotFound("Company was not found.");
                    }

                    resultCompanyId = Convert.ToInt32(reader["company_id"]);
                    resultCompanyName = reader["company_name"]?.ToString() ?? "";

                    resultSubscriptionId =
                        reader["subscription_id"] == DBNull.Value
                            ? 0
                            : Convert.ToInt32(reader["subscription_id"]);

                    resultSubscriptionName =
                        reader["subscription_name"] == DBNull.Value
                            ? ""
                            : reader["subscription_name"]?.ToString() ?? "";

                    resultSubscriptionPriority =
                        reader["subscription_priority"] == DBNull.Value
                            ? 0
                            : Convert.ToInt32(reader["subscription_priority"]);

                    resultDataId =
                        reader["data_id"] == DBNull.Value
                            ? 0
                            : Convert.ToInt32(reader["data_id"]);

                    resultTitle =
                        reader["title"] == DBNull.Value
                            ? ""
                            : reader["title"]?.ToString() ?? "";

                    resultContent =
                        reader["content"] == DBNull.Value
                            ? ""
                            : reader["content"]?.ToString() ?? "";

                    resultTopic =
                        reader["topic"] == DBNull.Value
                            ? ""
                            : reader["topic"]?.ToString() ?? "";
                }

                string companyWebsite = ExtractBetween(
                    resultContent,
                    "Company website:",
                    "Support email:"
                );

                string supportEmail = ExtractBetween(
                    resultContent,
                    "Support email:",
                    "Knowledge source:"
                );

                string knowledgeSource = ExtractBetween(
                    resultContent,
                    "Knowledge source:",
                    null
                );
                
                if (string.IsNullOrWhiteSpace(knowledgeSource) &&
                    !resultContent.Contains("Company website:", StringComparison.OrdinalIgnoreCase))
                {
                    knowledgeSource = resultContent;
                }

                var result = new
                {
                    companyId = resultCompanyId,
                    companyName = resultTitle != "" ? resultTitle : resultCompanyName,
                    subscriptionId = resultSubscriptionId,
                    subscriptionName = resultSubscriptionName,
                    priority = resultSubscriptionPriority,
                    dataId = resultDataId,
                    title = resultTitle,
                    content = resultContent,
                    topic = resultTopic,

                    companyWebsite = companyWebsite,
                    supportEmail = supportEmail,
                    knowledgeSource = knowledgeSource,
                    additionalNotes = resultTopic,

                    categories = GetCompanyCategories(connection, companyId)
                };

                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, ex.Message);
            }
        }

        // Updates the company's name and upserts its knowledge-base data (title/content/topic).
        [HttpPost]
        public IActionResult SaveCompanyData([FromBody] SaveCompanyDataRequest request)
        {
            if (request.CompanyId <= 0)
            {
                return BadRequest("CompanyId is required.");
            }

            if (string.IsNullOrWhiteSpace(request.CompanyName))
            {
                return BadRequest("CompanyName is required.");
            }

            string companyName = request.CompanyName.Trim();
            string content = BuildContent(request);

            if (string.IsNullOrWhiteSpace(content))
            {
                return BadRequest("Content is required.");
            }

            string? connectionString = _configuration.GetConnectionString("DefaultConnection");

            if (string.IsNullOrWhiteSpace(connectionString))
            {
                return StatusCode(500, "DefaultConnection was not found.");
            }

            using SqlConnection connection = new SqlConnection(connectionString);
            connection.Open();

            using SqlTransaction transaction = connection.BeginTransaction();

            try
            {
                UpdateCompanyName(connection, transaction, request.CompanyId, companyName);
                UpsertCompanyData(connection, transaction, request, companyName, content);

                transaction.Commit();

                return Ok(new
                {
                    message = "Company database saved successfully.",
                    companyId = request.CompanyId,
                    companyName = companyName,
                    title = companyName,
                    content = content,
                    topic = GetFinalTopic(request)
                });
            }
            catch (Exception ex)
            {
                transaction.Rollback();
                return StatusCode(500, ex.Message);
            }
        }

        // Updates the company's name in the Company table.
        private static void UpdateCompanyName(
            SqlConnection connection,
            SqlTransaction transaction,
            int companyId,
            string companyName)
        {
            string query = @"
                UPDATE Company
                SET company_name = @CompanyName
                WHERE company_id = @CompanyId;
            ";

            using SqlCommand command = new SqlCommand(query, connection, transaction);

            command.Parameters.Add("@CompanyId", SqlDbType.Int).Value = companyId;
            command.Parameters.Add("@CompanyName", SqlDbType.VarChar, 150).Value = companyName;

            int rowsAffected = command.ExecuteNonQuery();

            if (rowsAffected == 0)
            {
                throw new Exception("Company was not found in Companies table.");
            }
        }

        // Inserts or updates the CompanyData row (title/content/topic) for a company.
        private static void UpsertCompanyData(
            SqlConnection connection,
            SqlTransaction transaction,
            SaveCompanyDataRequest request,
            string companyName,
            string content)
        {
            string query = @"
                IF EXISTS (
                    SELECT 1
                    FROM CompanyData
                    WHERE company_id = @CompanyId
                )
                BEGIN
                    UPDATE CompanyData
                    SET
                        title = @Title,
                        content = @Content,
                        topic = @Topic
                    WHERE company_id = @CompanyId;
                END
                ELSE
                BEGIN
                    INSERT INTO CompanyData (
                        company_id,
                        title,
                        content,
                        topic
                    )
                    VALUES (
                        @CompanyId,
                        @Title,
                        @Content,
                        @Topic
                    );
                END
            ";

            using SqlCommand command = new SqlCommand(query, connection, transaction);

            command.Parameters.Add("@CompanyId", SqlDbType.Int).Value = request.CompanyId;

            command.Parameters.Add("@Title", SqlDbType.VarChar, 200).Value = companyName;

            command.Parameters.Add("@Content", SqlDbType.NVarChar, -1).Value = content;

            command.Parameters.Add("@Topic", SqlDbType.NVarChar, -1).Value = GetFinalTopic(request);

            command.ExecuteNonQuery();
        }

        // Assembles the stored content string from website/email/knowledge-source fields, falling back to raw Content if all are empty.
        private static string BuildContent(SaveCompanyDataRequest request)
        {
            List<string> parts = new List<string>();
        
            parts.Add($"Company website:\n{request.CompanyWebsite?.Trim() ?? ""}");
            parts.Add($"Support email:\n{request.SupportEmail?.Trim() ?? ""}");
            parts.Add($"Knowledge source:\n{request.KnowledgeSource?.Trim() ?? ""}");
        
            string builtContent = string.Join("\n\n", parts).Trim();
        
            if (!string.IsNullOrWhiteSpace(builtContent))
            {
                return builtContent;
            }
        
            if (!string.IsNullOrWhiteSpace(request.Content))
            {
                return request.Content.Trim();
            }
        
            return "";
        }

        // Picks the topic to store, preferring AdditionalNotes over Topic.
        private static string GetFinalTopic(SaveCompanyDataRequest request)
        {
            if (!string.IsNullOrWhiteSpace(request.AdditionalNotes))
            {
                return request.AdditionalNotes.Trim();
            }

            if (!string.IsNullOrWhiteSpace(request.Topic))
            {
                return request.Topic.Trim();
            }

            return "";
        }

        // Extracts the substring between startMarker and endMarker (or to the end of text if endMarker is null/not found).
        private static string ExtractBetween(string text, string startMarker, string? endMarker)
        {
            if (string.IsNullOrWhiteSpace(text))
            {
                return "";
            }

            int startIndex = text.IndexOf(startMarker, StringComparison.OrdinalIgnoreCase);

            if (startIndex == -1)
            {
                return "";
            }

            startIndex += startMarker.Length;

            if (string.IsNullOrWhiteSpace(endMarker))
            {
                return text.Substring(startIndex).Trim();
            }

            int endIndex = text.IndexOf(endMarker, startIndex, StringComparison.OrdinalIgnoreCase);

            if (endIndex == -1)
            {
                return text.Substring(startIndex).Trim();
            }

            return text.Substring(startIndex, endIndex - startIndex).Trim();
        }

        // Returns the categories assigned to a company, ordered by priority then name.
        private static List<object> GetCompanyCategories(SqlConnection connection, int companyId)
        {
            List<object> categories = new List<object>();

            string query = @"
                SELECT
                    cc.category_id,
                    ca.category_name,
                    cc.priority
                FROM CompanyCategories cc
                JOIN [Category] ca
                    ON cc.category_id = ca.category_id
                WHERE cc.company_id = @CompanyId
                ORDER BY cc.priority ASC, ca.category_name ASC;
            ";

            using SqlCommand command = new SqlCommand(query, connection);
            command.Parameters.Add("@CompanyId", SqlDbType.Int).Value = companyId;

            using SqlDataReader reader = command.ExecuteReader();

            while (reader.Read())
            {
                categories.Add(new
                {
                    categoryId = Convert.ToInt32(reader["category_id"]),
                    categoryName = reader["category_name"]?.ToString() ?? "",
                    priority = Convert.ToInt32(reader["priority"])
                });
            }

            return categories;
        }
    }
}