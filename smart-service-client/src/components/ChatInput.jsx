import React, { useRef, useState } from "react";

// Text/voice message composer with recording controls for the chat window
export default function ChatInput({ onSendMessage, onSendAudioMessage }) {
  const [text, setText] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Sends the trimmed text input as a message and clears the field
  const sendText = () => {
    const cleanText = text.trim();

    if (!cleanText) {
      return;
    }

    onSendMessage(cleanText);
    setText("");
  };

  // Sends the message when Enter is pressed without Shift
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendText();
    }
  };

  // Requests microphone access and starts recording a voice message
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const mediaRecorder = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        const audioFile = new File(
          [audioBlob],
          `voice-message-${Date.now()}.webm`,
          { type: "audio/webm" }
        );

        onSendAudioMessage(audioFile);

        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      alert(
        "Microphone access is blocked. Please allow microphone permission in the browser."
      );
    }
  };

  // Stops the active recording and updates the recording state
  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  // Starts or stops recording depending on the current state
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <footer className="chat-input-box" dir="ltr">
      <button
        className={`record-button ${isRecording ? "recording" : ""}`}
        onClick={toggleRecording}
        title={isRecording ? "Stop recording" : "Record voice message"}
        type="button"
      >
        {isRecording ? "■" : "🎙"}
      </button>

      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        rows={1}
      />

      <button className="send-button" onClick={sendText} type="button">
        Send
      </button>
    </footer>
  );
}