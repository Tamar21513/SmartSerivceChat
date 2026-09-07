# SmartService Chat

An intelligent customer-service chat system that combines Natural Language
Processing (NLP) and data analysis to give customers fast, accurate, and
personalized answers instead of routing them through generic support flows.

A user's free-form question is classified into one of 12 supported inquiry
types (price, order status, payment, complaint, technical issue, ...), turned
into a structured, type-specific search query, matched against a company's
knowledge base, and answered in natural language — while keeping track of
conversation history for follow-up questions.

## Repository structure

This is a monorepo containing all three parts of the system:

| Path | What it is |
|---|---|
| [`Felis_API/`](Felis_API) | C# / ASP.NET (.NET 8) API server — users, companies, subscriptions and reports. Talks to the SQL database. |
| [`Felis_python/`](Felis_python) | The NLP / machine-learning layer — question classification, JSON-structure building, data extraction, semantic search, answer generation, and speech-to-text/text-to-speech. |
| [`smart-service-client/`](smart-service-client) | React (Vite) front-end client. |
| [`database/`](database) | SQL Server database schema (`UserDB.sql`). |
| [`docs/`](docs) | Project book, summary presentation and logo assets. |

## Architecture

The system follows a layered client-server design:

```
Client (React) → Communication layer (HTTP/HTTPS) → Processing layer
    → NLP / ML layer → Database layer
```

1. The client sends a text or voice question.
2. The processing layer cleans the text, classifies it into one of 12 inquiry
   types, and builds a type-specific JSON structure from it.
3. The NLP layer computes embeddings, searches the company's knowledge base
   for the most relevant content, and extracts a focused answer.
4. A natural-language response is generated and returned to the client; the
   conversation is summarized and persisted to the database.

Key ML models used: **SetFit** (question-type classification), **FLAN-T5-LARGE**
(structured JSON extraction / answer generation), **DistilBERT** (focused
answer extraction from retrieved text), and sentence-embedding models for
semantic similarity search.

## Security

- Passwords are hashed with **Argon2** (never stored as plain text).
- Client-server communication runs over **HTTPS**.
- Access to the database only happens through the server — the client never
  talks to it directly.

## Running locally

Each sub-project manages its own dependencies:

**API** (`Felis_API/`) — open `Felis_API.csproj` in Visual Studio / JetBrains
Rider, or run:
```bash
dotnet run --project Felis_API
```
Update the connection string in `Felis_API/appsettings.json` to point at your
own SQL Server instance, and create the schema from `database/UserDB.sql`.

**ML service** (`Felis_python/`):
```bash
cd Felis_python
pip install -r requirements.txt
```

**Client** (`smart-service-client/`):
```bash
cd smart-service-client
npm install
cp .env.example .env   # fill in the required values (e.g. Google OAuth client ID)
npm run dev
```

## Documentation

The full project book (architecture, requirements analysis, UML diagrams,
database design, and more) is available at
[`docs/project-book.pdf`](docs/project-book.pdf).
