
import React, { useEffect, useMemo, useState } from "react";

const API_BASE_URL = "http://localhost:5199";

// Screen for a company to configure its database, categories, and knowledge source
export default function CompanyDatabaseSetup({
  user,
  selectedPlan,
  onLogout,
  onFinish,
  onComplete,
}) {
  const companyId = user?.id || user?.companyId;

  const [companyName, setCompanyName] = useState(
    user?.name || user?.companyName || ""
  );
  const [companyWebsite, setCompanyWebsite] = useState("");
  const [supportEmail, setSupportEmail] = useState("");
  const [knowledgeSource, setKnowledgeSource] = useState("");
  const [additionalNotes, setAdditionalNotes] = useState("");

  const [categories, setCategories] = useState([]);
  const [selectedCategoryIds, setSelectedCategoryIds] = useState([]);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [showCategoriesPage, setShowCategoriesPage] = useState(false);

  const [loadingCategories, setLoadingCategories] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [successScreen, setSuccessScreen] = useState(false);

  const planName =
    user?.subscriptionName ||
    selectedPlan?.subscriptionName ||
    selectedPlan?.name ||
    "Not selected";

  const planPriority =
    user?.priority ||
    user?.subscriptionPriority ||
    selectedPlan?.priority ||
    "-";

  const selectedCategoriesText = useMemo(() => {
    if (selectedCategoryIds.length === 0) {
      return "No categories selected";
    }

    if (selectedCategoryIds.length === 1) {
      return "1 category selected";
    }

    return `${selectedCategoryIds.length} categories selected`;
  }, [selectedCategoryIds]);

  useEffect(() => {
    loadCategories();
    loadCompanyCategories();
    loadCompanyData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetches the full list of available categories from the API
  const loadCategories = async () => {
    try {
      setLoadingCategories(true);
      setMessage("");

      const response = await fetch(`${API_BASE_URL}/api/categories`);

      if (!response.ok) {
        throw new Error("Could not load categories.");
      }

      const data = await response.json();

      if (Array.isArray(data)) {
        setCategories(data);
      } else {
        setCategories([]);
      }
    } catch (error) {
      console.error(error);
      setMessage("Could not load categories.");
    } finally {
      setLoadingCategories(false);
    }
  };

  // Fetches the categories already assigned to this company and preselects them
  const loadCompanyCategories = async () => {
    if (!companyId) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/categories/company/${companyId}`
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      if (Array.isArray(data)) {
        const ids = data
          .map((item) => item.categoryId)
          .filter((id) => typeof id === "number");

        setSelectedCategoryIds(ids);
      }
    } catch (error) {
      console.error(error);
    }
  };

  // Fetches previously saved company database details and fills the form fields
  const loadCompanyData = async () => {
    if (!companyId) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/CompanyData/${companyId}`
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      if (data) {
        setCompanyName(
          data.companyName ||
            data.company_name ||
            user?.name ||
            user?.companyName ||
            ""
        );

        setCompanyWebsite(data.companyWebsite || data.website || "");
        setSupportEmail(data.supportEmail || data.support_email || "");

        setKnowledgeSource(
          data.knowledgeSource ||
            data.knowledge_source ||
            data.content ||
            ""
        );

        setAdditionalNotes(
          data.additionalNotes ||
            data.notes ||
            data.topic ||
            ""
        );
      }
    } catch (error) {
      console.error(error);
    }
  };

  // Adds or removes a category id from the selected categories list
  const toggleCategory = (categoryId) => {
    setSelectedCategoryIds((prev) => {
      if (prev.includes(categoryId)) {
        return prev.filter((id) => id !== categoryId);
      }

      return [...prev, categoryId];
    });
  };

  // Creates a new category via the API and selects it
  const addCategory = async () => {
    const cleanName = newCategoryName.trim();

    if (!cleanName) {
      return;
    }

    try {
      setMessage("");

      const response = await fetch(`${API_BASE_URL}/api/categories`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          categoryName: cleanName,
        }),
      });

      if (!response.ok) {
        throw new Error("Could not add category.");
      }

      const addedCategory = await response.json();

      setCategories((prev) => {
        const exists = prev.some(
          (category) => category.categoryId === addedCategory.categoryId
        );

        if (exists) {
          return prev;
        }

        return [...prev, addedCategory];
      });

      setSelectedCategoryIds((prev) => {
        if (prev.includes(addedCategory.categoryId)) {
          return prev;
        }

        return [...prev, addedCategory.categoryId];
      });

      setNewCategoryName("");
      setMessage("Category added successfully.");
    } catch (error) {
      console.error(error);
      setMessage("Could not add category.");
    }
  };

  // Saves the currently selected category ids for this company
  const saveCompanyCategories = async () => {
    if (!companyId) {
      throw new Error("Company id is missing.");
    }

    const response = await fetch(
      `${API_BASE_URL}/api/categories/company/${companyId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          categoryIds: selectedCategoryIds,
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Could not save company categories.");
    }

    return await response.json();
  };

  // Validates required fields and saves the company's database info to the API
  const saveCompanyDatabase = async () => {
    if (!companyId) {
      throw new Error("Company id is missing.");
    }

    const cleanCompanyName = companyName.trim();

    if (!cleanCompanyName) {
      throw new Error("Company name is required.");
    }

    if (!knowledgeSource.trim()) {
      throw new Error("Knowledge source is required.");
    }

    const payload = {
      companyId: companyId,
      companyName: cleanCompanyName,
      title: cleanCompanyName,

      companyWebsite: companyWebsite.trim(),
      supportEmail: supportEmail.trim(),
      knowledgeSource: knowledgeSource.trim(),

      additionalNotes: additionalNotes.trim(),
      topic: additionalNotes.trim(),
    };

    const response = await fetch(`${API_BASE_URL}/api/CompanyData`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Could not save company database.");
    }

    return await response.json();
  };

  // Handles the setup form submit: saves the database and categories, then shows success
  const handleSave = async (event) => {
    event.preventDefault();
  
    try {
      setSaving(true);
      setMessage("");
    
      await saveCompanyDatabase();
      await saveCompanyCategories();
    
      setSuccessScreen(true);
    
      if (typeof onFinish === "function") {
        onFinish();
      }
    } catch (error) {
      console.error(error);
      setMessage(error.message || "Could not save company database.");
    } finally {
      setSaving(false);
    }
  };

  if (successScreen) {
    return (
      <div className="database-page">
        <div className="success-screen-card wide-success-card">
          <div className="success-icon">✓</div>
          <h2>נשמר בהצלחה</h2>
          <p>מסד הנתונים והקטגוריות של החברה נשמרו בהצלחה.</p>

          <button
            type="button"
            className="primary-button"
            onClick={() => setSuccessScreen(false)}
          >
            Back to company setup
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="database-page">
      <div className="database-shell">
        <div className="top-bar database-top-bar">
          <div className="top-logo">
            <img
              src="/logo.png"
              alt="Smart Service Chat"
              className="logo-image small"
            />

            <div>
              <strong>Company Area</strong>
              <span>Database and categories setup</span>
            </div>
          </div>

          <button type="button" className="logout-button" onClick={onLogout}>
            Logout
          </button>
        </div>

        <div className="database-card company-database-card">
          <div className="database-card-header">
            <div>
              <h1>Set up your company database</h1>

              <p className="database-plan-line">
                Selected plan: <strong>{planName}</strong> | Priority:{" "}
                <strong>{planPriority}</strong>
              </p>
            </div>

            <span className="database-status-pill">Company setup</span>
          </div>

          {message && <div className="database-error">{message}</div>}

          <form className="database-form" onSubmit={handleSave}>
            <label className="input-group">
              <span>Company name</span>
              <input
                type="text"
                value={companyName}
                onChange={(event) => setCompanyName(event.target.value)}
                placeholder="Company name"
              />
            </label>

            <label className="input-group">
              <span>Company website</span>
              <input
                type="text"
                value={companyWebsite}
                onChange={(event) => setCompanyWebsite(event.target.value)}
                placeholder="https://example.com"
              />
            </label>

            <label className="input-group">
              <span>Support email</span>
              <input
                type="email"
                value={supportEmail}
                onChange={(event) => setSupportEmail(event.target.value)}
                placeholder="support@example.com"
              />
            </label>

            <label className="input-group">
              <span>Knowledge source</span>
              <textarea
                className="large-textarea"
                value={knowledgeSource}
                onChange={(event) => setKnowledgeSource(event.target.value)}
                placeholder="Enter company information, links, FAQs, service policy, product details, and any text the bot should use."
              />
            </label>

            <label className="input-group">
              <span>Additional notes</span>
              <textarea
                className="large-textarea"
                value={additionalNotes}
                onChange={(event) => setAdditionalNotes(event.target.value)}
                placeholder="Optional notes for the chatbot."
              />
            </label>

            <div className="categories-section">
              <div className="categories-summary-card">
                <div>
                  <h2>Company categories</h2>

                  <p>
                    Select the categories this company belongs to. Priority is
                    filled automatically by the company subscription.
                  </p>

                  <div className="selected-categories-preview">
                    <span>{selectedCategoriesText}</span>
                  </div>
                </div>

                <button
                  type="button"
                  className="open-categories-button"
                  onClick={() => setShowCategoriesPage(true)}
                >
                  Choose categories
                </button>
              </div>

              {showCategoriesPage && (
                <div className="categories-modal-overlay">
                  <div className="categories-modal">
                    <div className="categories-modal-header">
                      <div>
                        <h2>Choose company categories</h2>

                        <p>
                          The priority is automatic according to the company
                          subscription.
                        </p>
                      </div>

                      <button
                        type="button"
                        className="close-categories-button"
                        onClick={() => setShowCategoriesPage(false)}
                      >
                        ×
                      </button>
                    </div>

                    <div className="category-add-row modal-add-row">
                      <input
                        type="text"
                        value={newCategoryName}
                        onChange={(event) =>
                          setNewCategoryName(event.target.value)
                        }
                        placeholder="Add new category"
                      />

                      <button
                        type="button"
                        className="add-category-button"
                        onClick={addCategory}
                      >
                        Add category
                      </button>
                    </div>

                    {loadingCategories ? (
                      <div className="empty-categories-message">
                        Loading categories...
                      </div>
                    ) : categories.length === 0 ? (
                      <div className="empty-categories-message">
                        No categories found. Check the C# API endpoint /api/categories.
                      </div>
                    ) : (
                      <div className="categories-grid colorful-categories-grid modal-categories-grid">
                        {categories.map((category, index) => {
                          const isSelected = selectedCategoryIds.includes(
                            category.categoryId
                          );

                          return (
                            <button
                              type="button"
                              key={category.categoryId}
                              className={`color-category-button category-color-${
                                index % 6
                              } ${isSelected ? "selected" : ""}`}
                              onClick={() =>
                                toggleCategory(category.categoryId)
                              }
                              title={category.categoryName}
                            >
                              <span className="category-check">
                                {isSelected ? "✓" : "+"}
                              </span>

                              <span className="category-name">
                                {category.categoryName}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    <div className="categories-modal-actions">
                      <button
                        type="button"
                        className="light-button"
                        onClick={() => setShowCategoriesPage(false)}
                      >
                        Cancel
                      </button>

                      <button
                        type="button"
                        className="primary-button done-categories-button"
                        onClick={() => setShowCategoriesPage(false)}
                      >
                        Done
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="database-actions">
              <button
                type="submit"
                className="primary-button update-database-button"
                disabled={saving}
              >
                {saving ? "Saving..." : "Save database"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
