# Viola AI Assistant

Viola is an AI assistant designed to provide helpful information and complete tasks through natural language conversations. It is built using LangChain and modular dialog management, with context awareness and web-enabled task handling.

## Features

- Conversational AI agent built with LangChain `create_agent`
- Context-aware dialogue using LangGraph's checkpointer and stable thread IDs
- Modular separation of agent logic, dialogue management, prompts, memory, tools, and app entry point
- Web search support through Tavily when `TAVILY_API_KEY` is configured
- DuckDuckGo web search fallback for local experimentation
- Task execution tools for scheduling meetings, managing tasks, and checking local time
- CLI interface for quick local use
- Environment variable support via `.env`
- Tests and GitHub Actions workflow for repository hygiene

## Project Structure

```text
viola-ai-assistant/
|-- .env.example
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- .gitignore
|-- LICENSE
|-- README.md
|-- pyproject.toml
|-- requirements.txt
|-- src/
|   `-- viola/
|       |-- __init__.py
|       |-- __main__.py
|       |-- app.py
|       |-- config.py
|       |-- agent/
|       |   |-- __init__.py
|       |   `-- viola_agent.py
|       |-- dialogue/
|       |   |-- __init__.py
|       |   `-- manager.py
|       |-- memory/
|       |   |-- __init__.py
|       |   `-- context.py
|       |-- prompts/
|       |   |-- __init__.py
|       |   |-- examples.py
|       |   `-- system.py
|       `-- tools/
|           |-- __init__.py
|           |-- registry.py
|           |-- task_store.py
|           |-- tasks.py
|           |-- time.py
|           `-- web_search.py
`-- tests/
    |-- test_config.py
    |-- test_prompt.py
    `-- test_task_store.py
```

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

If you prefer a plain requirements file:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at least:

```env
OPENAI_API_KEY=sk-your-openai-api-key
```

For higher quality web search, also set:

```env
TAVILY_API_KEY=tvly-your-tavily-api-key
```

## Run

Interactive CLI:

```bash
viola
```

Or:

```bash
python -m viola
```

Send one message and exit:

```bash
viola --message "Find the latest LangChain agent documentation and summarize it."
```

Resume a prior in-memory conversation thread during the same process:

```bash
viola --thread-id my-local-thread
```

## Example Prompts

- "Remember that I prefer concise status updates. What can you help me with today?"
- "Search the web for current AI assistant design patterns and summarize the top three."
- "Schedule a meeting called Product Sync tomorrow at 10:00 for 45 minutes with Mira and Dev."
- "Create a high-priority task to review the Q3 roadmap by Friday."
- "What meetings do I have on 2026-06-03?"
- "What time is it in Asia/Calcutta?"
- "Using what we discussed earlier, draft a short follow-up message."

## Environment Variables

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes for OpenAI models | None | API key for OpenAI chat models |
| `VIOLA_MODEL` | No | `openai:gpt-4.1-mini` | LangChain model identifier |
| `VIOLA_TEMPERATURE` | No | `0.3` | Model creativity level |
| `VIOLA_MAX_RETRIES` | No | `6` | Provider retry count |
| `VIOLA_REQUEST_TIMEOUT` | No | `60` | Model request timeout in seconds |
| `VIOLA_DEFAULT_TIMEZONE` | No | `Asia/Calcutta` | Default timezone for date and time tools |
| `VIOLA_DATA_DIR` | No | `.viola_data` | Local JSON store for meetings and tasks |
| `TAVILY_API_KEY` | No | None | Enables Tavily-powered web search |
| `VIOLA_TAVILY_MAX_RESULTS` | No | `5` | Web search result count |
| `LANGSMITH_TRACING` | No | `false` | Enables LangSmith tracing when configured |

## Development

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Format imports and code:

```bash
ruff check . --fix
ruff format .
```

## Notes

- The meeting and task tools intentionally use local JSON storage. That keeps the project simple and safe while leaving a clear extension point for Google Calendar, Outlook, Notion, or a database.
- LangChain model identifiers are provider-flexible. For non-OpenAI providers, install the relevant LangChain integration package and set `VIOLA_MODEL` accordingly.
- The implementation follows current LangChain documentation for agents, chat model initialization, and Tavily search integration:
  - https://docs.langchain.com/oss/python/langchain/agents
  - https://docs.langchain.com/oss/python/langchain/models
  - https://docs.langchain.com/oss/python/integrations/tools/tavily_search
