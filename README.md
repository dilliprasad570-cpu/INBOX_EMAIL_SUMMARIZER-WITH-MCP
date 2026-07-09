# 📬 Email Inbox Summarizer Agent

> **Built with [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)** — the agent connects to Gmail via a remote MCP server hosted by [Composio](https://composio.dev), not through local API calls.

An AI-powered agent that fetches your unread Gmail emails, summarizes them, categorizes by priority, and drafts professional replies — all through a simple web UI.

## 🏗️ Architecture

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   Gradio Web UI │──────▶│  LangChain Agent │──────▶│  NVIDIA LLM     │
│  (localhost:7860)│       │  (create_agent)  │       │  (gpt-oss-120b) │
└─────────────────┘       └───────┬──────────┘       └─────────────────┘
                                  │
                          ┌───────▼──────────┐
                          │  MCP Client      │  ◀── What is this?
                          │  (HTTP transport) │      LangChain talks to the
                          └───────┬──────────┘      MCP server over HTTP to
                                  │                  discover & call tools.
                          ┌───────▼──────────┐
                          │  Composio MCP    │  ◀── Remote server that wraps
                          │  Server (cloud)  │      Gmail APIs as MCP tools.
                          └───────┬──────────┘      You never call Gmail
                                  │                  APIs directly.
                          ┌───────▼──────────┐
                          │   Gmail Inbox    │
                          └──────────────────┘
```

## ✨ What It Does

1. **Fetches** your latest unread emails from Gmail
2. **Summarizes** each email in 1–2 lines
3. **Categorizes** them: `URGENT` · `NEEDS REPLY` · `FYI/INFORMATIONAL`
4. **Drafts replies** for emails that need a response
5. **Labels emails** (optional) with tags like "Urgent" or "Follow Up"

## 📋 Prerequisites

| Requirement | Where to get it |
|-------------|----------------|
| Python 3.10+ | [python.org](https://www.python.org/downloads/) |
| NVIDIA API Key | [NVIDIA AI](https://build.nvidia.com/) |
| Composio API Key | [Composio Dashboard](https://app.composio.dev/) |
| Gmail connected in Composio | Composio Dashboard → Integrations → Gmail |

## 🚀 Setup

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd "Email Inbox Summarizer Agent"
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
COMPOSIO_API_KEY=your_composio_api_key_here
NVIDIA_API_KEY=your_nvidia_api_key_here
```

### 3. Update `app.py` with your Composio IDs

Open `app.py` and replace these placeholder values with your own:

```python
# Line 23 — MCP server name (pick any unique name)
name="my-gmail-server"

# Line 26 — Your Gmail auth config ID from Composio dashboard
"auth_config": "ac_XXXXXXXXXXXX"

# Line 31 — Your Composio user ID
user_id="your-user-id-here"
```

### 4. Run the agent

```bash
python app.py
```

Open **http://127.0.0.1:7860** in your browser and type a query like:
> "Summarize my unread emails and draft replies"

## 📁 Project Structure

```
Email Inbox Summarizer Agent/
├── app.py              # Main application (agent + Gradio UI)
├── .env                # API keys (do NOT commit this)
├── requirements.txt    # Python dependencies
└── README.md           # You are here
```

## 🔑 Key Concepts

- **MCP (Model Context Protocol)**: A standard that lets AI agents discover and use tools from remote servers. Instead of writing Gmail API code yourself, the Composio MCP server exposes Gmail actions as tools the agent can call.
- **Composio**: Hosts the MCP server in the cloud and handles Gmail OAuth for you.
- **LangChain Agent**: The AI brain that decides which tools to call and when, based on your query.
