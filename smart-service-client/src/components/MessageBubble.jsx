import React from "react";

// Cleans up raw bot text by stripping "answer"/"ending" labels and normalizing line breaks
function formatBotMessage(text) {
  if (!text) return "";

  return String(text)
    .replace(/\r\n/g, "\n")
    .replace(/^\s*["']?answer["']?\s*:\s*/i, "")
    .replace(/\s*["']?ending["']?\s*:\s*/i, "\n\n")
    .trim();
}

// Renders a single chat message bubble (text or audio) for user or bot
export default function MessageBubble({ message }) {
  const isUser = message.sender === "user";

  const messageText = isUser
    ? message.text
    : formatBotMessage(message.text);

  return (
    <div
      className={`message-row ${isUser ? "user-message" : "bot-message"}`}
      dir="ltr"
    >
      <div className="message-bubble">
        {message.type === "audio" ? (
          <div className="audio-message">
            <strong>Voice message</strong>
            <audio controls src={message.audioUrl} />
            <span>{message.fileName}</span>
          </div>
        ) : (
          messageText
        )}
      </div>
    </div>
  );
}