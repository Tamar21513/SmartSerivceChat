using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using System.Net.Http.Json;

[ApiController]
[Route("api/[controller]")]
public class ThingsTheUserHasController : ControllerBase
{
    private readonly string connectionString =
        @"Server=TAMAR-MORIEL\SQLEXPRESS;Database=SmartServiceChatDB;Trusted_Connection=True;TrustServerCertificate=True;";

    private readonly HttpClient _httpClient;

    // Stores the injected HttpClient used to call the Python service.
    public ThingsTheUserHasController(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    // Loads a user's ThingsTheUserHas content from SQL and forwards it to the Python service.
    [HttpGet("user/{userId}")]
    public async Task<IActionResult> GetThingsTheUserHasByUserId(int userId)
    {
        try
        {
            ThingsTheUserHas thingsTheUserHas = new ThingsTheUserHas
            {
                UserId = userId,
                ThingsTheUserHasContent = new List<string>()
            };

            string query = @"SELECT ThingsTheUserHas_id, user_id, ThingsTheUserHas_content FROM ThingsTheUserHas WHERE user_id = @UserId;";

            using (SqlConnection connection = new SqlConnection(connectionString))
            {
                connection.Open();

                using (SqlCommand command = new SqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", userId);

                    using (SqlDataReader reader = command.ExecuteReader())
                    {
                        if (reader.Read())
                        {
                            thingsTheUserHas.ThingsTheUserHasId = Convert.ToInt32(reader["ThingsTheUserHas_id"]);
                            thingsTheUserHas.UserId = Convert.ToInt32(reader["user_id"]);
                            string content = reader["ThingsTheUserHas_content"]?.ToString() ?? "";
                            thingsTheUserHas.ThingsTheUserHasContent.Add(content);
                        }
                        else
                        {
                            return NotFound(new
                            {
                                message = "No ThingsTheUserHas file found for this user."
                            });
                        }
                    }
                }
            }

            string pythonUrl = "http://localhost:8000/things-the-user-has";

            HttpResponseMessage pythonResponse =
                await _httpClient.PostAsJsonAsync(pythonUrl, thingsTheUserHas);

            if (!pythonResponse.IsSuccessStatusCode)
            {
                return StatusCode(500, new
                {
                    message = "Data loaded from SQL, but sending to Python failed.",
                    pythonStatusCode = pythonResponse.StatusCode
                });
            }

            object? pythonResult =
                await pythonResponse.Content.ReadFromJsonAsync<object>();

            return Ok(new
            {
                message = "Data loaded and sent to Python successfully.",
                dataSentToPython = thingsTheUserHas,
                pythonResult = pythonResult
            });
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
}
