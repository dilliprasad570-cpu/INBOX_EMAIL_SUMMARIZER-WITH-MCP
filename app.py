from langchain.agents import create_agent
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from composio import Composio
import asyncio

checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}
model = ChatNVIDIA(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("NVIDIA_API_KEY"),
    temperature=1,
    top_p=1,
    max_completion_tokens=4096,
)
composio_key = os.getenv("COMPOSIO_API_KEY")
composio = Composio(api_key=composio_key)
server = composio.mcp.create(
    name="my-gmail-server",             # a name you choose
    toolkits=[{
        "toolkit": "Gmail",             # which toolkit to install
        "auth_config": "ac_Rm4UHZ7OxFsg" # your Tavily auth ID from Composio dashboard
    }],
    )

instance = composio.mcp.generate(
    user_id="pg-test-99fcc94c-9ce9-44d5-ad7a-75cee054d67f",
    mcp_config_id=server.id,
)

client = MultiServerMCPClient({
    "gmail": {
        "transport": "http",             # talks to the server over HTTP
        "url": instance["url"],          # the unique URL from Step 2
        "headers": {"x-api-key": composio_key},
    }
})

system_prompt="""You are an Email Inbox Summarizer & Draft Responder that helps users manage their Gmail inbox efficiently.
You have access to these Gmail tools:
- GMAIL_FETCH_EMAILS: Fetch emails from inbox (supports filters like unread, from, subject keywords)
- GMAIL_CREATE_DRAFT: Create a draft reply or new email
- GMAIL_MODIFY_LABELS: Add labels like "Urgent", "Follow Up" to emails
- GMAIL_LIST_LABELS: List all available labels in the account
- GMAIL_REPLY_TO_THREAD: Reply within an existing email thread
Your workflow:
1. First use GMAIL_FETCH_EMAILS to get the latest unread emails
2. Summarize each email in 1-2 lines
3. Categorize them into: URGENT, NEEDS REPLY, FYI/INFORMATIONAL
4. For emails that need a reply, use GMAIL_CREATE_DRAFT to draft a professional response
5. Optionally use GMAIL_MODIFY_LABELS to tag important emails
Present your summary in this format:
INBOX SUMMARY (X unread emails found)
URGENT
- [Sender] Subject — 1-line summary
  Draft reply: Created / Not needed
NEEDS REPLY
- [Sender] Subject — 1-line summary
  Draft reply: Created
FYI / INFORMATIONAL
- [Sender] Subject — 1-line summary
DRAFTS CREATED
- List of draft replies created with a preview of what was written
Don't use markdown format. Use plain text with clear sections and proper spacing."""

async def summarizer():
    """Fetch MCP tools, merge with local tools, and create the agent."""

    # ── MCP Step 3: FETCH tools from the remote server ─────
    # This reaches out to the Composio MCP server over HTTP,
    # asks "what tools do you have?", and gets back a list.
    # Each tool comes with a name, description, and input schema.
    # LangChain wraps them as Tool objects — identical to @tool functions.
    mcp_tools = await client.get_tools()

    # Merge remote MCP tools + local Python tools into one list.
    # The agent sees them all the same — it doesn't know which
    # ones are local and which are remote.
    all_tools = mcp_tools

    # Create the agent with the LLM, tools, prompt, and memory.
    return create_agent(
        model=model,
        tools=all_tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
    )

agent = asyncio.run(summarizer())

import gradio as gr
# ────────────────────────────────────────────────────────────
#  GRADIO UI — the web page the user sees
# ────────────────────────────────────────────────────────────

async def handle_query(query: str) -> str:
    """Pass the user's question to the agent and return the answer."""
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
    )
    return response["messages"][-1].content


demo = gr.Interface(
    fn=handle_query,
    inputs=gr.Textbox(lines=4, placeholder="Summarize and reply to my emails", label="Your Query"),
    outputs=gr.Textbox(lines=15, label="Agent Response"),
    title="🗺️ EMAIL summarizer Agent",
    description="Fetch, summarize, and draft replies for your unread Gmail messages.",
)

if __name__ == "__main__":
    demo.launch(debug=True)