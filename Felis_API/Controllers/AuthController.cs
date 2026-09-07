

using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using Isopoh.Cryptography.Argon2;
using System.Text.RegularExpressions;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly string connectionString =
        @"Server=TAMAR-MORIEL\SQLEXPRESS;Database=SmartServiceChatDB;Trusted_Connection=True;TrustServerCertificate=True;";

    // Validates the login request and attempts to authenticate the user or company.
    [HttpPost("login")]
    public IActionResult LoginUser([FromBody] LoginRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.MailOrUsername) ||
            string.IsNullOrWhiteSpace(request.Password) ||
            string.IsNullOrWhiteSpace(request.AccountType))
        {
            return BadRequest(new
            {
                success = false,
                message = "Name/email, password and account type are required."
            });
        }

        User? user = Login.LoginUser(
            request.MailOrUsername,
            request.Password,
            request.AccountType
        );

        if (user == null)
        {
            return Unauthorized(new
            {
                success = false,
                message = "User/company does not exist, password is incorrect, or account type is wrong."
            });
        }

        return Ok(new
        {
            success = true,
            message = "Login successful.",
            user = user
        });
    }

    // Validates a registration request and creates a new customer or company account.
    [HttpPost("register")]
    public IActionResult Register([FromBody] RegisterRequest request)
    {
        if (request == null)
        {
            return BadRequest(new
            {
                success = false,
                message = "Invalid request."
            });
        }

        if (string.IsNullOrWhiteSpace(request.AccountType))
        {
            return BadRequest(new
            {
                success = false,
                message = "Account type is required."
            });
        }

        string accountType = request.AccountType.Trim().ToLower();

        if (accountType != "customer" && accountType != "company")
        {
            return BadRequest(new
            {
                success = false,
                message = "Account type must be customer or company."
            });
        }

        if (string.IsNullOrWhiteSpace(request.Name))
        {
            return BadRequest(new
            {
                success = false,
                message = "Missing user name, please enter a name."
            });
        }

        if (string.IsNullOrWhiteSpace(request.Password))
        {
            return BadRequest(new
            {
                success = false,
                message = "Missing Password, please enter a Password."
            });
        }

        if (!IsStrongPassword(request.Password))
        {
            return BadRequest(new
            {
                success = false,
                message = "The password is not strong enough. It must contain at least 6 characters, uppercase letter, lowercase letter, number, and special character."
            });
        }

        if (accountType == "customer" && string.IsNullOrWhiteSpace(request.Email))
        {
            return BadRequest(new
            {
                success = false,
                message = "Email is required for customer accounts."
            });
        }

        if (request.SubscriptionId <= 0)
        {
            return BadRequest(new
            {
                success = false,
                message = "No subscription type selected."
            });
        }

        using SqlConnection connection = new SqlConnection(connectionString);
        connection.Open();

        using SqlTransaction transaction = connection.BeginTransaction();

        try
        {
            string expectedSubscriptionType =
                accountType == "company" ? "Company" : "Customer";

            if (!SubscriptionMatchesAccountType(
                    connection,
                    transaction,
                    request.SubscriptionId,
                    expectedSubscriptionType))
            {
                transaction.Rollback();

                return BadRequest(new
                {
                    success = false,
                    message = "Subscription does not match account type."
                });
            }

            if (accountType == "customer")
            {
                if (CustomerExists(connection, transaction, request.Email, request.Name))
                {
                    transaction.Rollback();

                    return BadRequest(new
                    {
                        success = false,
                        message = "A user with this email and username already exists in the system."
                    });
                }

                string passwordHash = Argon2.Hash(request.Password);

                User registeredUser = RegisterCustomer(
                    connection,
                    transaction,
                    request,
                    passwordHash
                );

                CreateEmptyThingsTheUserHas(
                    connection,
                    transaction,
                    registeredUser.Id
                );

                transaction.Commit();

                return Ok(new
                {
                    success = true,
                    message = "Registration completed successfully.",
                    accountType = "customer",
                    user = registeredUser
                });
            }
            else
            {
                if (CompanyExists(connection, transaction, request.Name))
                {
                    transaction.Rollback();

                    return BadRequest(new
                    {
                        success = false,
                        message = "A company with this name already exists in the system."
                    });
                }

                string passwordHash = Argon2.Hash(request.Password);

                Company registeredCompany = RegisterCompany(
                    connection,
                    transaction,
                    request,
                    passwordHash
                );

                transaction.Commit();

                return Ok(new
                {
                    success = true,
                    message = "Registration completed successfully.",
                    accountType = "company",
                    company = registeredCompany
                });
            }
        }
        catch (SqlException ex) when (ex.Number == 2627 || ex.Number == 2601)
        {
            transaction.Rollback();

            return BadRequest(new
            {
                success = false,
                message = "Duplicate data. User or company already exists."
            });
        }
        catch (Exception ex)
        {
            transaction.Rollback();

            return StatusCode(500, new
            {
                success = false,
                message = "Registration failed.",
                error = ex.Message
            });
        }
    }

    // Checks the password meets the minimum length and character-variety requirements.
    private static bool IsStrongPassword(string password)
    {
        if (string.IsNullOrWhiteSpace(password))
            return false;

        if (password.Length < 6)
            return false;

        bool hasLowercase = Regex.IsMatch(password, "[a-z]");
        bool hasUppercase = Regex.IsMatch(password, "[A-Z]");
        bool hasDigit = Regex.IsMatch(password, "[0-9]");
        bool hasSpecialChar = Regex.IsMatch(password, @"[^a-zA-Z0-9]");

        return hasLowercase && hasUppercase && hasDigit && hasSpecialChar;
    }

    // Checks whether a user with the given email and username already exists.
    private static bool CustomerExists(
        SqlConnection connection,
        SqlTransaction transaction,
        string email,
        string username)
    {
        string query = @"
            SELECT TOP 1 user_id
            FROM Users
            WHERE LOWER(email) = LOWER(@Email)
              AND LOWER(username) = LOWER(@Username);
        ";

        using SqlCommand command = new SqlCommand(query, connection, transaction);

        command.Parameters.AddWithValue("@Email", email.Trim());
        command.Parameters.AddWithValue("@Username", username.Trim());

        object? result = command.ExecuteScalar();

        return result != null;
    }

    // Checks whether a company with the given name already exists.
    private static bool CompanyExists(
        SqlConnection connection,
        SqlTransaction transaction,
        string companyName)
    {
        string query = @"
            SELECT TOP 1 company_id
            FROM Company
            WHERE LOWER(company_name) = LOWER(@CompanyName);
        ";

        using SqlCommand command = new SqlCommand(query, connection, transaction);

        command.Parameters.AddWithValue("@CompanyName", companyName.Trim());

        object? result = command.ExecuteScalar();

        return result != null;
    }

    // Checks that the given subscription is active and matches the expected account type.
    private static bool SubscriptionMatchesAccountType(
        SqlConnection connection,
        SqlTransaction transaction,
        int subscriptionId,
        string expectedSubscriptionType)
    {
        string query = @"
            SELECT COUNT(*)
            FROM Subscriptions
            WHERE subscription_id = @SubscriptionId
              AND subscription_type = @SubscriptionType
              AND is_active = 1;
        ";

        using SqlCommand command = new SqlCommand(query, connection, transaction);

        command.Parameters.AddWithValue("@SubscriptionId", subscriptionId);
        command.Parameters.AddWithValue("@SubscriptionType", expectedSubscriptionType);

        int count = Convert.ToInt32(command.ExecuteScalar());

        return count > 0;
    }

    // Inserts a new customer row into Users and returns the resulting User object.
    private static User RegisterCustomer(
        SqlConnection connection,
        SqlTransaction transaction,
        RegisterRequest request,
        string passwordHash)
    {
        string query = @"
            INSERT INTO Users
            (
                username,
                email,
                password_hash,
                city,
                age,
                occupation,
                role,
                subscription_id
            )
            OUTPUT INSERTED.user_id
            VALUES
            (
                @Username,
                @Email,
                @PasswordHash,
                @City,
                @Age,
                @Occupation,
                @Role,
                @SubscriptionId
            );
        ";

        using SqlCommand command = new SqlCommand(query, connection, transaction);

        command.Parameters.AddWithValue("@Username", request.Name.Trim().ToLower());
        command.Parameters.AddWithValue("@Email", request.Email.Trim().ToLower());
        command.Parameters.AddWithValue("@PasswordHash", passwordHash);

        command.Parameters.AddWithValue(
            "@City",
            string.IsNullOrWhiteSpace(request.City)
                ? DBNull.Value
                : request.City.Trim()
        );

        command.Parameters.AddWithValue(
            "@Age",
            request.Age.HasValue
                ? request.Age.Value
                : DBNull.Value
        );

        command.Parameters.AddWithValue(
            "@Occupation",
            string.IsNullOrWhiteSpace(request.Occupation)
                ? DBNull.Value
                : request.Occupation.Trim()
        );

        command.Parameters.AddWithValue("@Role", "user");
        command.Parameters.AddWithValue("@SubscriptionId", request.SubscriptionId);

        int userId = Convert.ToInt32(command.ExecuteScalar());

        return new User
        {
            Id = userId,
            Name = request.Name.Trim().ToLower(),
            Email = request.Email.Trim().ToLower(),
            PasswordHash = "",
            City = request.City ?? "",
            Age = request.Age ?? 0,
            Occupation = request.Occupation ?? "",
            Role = "user",
            UserType = "Customer",
            SubscriptionId = request.SubscriptionId
        };
    }

    // Creates an empty ThingsTheUserHas row for a newly registered user.
    private static void CreateEmptyThingsTheUserHas(
        SqlConnection connection,
        SqlTransaction transaction,
        int userId)
    {
        string query = @"
            INSERT INTO ThingsTheUserHas
            (
                user_id,
                ThingsTheUserHas_content
            )
            VALUES
            (
                @UserId,
                N''
            );
        ";

        using SqlCommand command = new SqlCommand(query, connection, transaction);

        command.Parameters.AddWithValue("@UserId", userId);

        command.ExecuteNonQuery();
    }

    // Inserts a new company row into Company and returns the resulting Company object.
    private static Company RegisterCompany(
        SqlConnection connection,
        SqlTransaction transaction,
        RegisterRequest request,
        string passwordHash)
    {
        string query = @"
            INSERT INTO Company
            (
                company_name,
                password_hash,
                is_active,
                subscription_id,
                subscription_start_date
            )
            OUTPUT INSERTED.company_id
            VALUES
            (
                @CompanyName,
                @PasswordHash,
                @IsActive,
                @SubscriptionId,
                GETDATE()
            );
        ";

        using SqlCommand command = new SqlCommand(query, connection, transaction);

        command.Parameters.AddWithValue("@CompanyName", request.Name.Trim());
        command.Parameters.AddWithValue("@PasswordHash", passwordHash);
        command.Parameters.AddWithValue("@IsActive", true);
        command.Parameters.AddWithValue("@SubscriptionId", request.SubscriptionId);

        int companyId = Convert.ToInt32(command.ExecuteScalar());

        return new Company
        {
            CompanyId = companyId,
            CompanyName = request.Name.Trim(),
            PasswordHash = "",
            IsActive = true,
            SubscriptionId = request.SubscriptionId,
            SubscriptionStartDate = DateTime.Now
        };
    }
}


