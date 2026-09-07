import React, { useState } from "react";
import InputField from "./InputField";

const API_BASE_URL = "http://localhost:5199";

// Modal for viewing and editing the current user's profile details
export default function UserProfileModal({ user, onClose, onUserUpdate }) {
  const [formData, setFormData] = useState({
    name: user?.name || "",
    email: user?.email || "",
    city: user?.city || "",
    age: user?.age || 0,
    occupation: user?.occupation || "",
    role: user?.role || "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Submits the updated profile fields to the API and updates local user state
  const handleSave = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/api/users/${user.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          city: formData.city,
          age: Number(formData.age),
          occupation: formData.occupation,
          role: formData.role,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.message || "Failed to update user details.");
        return;
      }

      const updatedUser = {
        ...user,
        city: formData.city,
        age: Number(formData.age),
        occupation: formData.occupation,
      };

      localStorage.setItem("currentUser", JSON.stringify(updatedUser));
      onUserUpdate(updatedUser);
      onClose();
    } catch (error) {
      console.error(error);
      setError("Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-modal-overlay">
      <div className="profile-modal">
        <div className="profile-modal-header">
          <h2>User Profile</h2>
          <button type="button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="profile-form">
          <InputField
            label="Name"
            type="text"
            value={formData.name}
            disabled
            onChange={() => {}}
          />

          <InputField
            label="Email"
            type="email"
            value={formData.email}
            disabled
            onChange={() => {}}
          />

          <InputField
            label="Role"
            type="text"
            value={formData.role}
            disabled
            onChange={() => {}}
          />

          <InputField
            label="City"
            type="text"
            value={formData.city}
            placeholder="City"
            onChange={(value) => setFormData({ ...formData, city: value })}
          />

          <InputField
            label="Age"
            type="number"
            value={formData.age}
            placeholder="Age"
            onChange={(value) => setFormData({ ...formData, age: value })}
          />

          <InputField
            label="Occupation"
            type="text"
            value={formData.occupation}
            placeholder="Occupation"
            onChange={(value) =>
              setFormData({ ...formData, occupation: value })
            }
          />

          {error && <p className="small-note">{error}</p>}

          <div className="profile-actions">
            <button type="button" className="light-button" onClick={onClose}>
              Cancel
            </button>

            <button
              type="button"
              className="primary-button"
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? "Saving..." : "Save changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}