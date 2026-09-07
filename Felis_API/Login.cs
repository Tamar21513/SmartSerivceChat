
using Microsoft.Data.SqlClient;
using Isopoh.Cryptography.Argon2;

public class Login
{
    static string connectionString =
        @"Server=TAMAR-MORIEL\SQLEXPRESS;Database=SmartServiceChatDB;Trusted_Connection=True;TrustServerCertificate=True;";

    // Dispatches to the customer or company login flow based on account type.
    public static User? LoginUser(
        string mail_or_username = " ",
        string entered_password = " ",
        string accountType = " "
    )
    {
        string cleanAccountType = accountType.Trim().ToLower();

        if (cleanAccountType == "customer")
        {
            return LoginCustomer(mail_or_username, entered_password);
        }

        if (cleanAccountType == "company")
        {
            return LoginCompany(mail_or_username, entered_password);
        }

        return null;
    }

    // Looks up a customer by email or username and verifies the password hash.
    private static User? LoginCustomer(string mail_or_username, string entered_password)
    {
        using SqlConnection conn = new SqlConnection(connectionString);
        conn.Open();

        using SqlCommand cursor = new SqlCommand(
            @"
            SELECT 
                u.user_id,
                u.username,
                u.email,
                u.password_hash,
                u.city,
                u.age,
                u.occupation,
                u.role,
                u.subscription_id,
                s.subscription_name,
                s.priority
            FROM Users u
            LEFT JOIN Subscriptions s
                ON u.subscription_id = s.subscription_id
            WHERE u.email = @mail_or_username 
               OR u.username = @mail_or_username
            ", conn);

        cursor.Parameters.AddWithValue("@mail_or_username", mail_or_username.Trim());

        using SqlDataReader reader = cursor.ExecuteReader();

        if (!reader.Read())
        {
            return null;
        }

        string storedHash = reader["password_hash"]?.ToString() ?? "";

        try
        {
            if (!Argon2.Verify(storedHash, entered_password))
            {
                return null;
            }
        }
        catch
        {
            return null;
        }

        return new User
        {
            Id = Convert.ToInt32(reader["user_id"]),
            Name = reader["username"]?.ToString() ?? "",
            Email = reader["email"]?.ToString() ?? "",
            PasswordHash = storedHash,
            City = reader["city"] == DBNull.Value ? "" : reader["city"]?.ToString() ?? "",
            Age = reader["age"] == DBNull.Value ? 0 : Convert.ToInt32(reader["age"]),
            Occupation = reader["occupation"] == DBNull.Value ? "" : reader["occupation"]?.ToString() ?? "",
            Role = reader["role"]?.ToString() ?? "",
            UserType = "Customer",
            SubscriptionId = reader["subscription_id"] == DBNull.Value ? 0 : Convert.ToInt32(reader["subscription_id"]),
            SubscriptionName = reader["subscription_name"] == DBNull.Value ? "" : reader["subscription_name"]?.ToString() ?? "",
            Priority = reader["priority"] == DBNull.Value ? 0 : Convert.ToInt32(reader["priority"])
        };
    }

    // Looks up an active company by name and verifies the password hash.
    private static User? LoginCompany(string companyName, string entered_password)
    {
        using SqlConnection conn = new SqlConnection(connectionString);
        conn.Open();

        using SqlCommand cursor = new SqlCommand(
            @"
            SELECT 
                c.company_id,
                c.company_name,
                c.password_hash,
                c.is_active,
                c.subscription_id,
                s.subscription_name,
                s.priority
            FROM Company c
            LEFT JOIN Subscriptions s
                ON c.subscription_id = s.subscription_id
            WHERE LOWER(LTRIM(RTRIM(c.company_name))) = LOWER(LTRIM(RTRIM(@companyName)))
              AND c.is_active = 1
            ", conn);

        cursor.Parameters.AddWithValue("@companyName", companyName.Trim());

        using SqlDataReader reader = cursor.ExecuteReader();

        if (!reader.Read())
        {
            return null;
        }

        string storedHash = reader["password_hash"]?.ToString() ?? "";

        try
        {
            if (!Argon2.Verify(storedHash, entered_password))
            {
                return null;
            }
        }
        catch
        {
            return null;
        }

        return new User
        {
            Id = Convert.ToInt32(reader["company_id"]),
            Name = reader["company_name"]?.ToString() ?? "",
            Email = "",
            PasswordHash = storedHash,
            City = "",
            Age = 0,
            Occupation = "",
            Role = "company",
            UserType = "Company",
            SubscriptionId = reader["subscription_id"] == DBNull.Value ? 0 : Convert.ToInt32(reader["subscription_id"]),
            SubscriptionName = reader["subscription_name"] == DBNull.Value ? "" : reader["subscription_name"]?.ToString() ?? "",
            Priority = reader["priority"] == DBNull.Value ? 0 : Convert.ToInt32(reader["priority"])
        };
    }
}
