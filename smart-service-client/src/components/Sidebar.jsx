import React from "react";

// Left sidebar showing the user's profile, plan, and conversation history list
export default function Sidebar({
  user,
  selectedPlan,
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onLogout,
  onOpenProfile,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <div className="user-profile-box">
          <div className="user-avatar">
            {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
          </div>

          <div className="user-details">
            <strong>{user?.name || "User"}</strong>
            <span>{user?.role || "user"}</span>
          </div>

          <button
            type="button"
            className="profile-icon-button"
            onClick={onOpenProfile}
            title="Profile"
          >
            Profile
          </button>
        </div>

        <button type="button" className="logout-button" onClick={onLogout}>
          Logout
        </button>

        <button type="button" className="new-chat-button" onClick={onNewChat}>
          + New chat
        </button>

        {selectedPlan && (
          <div className="sidebar-user-plan">
            <strong>{selectedPlan.name}</strong>
            <span>{selectedPlan.price} ₪</span>
          </div>
        )}

        <div className="history-title">Conversation history</div>
      </div>

      <div className="chat-list">
        {chats.map((chat) => (
          <button
            key={chat.id}
            type="button"
            className={`chat-history-item ${
              activeChatId === chat.id ? "active" : ""
            }`}
            onClick={() => onSelectChat(chat.id)}
          >
            <span className="chat-title">{chat.title}</span>
            <span className="chat-date">{chat.date}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}