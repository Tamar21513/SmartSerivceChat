import React from "react";

// Renders the app logo image, optionally in a smaller size
export default function LogoImage({ small = false }) {
  return (
    <img
      className={small ? "logo-image small" : "logo-image"}
      src="/logo.png"
    />
  );
}