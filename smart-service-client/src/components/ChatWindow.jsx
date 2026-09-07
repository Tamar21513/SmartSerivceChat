import React from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

// Displays the active chat's header, message list, and input box
export default function ChatWindow({
  chat,
  onSendMessage,
  onSendAudioMessage,
}) {
  return (
    <main className="chat-window">
      <header className="chat-header">
        <div>
          <h2>{chat?.title}</h2>
          <p>Smart customer service in real time</p>
        </div>

        <span className="status-pill">● Online</span>
      </header>

      <section className="messages-area">
        {chat?.messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </section>

      <ChatInput
        onSendMessage={onSendMessage}
        onSendAudioMessage={onSendAudioMessage}
      />
    </main>
  );
}