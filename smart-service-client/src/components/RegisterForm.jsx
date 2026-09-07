
import React, { useEffect, useMemo, useState } from "react";
import InputField from "./InputField";
import PlanCard from "./PlanCard";
import PaymentForm from "./PaymentForm";

const API_BASE_URL = "http://localhost:5199";

// Formats a duration in days as a human-readable string (e.g. "1 month", "1 year")
function formatDuration(days) {
  if (days === 365) {
    return "1 year";
  }

  if (days % 30 === 0) {
    const months = days / 30;
    return months === 1 ? "1 month" : `${months} months`;
  }

  if (days === 1) {
    return "1 day";
  }

  return `${days} days`;
}

// Converts a raw subscription object from the API into the plan shape used by the UI
function mapSubscriptionToPlan(sub) {
  return {
    id: sub.subscriptionId,
    subscriptionId: sub.subscriptionId,
    name: sub.name,
    duration: formatDuration(sub.durationDays),
    durationDays: sub.durationDays,
    priority: sub.priority,
    price: sub.price,
    description: sub.description,
    subscriptionType: sub.subscriptionType,
    isActive: sub.isActive,
  };
}

// Registration form for creating a customer or company account with a subscription and payment
export default function RegisterForm({ onRegisterSuccess, onMoveToLogin }) {
  const [accountType, setAccountType] = useState("customer");

  const [companyPlans, setCompanyPlans] = useState([]);
  const [customerPlans, setCustomerPlans] = useState([]);

  const [selectedPlanId, setSelectedPlanId] = useState("");
  const [loadingPlans, setLoadingPlans] = useState(false);
  const [plansError, setPlansError] = useState("");

  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successUser, setSuccessUser] = useState(null);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [paymentData, setPaymentData] = useState({
    cardOwner: "",
    cardNumber: "",
    expiry: "",
    cvv: "",
  });

  const plans = useMemo(() => {
    return accountType === "company" ? companyPlans : customerPlans;
  }, [accountType, companyPlans, customerPlans]);

  const selectedPlan =
    plans.find((plan) => String(plan.id) === String(selectedPlanId)) ||
    plans[0];

  useEffect(() => {
    // Fetches active customer and company subscriptions and selects a default plan
    async function loadSubscriptions() {
      try {
        setLoadingPlans(true);
        setPlansError("");

        const [customerResponse, companyResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/api/subscriptions?type=Customer`),
          fetch(`${API_BASE_URL}/api/subscriptions?type=Company`),
        ]);

        if (!customerResponse.ok || !companyResponse.ok) {
          throw new Error("Failed to load subscriptions");
        }

        const customerData = await customerResponse.json();
        const companyData = await companyResponse.json();

        const fixedCustomerPlans = customerData.map(mapSubscriptionToPlan);
        const fixedCompanyPlans = companyData.map(mapSubscriptionToPlan);

        setCustomerPlans(fixedCustomerPlans);
        setCompanyPlans(fixedCompanyPlans);

        if (fixedCustomerPlans.length > 0) {
          setSelectedPlanId(fixedCustomerPlans[0].id);
        } else if (fixedCompanyPlans.length > 0) {
          setSelectedPlanId(fixedCompanyPlans[0].id);
        }
      } catch (error) {
        console.error(error);
        setPlansError("Could not load active subscriptions from the server.");
      } finally {
        setLoadingPlans(false);
      }
    }

    loadSubscriptions();
  }, []);

  // Switches the account type tab and resets the selected plan accordingly
  const handleAccountTypeChange = (type) => {
    setAccountType(type);
    setSubmitError("");

    if (type === "company") {
      setSelectedPlanId(companyPlans[0]?.id || "");
    } else {
      setSelectedPlanId(customerPlans[0]?.id || "");
    }
  };

  // Validates the registration form, submits it to the API, and stores the new user
  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitError("");

    if (!formData.name.trim() || !formData.password.trim()) {
      setSubmitError("Please enter name and password.");
      return;
    }

    if (accountType === "customer" && !formData.email.trim()) {
      setSubmitError("Please enter email for customer account.");
      return;
    }

    if (!selectedPlan) {
      setSubmitError("Please choose an active subscription.");
      return;
    }

    if (
      !paymentData.cardOwner ||
      !paymentData.cardNumber ||
      !paymentData.expiry ||
      !paymentData.cvv
    ) {
      setSubmitError("Please fill payment details.");
      return;
    }

    try {
      setSubmitting(true);

      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          accountType,
          name: formData.name.trim(),
          email: formData.email.trim(),
          password: formData.password,
          subscriptionId: Number(selectedPlan.subscriptionId),
        }),
      });

      const data = await response.json();

      if (!response.ok || data.success !== true) {
        setSubmitError(data.message || "Registration failed.");
        return;
      }

      let fixedUser;

      if (accountType === "company") {
        const company = data.company;

        fixedUser = {
          id: company.companyId,
          name: company.companyName,
          email: formData.email.trim(),
          role: "company",
          userType: "Company",
          city: "",
          age: 0,
          occupation: "",
          subscriptionId: company.subscriptionId,
          plan: selectedPlan,
          authProvider: "password",
        };
      } else {
        const user = data.user;

        fixedUser = {
          id: user.id,
          name: user.name,
          email: user.email || formData.email.trim(),
          role: user.role,
          userType: user.userType,
          city: user.city,
          age: user.age,
          occupation: user.occupation,
          subscriptionId: user.subscriptionId,
          plan: selectedPlan,
          authProvider: "password",
        };
      }

      localStorage.setItem("currentUser", JSON.stringify(fixedUser));
      setSuccessUser(fixedUser);
    } catch (error) {
      console.error("Register error:", error);
      setSubmitError("Could not connect to the server.");
    } finally {
      setSubmitting(false);
    }
  };

  if (successUser) {
    return (
      <div className="success-screen-card">
        <div className="success-icon">✓</div>
        <h2>נוסף בהצלחה</h2>
        <p>החשבון נשמר במערכת בהצלחה.</p>
        <button
          type="button"
          className="primary-button"
          onClick={() => onRegisterSuccess(successUser)}
        >
          Continue
        </button>
      </div>
    );
  }

  return (
    <div className="auth-form-card register-card">
      <div className="form-title"></div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="register-section">
          <h3>Account details</h3>

          <InputField
            label={accountType === "company" ? "Company name" : "Name"}
            type="text"
            value={formData.name}
            placeholder={accountType === "company" ? "Company name" : "Full name"}
            onChange={(value) => setFormData({ ...formData, name: value })}
          />

          <InputField
            label="Email"
            type="email"
            value={formData.email}
            placeholder="name@example.com"
            onChange={(value) => setFormData({ ...formData, email: value })}
          />

          <InputField
            label="Password"
            type="password"
            value={formData.password}
            placeholder="Choose a password"
            onChange={(value) => setFormData({ ...formData, password: value })}
          />
        </div>

        <div className="register-section">
          <h3>Subscription type</h3>

          <div className="account-type-tabs">
            <button
              type="button"
              className={accountType === "customer" ? "active" : ""}
              onClick={() => handleAccountTypeChange("customer")}
            >
              Customer
            </button>

            <button
              type="button"
              className={accountType === "company" ? "active" : ""}
              onClick={() => handleAccountTypeChange("company")}
            >
              Company
            </button>
          </div>

          {loadingPlans && <p className="small-note">Loading active subscriptions...</p>}

          {plansError && <p className="small-note">{plansError}</p>}

          {!loadingPlans && !plansError && plans.length === 0 && (
            <p className="small-note">No active subscriptions found.</p>
          )}

          <div className="register-plans-grid">
            {plans.map((plan) => (
              <PlanCard
                key={plan.id}
                plan={plan}
                selected={String(selectedPlan?.id) === String(plan.id)}
                onSelect={() => setSelectedPlanId(plan.id)}
              />
            ))}
          </div>
        </div>

        <div className="register-section">
          <h3>Payment details</h3>

          <p className="small-note">
            Payment details are used only for this transaction and are not saved in the system.
          </p>

          <PaymentForm paymentData={paymentData} setPaymentData={setPaymentData} />
        </div>

        {submitError && <p className="small-note">{submitError}</p>}

        <button className="primary-button" type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Create account"}
        </button>
      </form>

      <div className="auth-switch-box">
        <span>Already have an account?</span>
        <button type="button" onClick={onMoveToLogin}>
          Back to sign in
        </button>
      </div>
    </div>
  );
}

