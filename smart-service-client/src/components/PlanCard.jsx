import React from "react";

// Selectable card that displays a subscription plan's details
export default function PlanCard({ plan, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`plan-card ${selected ? "selected" : ""}`}
      onClick={onSelect}
    >
      <div className="plan-head">
        <h3>{plan.name}</h3>
        <span>₪{plan.price}</span>
      </div>

      <p>{plan.description}</p>

      <div className="plan-meta">
        <span>Duration: {plan.duration}</span>
        <span>Priority: {plan.priority}</span>
      </div>
    </button>
  );
}