using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;

[ApiController]
[Route("api/[controller]")]
public class ReportsController : ControllerBase
{
    private readonly string connectionString = @"Server=TAMAR-MORIEL\SQLEXPRESS;Database=SmartServiceChatDB;Trusted_Connection=True;TrustServerCertificate=True;";

    // Returns all reports for a given user, most recent first.
    [HttpGet("user/{userId}")]
    public IActionResult GetReportsByUserId(int userId)
    {
        try
        {
            List<Report> reports = new List<Report>();

            string query = @"
                SELECT 
                    report_id,
                    user_id,
                    created_at,
                    report_content
                FROM Reports
                WHERE user_id = @UserId
                ORDER BY created_at DESC;
            ";

            using (SqlConnection connection = new SqlConnection(connectionString))
            {
                connection.Open();

                using (SqlCommand command = new SqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", userId);

                    using (SqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            Report report = new Report
                            {
                                ReportId = Convert.ToInt32(reader["report_id"]),
                                UserId = Convert.ToInt32(reader["user_id"]),
                                CreatedAt = Convert.ToDateTime(reader["created_at"]),
                                ReportContent = reader["report_content"]?.ToString() ?? ""
                            };

                            reports.Add(report);
                        }
                    }
                }
            }

            return Ok(reports);
        }
        catch (SqlException ex)
        {
            return StatusCode(500, new
            {
                message = "SQL error.",
                error = ex.Message
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                message = "Server error.",
                error = ex.Message
            });
        }
    }

    public class SaveChatRequest
    {
        public int UserId { get; set; }

        public int? ReportId { get; set; }

        public List<string> Conversation { get; set; } = new();
    }

    // Saves a chat conversation as a new report, or updates an existing one if ReportId is provided.
    [HttpPost("save-chat")]
    public IActionResult SaveChat([FromBody] SaveChatRequest request)
    {
        try
        {
            if (request.UserId <= 0)
            {
                return BadRequest(new
                {
                    success = false,
                    message = "Invalid user id."
                });
            }

            if (request.Conversation == null || request.Conversation.Count == 0)
            {
                return BadRequest(new
                {
                    success = false,
                    message = "Conversation is empty."
                });
            }

            string reportContent = BuildReportContent(request.Conversation);

            using (SqlConnection connection = new SqlConnection(connectionString))
            {
                connection.Open();

                Report savedReport;

                if (request.ReportId.HasValue && request.ReportId.Value > 0)
                {
                    savedReport = UpdateReport(connection, request.UserId, request.ReportId.Value, reportContent);
                }
                else
                {
                    savedReport = InsertReport(connection, request.UserId, reportContent);
                }

                return Ok(new
                {
                    success = true,
                    message = "Chat saved successfully.",
                    reportId = savedReport.ReportId,
                    userId = savedReport.UserId,
                    createdAt = savedReport.CreatedAt,
                    reportContent = savedReport.ReportContent
                });
            }
        }
        catch (SqlException ex)
        {
            return StatusCode(500, new
            {
                success = false,
                message = "SQL error.",
                error = ex.Message
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new
            {
                success = false,
                message = "Server error.",
                error = ex.Message
            });
        }
    }

    public class ConversationFromPythonRequest
    {
        public int UserId { get; set; }
        public List<string> Conversation { get; set; } = new();
    }

    // Legacy endpoint that adapts a Python-originated conversation payload into a SaveChat call.
    [HttpPost("from-python")]
    public IActionResult SaveConversationFromPython([FromBody] ConversationFromPythonRequest request)
    {
        SaveChatRequest saveChatRequest = new SaveChatRequest
        {
            UserId = request.UserId,
            ReportId = null,
            Conversation = request.Conversation
        };

        return SaveChat(saveChatRequest);
    }

    // Inserts a new report row and returns the saved report.
    private static Report InsertReport(SqlConnection connection, int userId, string reportContent)
    {
        string insertQuery = @"
            INSERT INTO Reports (user_id, report_content)
            OUTPUT INSERTED.report_id, INSERTED.user_id, INSERTED.created_at, INSERTED.report_content
            VALUES (@UserId, @ReportContent);
        ";

        using (SqlCommand command = new SqlCommand(insertQuery, connection))
        {
            command.Parameters.AddWithValue("@UserId", userId);
            command.Parameters.AddWithValue("@ReportContent", reportContent);

            using (SqlDataReader reader = command.ExecuteReader())
            {
                if (!reader.Read())
                {
                    throw new Exception("Insert failed.");
                }

                return ReadReport(reader);
            }
        }
    }

    // Updates an existing report's content; falls back to inserting a new report if the id was not found.
    private static Report UpdateReport(SqlConnection connection, int userId, int reportId, string reportContent)
    {
        string updateQuery = @"
            UPDATE Reports
            SET report_content = @ReportContent
            OUTPUT INSERTED.report_id, INSERTED.user_id, INSERTED.created_at, INSERTED.report_content
            WHERE report_id = @ReportId AND user_id = @UserId;
        ";

        using (SqlCommand command = new SqlCommand(updateQuery, connection))
        {
            command.Parameters.AddWithValue("@ReportId", reportId);
            command.Parameters.AddWithValue("@UserId", userId);
            command.Parameters.AddWithValue("@ReportContent", reportContent);

            using (SqlDataReader reader = command.ExecuteReader())
            {
                if (reader.Read())
                {
                    return ReadReport(reader);
                }
            }
        }

        return InsertReport(connection, userId, reportContent);
    }

    // Maps the current row of a SqlDataReader into a Report object.
    private static Report ReadReport(SqlDataReader reader)
    {
        return new Report
        {
            ReportId = Convert.ToInt32(reader["report_id"]),
            UserId = Convert.ToInt32(reader["user_id"]),
            CreatedAt = Convert.ToDateTime(reader["created_at"]),
            ReportContent = reader["report_content"]?.ToString() ?? ""
        };
    }

    // Builds the stored report text from the conversation transcript plus sentiment placeholder sections.
    private static string BuildReportContent(List<string> conversation)
    {
        List<string> lines = new List<string>();

        lines.Add("Transcript:");

        foreach (string item in conversation)
        {
            if (!string.IsNullOrWhiteSpace(item))
            {
                lines.Add(item.Trim());
            }
        }

        lines.Add("");
        lines.Add("Sentiment and Emotions:");
        lines.Add("Sentiment:");
        lines.Add("Emotions detected:");

        return string.Join(Environment.NewLine, lines);
    }
}
