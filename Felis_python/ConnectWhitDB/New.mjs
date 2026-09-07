import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // שמור את המפתח כמשתנה סביבה
});

const search_query =
  "List the latest OpenAI product launches in chronological order from latest to oldest in the past 2 years";

const response = await client.responses.create({
  model: "GPT-5 nano",
  input: search_query,
});

console.log(response.output_text);