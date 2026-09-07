using Microsoft.Data.SqlClient;

public class SubscriptionRepository
{
    private readonly string connectionString;

    // Stores the connection string used for subscription queries.
    public SubscriptionRepository(string connectionString)
    {
        this.connectionString = connectionString;
    }

    // Fetches all active subscriptions of the given type, ordered by priority then price.
    public List<Subscription> GetAllSubscriptions(string subscriptionsType)
    {
        if (subscriptionsType != "Company" && subscriptionsType != "Customer")
        {
            throw new ArgumentException("Subscription type must be either Company or Customer.");
        }

        List<Subscription> subscriptionsList = new List<Subscription>();

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
            WHERE subscription_type = @SubscriptionsType
              AND is_active = 1
            ORDER BY priority ASC, price ASC;
        ";

        using SqlConnection connection = new SqlConnection(connectionString);
        connection.Open();

        using SqlCommand command = new SqlCommand(query, connection);
        command.Parameters.AddWithValue("@SubscriptionsType", subscriptionsType);

        using SqlDataReader reader = command.ExecuteReader();

        while (reader.Read())
        {
            Subscription s = new Subscription
            {
                SubscriptionId = Convert.ToInt32(reader["subscription_id"]),
                Name = reader["subscription_name"]?.ToString() ?? "",
                DurationDays = Convert.ToInt32(reader["duration_days"]),
                Priority = Convert.ToInt32(reader["priority"]),
                Price = Convert.ToInt32(reader["price"]),
                Description = reader["description"]?.ToString() ?? "",
                SubscriptionType = reader["subscription_type"]?.ToString() ?? "",
                IsActive = Convert.ToBoolean(reader["is_active"])
            };

            subscriptionsList.Add(s);
        }

        return subscriptionsList;
    }
}
