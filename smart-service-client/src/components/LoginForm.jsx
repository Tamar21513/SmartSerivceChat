import React, { useState } from "react";
import InputField from "./InputField";

const API_BASE_URL = "http://localhost:5199";

// Login form supporting both customer and company account types
export default function LoginForm({ onLoginSuccess, onMoveToRegister }) {
  const [accountType, setAccountType] = useState("customer");

  const [formData, setFormData] = useState({
    mailOrUsername: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Validates credentials, calls the login API, and reports the signed-in user
  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!formData.mailOrUsername || !formData.password) {
      setError("Please enter email/username and password.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mailOrUsername: formData.mailOrUsername,
          password: formData.password,
          accountType: accountType,
        }),
      });

      const data = await response.json();

      if (!response.ok || data.success !== true) {
        setError(data.message || "Login failed.");
        return;
      }

      const user = data.user;

      localStorage.setItem("currentUser", JSON.stringify(user));

      onLoginSuccess({
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        userType: user.userType,
        city: user.city,
        age: user.age,
        occupation: user.occupation,
        subscriptionId: user.subscriptionId,
      });
    } catch (error) {
      console.error("Login error:", error);
      setError("Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form-card">
      <div className="form-title"></div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="account-type-tabs">
          <button
            type="button"
            className={accountType === "customer" ? "active" : ""}
            onClick={() => setAccountType("customer")}
          >
            Customer
          </button>

          <button
            type="button"
            className={accountType === "company" ? "active" : ""}
            onClick={() => setAccountType("company")}
          >
            Company
          </button>
        </div>

        <InputField
          label={accountType === "company" ? "Company name" : "Email or username"}
          type="text"
          value={formData.mailOrUsername}
          placeholder={
            accountType === "company" ? "Company name" : "Email or username"
          }
          onChange={(value) =>
            setFormData({ ...formData, mailOrUsername: value })
          }
        />

        <InputField
          label="Password"
          type="password"
          value={formData.password}
          placeholder="Password"
          onChange={(value) => setFormData({ ...formData, password: value })}
        />

        {error && <p className="small-note">{error}</p>}

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <div className="auth-switch-box">
        <span>Don&apos;t have an account?</span>
        <button type="button" onClick={onMoveToRegister}>
          Create account
        </button>
      </div>
    </div>
  );
}