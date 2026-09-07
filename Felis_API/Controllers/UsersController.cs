using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly string connectionString =
        @"Server=TAMAR-MORIEL\SQLEXPRESS;Database=SmartServiceChatDB;Trusted_Connection=True;TrustServerCertificate=True;";

    // Updates a user's city, age, and occupation in the database.
    [HttpPut("{id}")]
    public IActionResult UpdateUser(int id, [FromBody] User updatedUser)
    {
        try
        {
            string query = @"
                UPDATE Users
                SET 
                    city = @City,
                    age = @Age,
                    Occupation = @Occupation
                WHERE user_id = @UserId;
            ";

            using (SqlConnection connection = new SqlConnection(connectionString))
            {
                connection.Open();

                using (SqlCommand command = new SqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", id);
                    command.Parameters.AddWithValue("@City", updatedUser.City ?? "");
                    command.Parameters.AddWithValue("@Age", updatedUser.Age);
                    command.Parameters.AddWithValue("@Occupation", updatedUser.Occupation ?? "");

                    int rowsAffected = command.ExecuteNonQuery();

                    if (rowsAffected == 0)
                    {
                        return NotFound(new
                        {
                            success = false,
                            message = "User was not found."
                        });
                    }
                }
            }

            return Ok(new
            {
                success = true,
                message = "User details updated successfully."
            });
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
}