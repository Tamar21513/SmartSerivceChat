import 'dotenv/config';
import OpenAI from "openai";

// בדיקה שהמפתח קיים
if (!process.env.OPENAI_API_KEY) {
  console.error("API key is missing. Check your .env file.");
  process.exit(1);
}

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

try {
  const response = await client.responses.create({
    model: "gpt-4.1-mini",   // מודל יציב וזול יותר
    input: "What was a positive news story from today?"
  });

  console.log(response.output_text);

} catch (err) {
  console.error("Status:", err.status);
  console.error("Type:", err.type);
  console.error("Message:", err.message);
}