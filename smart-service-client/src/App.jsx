import React, { useMemo, useState } from "react";
import "./App.css";

import AuthPage from "./components/AuthPage";
import CompanyDatabaseSetup from "./components/CompanyDatabaseSetup";
import AdminDashboard from "./components/AdminDashboard";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import UserProfileModal from "./components/UserProfileModal";

import { adminDefaultPlans } from "./data/plans";

const API_BASE_URL = "http://localhost:5199";
const PYTHON_API_BASE_URL = "http://localhost:8000";

// Builds the bot's opening greeting message for a new chat
function createWelcomeMessage(id = Date.now()) {
  return {
    id,
    sender: "bot",
    type: "text",
    text: "Hello, I am Smart Service Chat. How can I help you?",
  };
}

// Creates a fresh empty local chat (reportContent is empty since nothing is saved to SQL yet)
function createNewChat() {
  return {
    id: `local_${Date.now()}`,
    reportId: null,
    title: "New conversation",
    date: "Now",
    isNew: true,
    isHistory: false,
    isChanged: false,
    reportContent: "",
    messages: [createWelcomeMessage(1)],
  };
}

// Derives a chat title from the first "User:" line found in the report content
function getChatTitle(reportContent) {
  const content = reportContent || "";

  const firstUserLine = content
    .split("\n")
    .find((line) => line.trim().startsWith("User:"));

  if (!firstUserLine) {
    return "Previous conversation";
  }

  return firstUserLine.replace("User:", "").trim().slice(0, 32);
}

// Formats a server-provided timestamp into a localized date string
function formatReportDate(createdAt) {
  if (!createdAt) {
    return "";
  }

  return new Date(createdAt).toLocaleDateString();
}

// Parses the full report content text into an array of displayable chat messages
function parseReportContentToMessages(reportContent, reportId) {
  const content = reportContent || "";
  const lines = content.split("\n");
  const messages = [];

  let currentSender = null;
  let currentText = "";
  let messageIndex = 1;

  const numericReportId = Number(reportId) || Date.now();

  const saveCurrentMessage = () => {
    if (!currentSender || !currentText.trim()) {
      return;
    }

    messages.push({
      id: numericReportId * 1000 + messageIndex,
      sender: currentSender,
      type: "text",
      text: currentText.trim(),
    });

    messageIndex += 1;
    currentSender = null;
    currentText = "";
  };

  for (const line of lines) {
    const cleanLine = line.trim();

    if (!cleanLine) {
      continue;
    }

    if (cleanLine.startsWith("Topics in report:")) {
      saveCurrentMessage();
      break;
    }

    if (cleanLine.startsWith("Sentiment and Emotions:")) {
      saveCurrentMessage();
      break;
    }

    if (cleanLine.startsWith("Sentiment:")) {
      saveCurrentMessage();
      break;
    }

    if (cleanLine.startsWith("Emotions detected:")) {
      saveCurrentMessage();
      break;
    }

    if (cleanLine.startsWith("Transcript:")) {
      continue;
    }

    if (cleanLine.startsWith("User:")) {
      saveCurrentMessage();
      currentSender = "user";
      currentText = cleanLine.replace("User:", "").trim();
      continue;
    }

    if (cleanLine.startsWith("Bot:")) {
      saveCurrentMessage();
      currentSender = "bot";
      currentText = cleanLine.replace("Bot:", "").trim();
      continue;
    }

    if (currentSender) {
      currentText += ` ${cleanLine}`;
    }
  }

  saveCurrentMessage();

  if (messages.length === 0) {
    return [
      {
        id: numericReportId * 1000,
        sender: "bot",
        type: "text",
        text: "This conversation could not be displayed as chat messages.",
      },
    ];
  }

  return messages;
}

// Converts reports coming from the C# API into chat objects for React, keeping reportContent on each chat
function convertReportsToHistoryChats(reports) {
  return reports.map((report) => {
    const reportId = report.reportId ?? report.report_id ?? report.id ?? null;

    const reportContent =
      report.reportContent ??
      report.report_content ??
      report.ReportContent ??
      report.content ??
      "";

    const createdAt =
      report.createdAt ??
      report.created_at ??
      report.CreatedAt ??
      null;

    return {
      id: `report_${reportId}`,
      reportId,
      title: getChatTitle(reportContent),
      date: formatReportDate(createdAt),
      isHistory: true,
      isNew: false,
      isChanged: false,
      reportContent,
      messages: parseReportContentToMessages(reportContent, reportId),
    };
  });
}

// Builds a plain-text conversation array (for saving) from displayed chat messages
function buildConversationForSave(messages) {
  return messages
    .filter(
      (message) =>
        message.type === "text" &&
        (message.sender === "user" || message.sender === "bot") &&
        message.text?.trim()
    )
    .map((message) => {
      const prefix = message.sender === "user" ? "User" : "Bot";
      return `${prefix}: ${message.text.trim()}`;
    });
}

// Checks whether a chat contains at least one real (non-empty) user message
function hasRealUserMessage(chat) {
  return chat?.messages?.some(
    (message) => message.sender === "user" && message.text?.trim()
  );
}

// Converts raw "User:"/"Bot:" prefixed messages from Python into React message objects
function convertPythonMessagesToReactMessages(messages, chatId) {
  if (!Array.isArray(messages)) {
    return [];
  }

  return messages.map((message, index) => {
    const cleanMessage = String(message || "").trim();

    if (cleanMessage.startsWith("User:")) {
      return {
        id: `${chatId}_user_${index}`,
        sender: "user",
        type: "text",
        text: cleanMessage.replace("User:", "").trim(),
      };
    }

    if (cleanMessage.startsWith("Bot:")) {
      return {
        id: `${chatId}_bot_${index}`,
        sender: "bot",
        type: "text",
        text: cleanMessage.replace("Bot:", "").trim(),
      };
    }

    return {
      id: `${chatId}_message_${index}`,
      sender: "bot",
      type: "text",
      text: cleanMessage,
    };
  });
}

// Root app component: manages screens, chats, and sync between the C# and Python backends
export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [screen, setScreen] = useState("auth");

  const [selectedPlan, setSelectedPlan] = useState(null);
  const [plans, setPlans] = useState(adminDefaultPlans);

  const [companies, setCompanies] = useState([]);
  const [customers, setCustomers] = useState([]);

  const [chats, setChats] = useState([createNewChat()]);
  const [activeChatId, setActiveChatId] = useState(null);

  const [showProfile, setShowProfile] = useState(false);

  const activeChat = useMemo(() => {
    return chats.find((chat) => chat.id === activeChatId) || chats[0];
  }, [chats, activeChatId]);

  // Updates a chat's local state after it has been saved to SQL via Python/C#
  const updateChatAfterSave = (oldChatId, savedData) => {
    if (!savedData) {
      return;
    }

    setChats((prevChats) =>
      prevChats.map((chat) => {
        if (chat.id !== oldChatId) {
          return chat;
        }

        const savedReportId = savedData.reportId ?? chat.reportId;

        return {
          ...chat,
          id: savedReportId ? `report_${savedReportId}` : chat.id,
          reportId: savedReportId,
          isNew: false,
          isHistory: true,
          isChanged: false,
          date: savedData.createdAt
            ? formatReportDate(savedData.createdAt)
            : chat.date,
        };
      })
    );

    if (savedData.reportId && activeChatId === oldChatId) {
      setActiveChatId(`report_${savedData.reportId}`);
    }
  };

  // Sends chats to Python so they are kept in its internal store; reportContent is included so Python can build a topic tree
  const syncChatsToPython = async (chatsToSync, userId) => {
    try {
      const bodyToSend = {
        userId,
        chats: chatsToSync.map((chat) => ({
          chatId: chat.id,
          reportId: chat.reportId ?? null,
          title: chat.title ?? "New conversation",
          isChanged: chat.isChanged ?? false,
          conversation: buildConversationForSave(chat.messages ?? []),
          reportContent: chat.reportContent ?? "",
        })),
      };

      await fetch(`${PYTHON_API_BASE_URL}/sync-chats`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(bodyToSend),
      });
    } catch (error) {
      console.error("Sync chats to Python failed:", error);
    }
  };

  // Sends just one chat to Python (convenience wrapper around syncChatsToPython)
  const syncSingleChatToPython = async (chat, userId) => {
    if (!chat || !userId) {
      return;
    }

    await syncChatsToPython([chat], userId);
  };

  // Saves a chat only if it was changed and contains a real user message
  const saveChatIfChanged = async (chatId) => {
    const chatToSave = chats.find((chat) => chat.id === chatId);

    if (!chatToSave || !chatToSave.isChanged || !hasRealUserMessage(chatToSave)) {
      return null;
    }

    if (!currentUser?.id) {
      console.warn("Chat was not saved because user id is missing.");
      return null;
    }

    const response = await fetch(`${PYTHON_API_BASE_URL}/save-chat-if-changed`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        userId: currentUser.id,
        chatId: chatToSave.id,
        reportId: chatToSave.reportId,
        title: chatToSave.title,
        conversation: buildConversationForSave(chatToSave.messages),
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.warn("Python chat save failed:", errorText);
      return null;
    }

    const savedData = await response.json();

    updateChatAfterSave(chatId, savedData);

    return savedData;
  };

  // Saves every chat that has unsaved changes
  const saveAllChangedChats = async () => {
    if (!currentUser?.id) {
      return;
    }

    const changedChats = chats.filter(
      (chat) => chat.isChanged && hasRealUserMessage(chat)
    );

    for (const chat of changedChats) {
      try {
        await saveChatIfChanged(chat.id);
      } catch (error) {
        console.error("Save changed chat error:", error);
      }
    }
  };

  // Loads the user's reports from C# and converts them into history chats
  const loadUserReports = async (userId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/user/${userId}`);

      if (!response.ok) {
        throw new Error("Failed to load user reports.");
      }

      const reports = await response.json();

      const historyChats = convertReportsToHistoryChats(reports);
      const newChat = createNewChat();
      const allChats = [newChat, ...historyChats];

      setChats(allChats);
      setActiveChatId(newChat.id);

      await syncChatsToPython(allChats, userId);
    } catch (error) {
      console.error("Reports loading error:", error);

      const newChat = createNewChat();

      setChats([newChat]);
      setActiveChatId(newChat.id);

      await syncChatsToPython([newChat], userId);
    }
  };

  // Loads the user's "ThingsTheUserHas" data from C#
  const loadThingsTheUserHas = async (userId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/ThingsTheUserHas/user/${userId}`
      );

      if (!response.ok) {
        console.warn("ThingsTheUserHas was not loaded.");
        return;
      }

      await response.json();
    } catch (error) {
      console.error("ThingsTheUserHas loading error:", error);
    }
  };

  // Navigates to the correct screen (admin, company setup, or chat) based on user role
  const openScreenByRole = async (userData) => {
    const role = userData.role?.toLowerCase();

    if (role === "admin") {
      setScreen("admin");
      return;
    }

    if (role === "company") {
      setSelectedPlan(userData.plan || null);
      setScreen("company_database");
      return;
    }

    await loadUserReports(userData.id);
    await loadThingsTheUserHas(userData.id);

    setScreen("chat");
  };

  // Stores the logged-in user and opens the appropriate screen for them
  const handleLoginSuccess = async (userData) => {
    setCurrentUser(userData);
    localStorage.setItem("currentUser", JSON.stringify(userData));

    await openScreenByRole(userData);
  };

  // Stores the newly registered user, tracks them locally, and opens the right screen
  const handleRegisterSuccess = async (userData) => {
    setCurrentUser(userData);
    setSelectedPlan(userData.plan || null);
    localStorage.setItem("currentUser", JSON.stringify(userData));

    const role = userData.role?.toLowerCase();

    if (role === "company") {
      setCompanies((prev) => [
        ...prev,
        {
          id: userData.id,
          name: userData.name,
          email: userData.email,
          plan: userData.plan,
          databaseReady: false,
        },
      ]);

      setScreen("company_database");
      return;
    }

    setCustomers((prev) => [
      ...prev,
      {
        id: userData.id,
        name: userData.name,
        email: userData.email,
        plan: userData.plan,
      },
    ]);

    await openScreenByRole(userData);
  };

  // Updates the current user's stored details after a profile edit
  const handleUserUpdate = (updatedUser) => {
    setCurrentUser(updatedUser);
    localStorage.setItem("currentUser", JSON.stringify(updatedUser));
  };

  // Saves a company's database setup details to the C# API
  const handleDatabaseReady = async (databaseData) => {
    if (!databaseData) {
      return;
    }
  
    if (!currentUser?.id) {
      throw new Error("Company id was not found. Please login again.");
    }
  
    const companyName = databaseData.companyName?.trim();
  
    if (!companyName) {
      throw new Error("Company name is required.");
    }
  
    const response = await fetch(`${API_BASE_URL}/api/CompanyData`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        companyId: currentUser.id,
        companyName: companyName,
        title: companyName,
      
        companyWebsite: databaseData.website || databaseData.companyWebsite || "",
        supportEmail: databaseData.supportEmail || "",
        knowledgeSource: databaseData.knowledgeSource || "",
      
        additionalNotes: databaseData.notes || databaseData.additionalNotes || "",
        topic: databaseData.notes || databaseData.additionalNotes || "",
      }),
    });
  
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Failed to save company database.");
    }
  
    return await response.json();
  };

  // Switches the active chat: saves the current chat first, then syncs the newly selected one to Python
  const handleSelectChat = async (newChatId) => {
    if (newChatId === activeChatId) {
      return;
    }

    try {
      await saveChatIfChanged(activeChatId);
    } catch (error) {
      console.error("Save before switching chat failed:", error);
    }

    const selectedChat = chats.find((chat) => chat.id === newChatId);

    if (selectedChat && currentUser?.id) {
      await syncSingleChatToPython(selectedChat, currentUser.id);
    }

    setActiveChatId(newChatId);
  };

  // Saves the current chat if needed, then starts and selects a brand new chat
  const handleNewChat = async () => {
    try {
      await saveChatIfChanged(activeChatId);
    } catch (error) {
      console.error("Save before new chat failed:", error);
    }

    const newChat = createNewChat();

    newChat.messages = [
      {
        id: Date.now(),
        sender: "bot",
        type: "text",
        text: "A new conversation has started. Type a message or send a voice recording.",
      },
    ];

    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);

    if (currentUser?.id) {
      await syncSingleChatToPython(newChat, currentUser.id);
    }
  };

  // Saves changed chats, clears the session, and returns to the auth screen
  const handleLogout = async () => {
    await saveAllChangedChats();

    localStorage.removeItem("currentUser");
    setCurrentUser(null);
    setSelectedPlan(null);
    setShowProfile(false);

    const newChat = createNewChat();
    setChats([newChat]);
    setActiveChatId(newChat.id);
    setScreen("auth");
  };

  // Sends a text message to Python, adds it to the chat, and appends the returned bot reply
  const handleSendTextMessage = async (messageText) => {
    const cleanText = messageText.trim();

    if (!cleanText) {
      return;
    }

    const currentActiveChatId = activeChatId;

    const chatBeforeSend = chats.find(
      (chat) => chat.id === currentActiveChatId
    );

    const userMessage = {
      id: Date.now(),
      sender: "user",
      type: "text",
      text: cleanText,
    };

    setChats((prevChats) =>
      prevChats.map((chat) => {
        if (chat.id !== currentActiveChatId) {
          return chat;
        }

        return {
          ...chat,
          title:
            chat.title === "New conversation" ||
            chat.title === "First conversation"
              ? cleanText.slice(0, 28)
              : chat.title,
          isChanged: true,
          messages: [...chat.messages, userMessage],
        };
      })
    );

    try {
      const response = await fetch(`${PYTHON_API_BASE_URL}/chat-message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: currentUser?.id ?? 0,
          chatId: currentActiveChatId,
          reportId: chatBeforeSend?.reportId ?? null,
          nameUser: currentUser?.name ?? "",
          email: currentUser?.email ?? "",
          city: currentUser?.city ?? "",
          age: currentUser?.age ?? 0,
          occupation: currentUser?.occupation ?? "",
          role: currentUser?.role ?? "",
          message: cleanText,
        }),
      });

      const result = await response.json();

      const pythonMessages = Array.isArray(result.messages)
        ? convertPythonMessagesToReactMessages(
            result.messages,
            currentActiveChatId
          )
        : null;

      if (pythonMessages && pythonMessages.length > 0) {
        setChats((prevChats) =>
          prevChats.map((chat) => {
            if (chat.id !== currentActiveChatId) {
              return chat;
            }

            return {
              ...chat,
              title:
                chat.title === "New conversation" ||
                chat.title === "First conversation"
                  ? cleanText.slice(0, 28)
                  : chat.title,
              isChanged: true,
              messages: pythonMessages,
            };
          })
        );

        return;
      }

      const botMessage = {
        id: Date.now() + 1,
        sender: "bot",
        type: "text",
        text:
          result.answer ||
          "I received your message, but Python did not return an answer.",
      };

      setChats((prevChats) =>
        prevChats.map((chat) => {
          if (chat.id !== currentActiveChatId) {
            return chat;
          }

          return {
            ...chat,
            isChanged: true,
            messages: [...chat.messages, botMessage],
          };
        })
      );
    } catch (error) {
      console.error("Python API error:", error);

      const errorMessage = {
        id: Date.now() + 1,
        sender: "bot",
        type: "text",
        text: "Could not connect to the Python server.",
      };

      setChats((prevChats) =>
        prevChats.map((chat) => {
          if (chat.id !== currentActiveChatId) {
            return chat;
          }

          return {
            ...chat,
            isChanged: true,
            messages: [...chat.messages, errorMessage],
          };
        })
      );
    }
  };

  // Adds a recorded audio message to the active chat as a local message
  const handleSendAudioMessage = (audioFile) => {
    if (!audioFile) {
      return;
    }

    addMessage({
      sender: "user",
      type: "audio",
      audioUrl: URL.createObjectURL(audioFile),
      fileName: audioFile.name,
    });
  };

  // Appends a local message plus a placeholder bot reply to the active chat
  const addMessage = (message) => {
    setChats((prevChats) =>
      prevChats.map((chat) => {
        if (chat.id !== activeChatId) {
          return chat;
        }

        const userMessage = {
          id: Date.now(),
          ...message,
        };

        const botMessage = {
          id: Date.now() + 1,
          sender: "bot",
          type: "text",
          text:
            message.type === "audio"
              ? "I received your audio file. Later, it will be sent to the server for processing."
              : "I received your message. Later, this will be connected to your Python/FastAPI server.",
        };

        return {
          ...chat,
          title:
            chat.title === "New conversation" ||
            chat.title === "First conversation"
              ? message.type === "audio"
                ? "Voice message"
                : message.text.slice(0, 28)
              : chat.title,
          isChanged: true,
          messages: [...chat.messages, userMessage, botMessage],
        };
      })
    );
  };

  if (screen === "auth") {
    return (
      <AuthPage
        onLoginSuccess={handleLoginSuccess}
        onRegisterSuccess={handleRegisterSuccess}
      />
    );
  }

  if (screen === "company_database") {
    return (
      <CompanyDatabaseSetup
        user={currentUser}
        selectedPlan={selectedPlan}
        onComplete={handleDatabaseReady}
        onLogout={handleLogout}
      />
    );
  }

  if (screen === "admin") {
    return (
      <AdminDashboard
        plans={plans}
        setPlans={setPlans}
        companies={companies}
        customers={customers}
        onLogout={handleLogout}
      />
    );
  }

  return (
    <div className="app" dir="ltr">
      <Sidebar
        user={currentUser}
        selectedPlan={selectedPlan}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onLogout={handleLogout}
        onOpenProfile={() => setShowProfile(true)}
      />

      <ChatWindow
        chat={activeChat}
        onSendMessage={handleSendTextMessage}
        onSendAudioMessage={handleSendAudioMessage}
      />

      {showProfile && (
        <UserProfileModal
          user={currentUser}
          onClose={() => setShowProfile(false)}
          onUserUpdate={handleUserUpdate}
        />
      )}
    </div>
  );
}