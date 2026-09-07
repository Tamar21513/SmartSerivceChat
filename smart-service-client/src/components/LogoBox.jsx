import React from "react";

// Renders the robot-head logo icon, optionally in a smaller size
export default function LogoBox({ small = false }) {
  return (
    <div className={small ? "logo-box small" : "logo-box"}>
      <div className="robot-head">
        <span />
        <span />
      </div>
    </div>
  );
}