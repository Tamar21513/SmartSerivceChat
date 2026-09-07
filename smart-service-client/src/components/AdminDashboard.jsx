
import React, { useEffect, useState } from "react";

const API_BASE_URL = "http://localhost:5199";

const emptySubscription = {
  subscriptionName: "",
  durationDays: "",
  priority: "",
  price: "",
  description: "",
  subscriptionType: "Customer",
  isActive: true,
};

// Admin screen for managing users, companies, and subscriptions
export default function AdminDashboard({ onLogout }) {
  const [users, setUsers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);

  const [activeTab, setActiveTab] = useState("users");
  const [message, setMessage] = useState("");
  const [successScreen, setSuccessScreen] = useState(null);

  const [showAddSubscription, setShowAddSubscription] = useState(false);
  const [newSubscription, setNewSubscription] = useState(emptySubscription);

  useEffect(() => {
    loadAdminData();
  }, []);

  // Fetches users, companies, and subscriptions from the admin API in parallel
  const loadAdminData = async () => {
    try {
      setMessage("");

      const [usersResponse, companiesResponse, subscriptionsResponse] =
        await Promise.all([
          fetch(`${API_BASE_URL}/api/admin/users`),
          fetch(`${API_BASE_URL}/api/admin/companies`),
          fetch(`${API_BASE_URL}/api/admin/subscriptions`),
        ]);

      if (!usersResponse.ok || !companiesResponse.ok || !subscriptionsResponse.ok) {
        throw new Error("Failed to load admin data.");
      }

      setUsers(await usersResponse.json());
      setCompanies(await companiesResponse.json());
      setSubscriptions(await subscriptionsResponse.json());
    } catch (error) {
      console.error(error);
      setMessage("Could not load admin data.");
    }
  };

  // Displays the full-screen success message with the given title and text
  const showSuccess = (title, text) => {
    setSuccessScreen({ title, text });
  };

  // Updates a single field on the user at the given index in local state
  const updateUserField = (index, field, value) => {
    setUsers((prevUsers) =>
      prevUsers.map((user, i) => (i === index ? { ...user, [field]: value } : user))
    );
  };

  // Updates a single field on the company at the given index in local state
  const updateCompanyField = (index, field, value) => {
    setCompanies((prevCompanies) =>
      prevCompanies.map((company, i) =>
        i === index ? { ...company, [field]: value } : company
      )
    );
  };

  // Updates a single field on the subscription at the given index in local state
  const updateSubscriptionField = (index, field, value) => {
    setSubscriptions((prevSubscriptions) =>
      prevSubscriptions.map((subscription, i) =>
        i === index ? { ...subscription, [field]: value } : subscription
      )
    );
  };

  // Updates a single field on the new-subscription form draft
  const updateNewSubscriptionField = (field, value) => {
    setNewSubscription((prev) => ({ ...prev, [field]: value }));
  };

  // Persists edits to a user via the admin API and refreshes the data
  const saveUser = async (user) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/users/${user.userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user.username,
          email: user.email,
          city: user.city,
          age: user.age === "" ? 0 : Number(user.age),
          occupation: user.occupation,
          role: user.role,
          subscriptionId: user.subscriptionId === "" ? 0 : Number(user.subscriptionId),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update user.");
      }

      await loadAdminData();
      showSuccess("נשמר בהצלחה", "פרטי הלקוח נשמרו במערכת.");
    } catch (error) {
      console.error(error);
      setMessage("Could not save user.");
    }
  };

  // Persists edits to a company via the admin API and refreshes the data
  const saveCompany = async (company) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/companies/${company.companyId}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            companyName: company.companyName,
            isActive: company.isActive,
            subscriptionId: company.subscriptionId === "" ? 0 : Number(company.subscriptionId),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update company.");
      }

      await loadAdminData();
      showSuccess("נשמר בהצלחה", "פרטי החברה נשמרו במערכת.");
    } catch (error) {
      console.error(error);
      setMessage("Could not save company.");
    }
  };

  // Persists edits to a subscription via the admin API and refreshes the data
  const saveSubscription = async (subscription) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/subscriptions/${subscription.subscriptionId}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            subscriptionName: subscription.subscriptionName,
            durationDays: Number(subscription.durationDays),
            priority: Number(subscription.priority),
            price: Number(subscription.price),
            description: subscription.description,
            subscriptionType: subscription.subscriptionType,
            isActive: Boolean(subscription.isActive),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update subscription.");
      }

      await loadAdminData();
      showSuccess("נשמר בהצלחה", "סוג המנוי נשמר במערכת.");
    } catch (error) {
      console.error(error);
      setMessage("Could not save subscription.");
    }
  };

  // Validates the new-subscription form, creates it via the API, and resets the form
  const addSubscription = async () => {
    try {
      if (!newSubscription.subscriptionName.trim()) {
        setMessage("Subscription name is required.");
        return;
      }

      if (Number(newSubscription.durationDays) <= 0) {
        setMessage("Duration must be greater than 0.");
        return;
      }

      if (Number(newSubscription.priority) <= 0) {
        setMessage("Priority must be greater than 0.");
        return;
      }

      if (Number(newSubscription.price) < 0) {
        setMessage("Price must be 0 or greater.");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/admin/subscriptions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subscriptionName: newSubscription.subscriptionName,
          durationDays: Number(newSubscription.durationDays),
          priority: Number(newSubscription.priority),
          price: Number(newSubscription.price),
          description: newSubscription.description,
          subscriptionType: newSubscription.subscriptionType,
          isActive: Boolean(newSubscription.isActive),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to add subscription.");
      }

      setNewSubscription(emptySubscription);
      setShowAddSubscription(false);
      await loadAdminData();
      showSuccess("נוסף בהצלחה", "סוג המנוי נוסף למערכת.");
    } catch (error) {
      console.error(error);
      setMessage("Could not add subscription.");
    }
  };

  // Confirms with the user, then deletes the given entity type/id via the admin API
  const deleteItem = async (type, id, name) => {
    const approved = window.confirm(`Delete ${name}?`);

    if (!approved) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/${type}/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Failed to delete ${type}.`);
      }

      await loadAdminData();
      showSuccess("נמחק בהצלחה", `${name} נמחק מהמערכת.`);
    } catch (error) {
      console.error(error);
      setMessage(`Could not delete ${name}.`);
    }
  };

  if (successScreen) {
    return (
      <div className="admin-page">
        <div className="success-screen-card wide-success-card">
          <div className="success-icon">✓</div>
          <h2>{successScreen.title}</h2>
          <p>{successScreen.text}</p>
          <button
            type="button"
            className="primary-button"
            onClick={() => setSuccessScreen(null)}
          >
            Back to admin
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <div className="top-bar">
        <div className="top-logo">
          <div>
            <strong>Admin Dashboard</strong>
            <span>Manage system data</span>
          </div>
        </div>

        <button type="button" className="light-button" onClick={onLogout}>
          Logout
        </button>
      </div>

      <div className="admin-card admin-main-card">
        <div className="admin-header-row">
          <div>
            <h1>System Management</h1>
            <p>View, edit, activate, deactivate and delete system data.</p>
          </div>

          <button type="button" className="primary-button" onClick={loadAdminData}>
            Refresh
          </button>
        </div>

        {message && <p className="admin-message">{message}</p>}

        <div className="admin-tabs-row">
          <div className="admin-tabs">
            <button
              type="button"
              className={activeTab === "users" ? "active" : ""}
              onClick={() => setActiveTab("users")}
            >
              Users
            </button>

            <button
              type="button"
              className={activeTab === "companies" ? "active" : ""}
              onClick={() => setActiveTab("companies")}
            >
              Companies
            </button>

            <button
              type="button"
              className={activeTab === "subscriptions" ? "active" : ""}
              onClick={() => setActiveTab("subscriptions")}
            >
              Subscriptions
            </button>
          </div>

          {activeTab === "subscriptions" && (
            <button
              type="button"
              className="primary-button add-subscription-button"
              onClick={() => setShowAddSubscription((prev) => !prev)}
            >
              {showAddSubscription ? "Close" : "+ Add subscription"}
            </button>
          )}
        </div>

        {activeTab === "users" && (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>City</th>
                  <th>Age</th>
                  <th>Occupation</th>
                  <th>Role</th>
                  <th>Subscription ID</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {users.map((user, index) => (
                  <tr key={user.userId}>
                    <td>{user.userId}</td>
                    <td>
                      <input
                        value={user.username || ""}
                        onChange={(e) => updateUserField(index, "username", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        value={user.email || ""}
                        onChange={(e) => updateUserField(index, "email", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        value={user.city || ""}
                        onChange={(e) => updateUserField(index, "city", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        value={user.age ?? ""}
                        onChange={(e) => updateUserField(index, "age", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        value={user.occupation || ""}
                        onChange={(e) => updateUserField(index, "occupation", e.target.value)}
                      />
                    </td>
                    <td>
                      <select
                        value={user.role || "user"}
                        onChange={(e) => updateUserField(index, "role", e.target.value)}
                      >
                        <option value="user">user</option>
                        <option value="admin">admin</option>
                      </select>
                    </td>
                    <td>
                      <input
                        type="number"
                        value={user.subscriptionId ?? ""}
                        onChange={(e) => updateUserField(index, "subscriptionId", e.target.value)}
                      />
                    </td>
                    <td className="admin-actions-cell">
                      <button type="button" className="light-button" onClick={() => saveUser(user)}>
                        Save
                      </button>
                      <button
                        type="button"
                        className="danger-button"
                        onClick={() => deleteItem("users", user.userId, "User")}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "companies" && (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Company name</th>
                  <th>Status</th>
                  <th>Subscription ID</th>
                  <th>Subscription start</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {companies.map((company, index) => (
                  <tr key={company.companyId}>
                    <td>{company.companyId}</td>
                    <td>
                      <input
                        value={company.companyName || ""}
                        onChange={(e) => updateCompanyField(index, "companyName", e.target.value)}
                      />
                    </td>
                    <td>
                      <select
                        value={company.isActive ? "active" : "inactive"}
                        onChange={(e) =>
                          updateCompanyField(index, "isActive", e.target.value === "active")
                        }
                      >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                      </select>
                    </td>
                    <td>
                      <input
                        type="number"
                        value={company.subscriptionId ?? ""}
                        onChange={(e) => updateCompanyField(index, "subscriptionId", e.target.value)}
                      />
                    </td>
                    <td>{company.subscriptionStartDate || "-"}</td>
                    <td className="admin-actions-cell">
                      <button type="button" className="light-button" onClick={() => saveCompany(company)}>
                        Save
                      </button>
                      <button
                        type="button"
                        className="danger-button"
                        onClick={() => deleteItem("companies", company.companyId, "Company")}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "subscriptions" && (
          <>
            {showAddSubscription && (
              <div className="add-subscription-box">
                <h3>Add new subscription</h3>

                <div className="add-subscription-grid">
                  <input
                    placeholder="Subscription name"
                    value={newSubscription.subscriptionName}
                    onChange={(e) => updateNewSubscriptionField("subscriptionName", e.target.value)}
                  />
                  <input
                    type="number"
                    placeholder="Duration days"
                    value={newSubscription.durationDays}
                    onChange={(e) => updateNewSubscriptionField("durationDays", e.target.value)}
                  />
                  <input
                    type="number"
                    placeholder="Priority"
                    value={newSubscription.priority}
                    onChange={(e) => updateNewSubscriptionField("priority", e.target.value)}
                  />
                  <input
                    type="number"
                    placeholder="Price"
                    value={newSubscription.price}
                    onChange={(e) => updateNewSubscriptionField("price", e.target.value)}
                  />
                  <input
                    placeholder="Description"
                    value={newSubscription.description}
                    onChange={(e) => updateNewSubscriptionField("description", e.target.value)}
                  />
                  <select
                    value={newSubscription.subscriptionType}
                    onChange={(e) => updateNewSubscriptionField("subscriptionType", e.target.value)}
                  >
                    <option value="Customer">Customer</option>
                    <option value="Company">Company</option>
                  </select>
                  <select
                    value={newSubscription.isActive ? "active" : "inactive"}
                    onChange={(e) => updateNewSubscriptionField("isActive", e.target.value === "active")}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>

                <button type="button" className="primary-button" onClick={addSubscription}>
                  Save new subscription
                </button>
              </div>
            )}

            <div className="admin-table-wrapper">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Days</th>
                    <th>Priority</th>
                    <th>Price</th>
                    <th>Description</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {subscriptions.map((subscription, index) => (
                    <tr key={subscription.subscriptionId}>
                      <td>{subscription.subscriptionId}</td>
                      <td>
                        <input
                          value={subscription.subscriptionName || ""}
                          onChange={(e) =>
                            updateSubscriptionField(index, "subscriptionName", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          value={subscription.durationDays ?? ""}
                          onChange={(e) =>
                            updateSubscriptionField(index, "durationDays", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          value={subscription.priority ?? ""}
                          onChange={(e) =>
                            updateSubscriptionField(index, "priority", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          type="number"
                          value={subscription.price ?? ""}
                          onChange={(e) =>
                            updateSubscriptionField(index, "price", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <input
                          value={subscription.description || ""}
                          onChange={(e) =>
                            updateSubscriptionField(index, "description", e.target.value)
                          }
                        />
                      </td>
                      <td>
                        <select
                          value={subscription.subscriptionType || "Customer"}
                          onChange={(e) =>
                            updateSubscriptionField(index, "subscriptionType", e.target.value)
                          }
                        >
                          <option value="Customer">Customer</option>
                          <option value="Company">Company</option>
                        </select>
                      </td>
                      <td>
                        <select
                          value={subscription.isActive ? "active" : "inactive"}
                          onChange={(e) =>
                            updateSubscriptionField(index, "isActive", e.target.value === "active")
                          }
                        >
                          <option value="active">Active</option>
                          <option value="inactive">Inactive</option>
                        </select>
                      </td>
                      <td className="admin-actions-cell">
                        <button
                          type="button"
                          className="light-button"
                          onClick={() => saveSubscription(subscription)}
                        >
                          Save
                        </button>
                        <button
                          type="button"
                          className="danger-button"
                          onClick={() =>
                            deleteItem(
                              "subscriptions",
                              subscription.subscriptionId,
                              "Subscription"
                            )
                          }
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

