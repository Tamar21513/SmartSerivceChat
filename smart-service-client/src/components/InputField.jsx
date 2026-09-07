import React, { useState } from "react";

// Labeled input with an optional show/hide toggle for password fields
export default function InputField({
  label,
  type = "text",
  value,
  placeholder,
  onChange,
  disabled = false,
}) {
  const [showPassword, setShowPassword] = useState(false);

  const isPassword = type === "password";

  const inputType = isPassword && showPassword ? "text" : type;

  return (
    <label className="input-group">
      <span>{label}</span>

      <div className={isPassword ? "password-input-wrapper" : ""}>
        <input
          type={inputType}
          value={value}
          placeholder={placeholder}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
        />

        {isPassword && (
          <button
            type="button"
            className="password-toggle-button"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        )}
      </div>
    </label>
  );
}