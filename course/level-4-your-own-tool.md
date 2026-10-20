# Level 4: Build Your Own Tool

There's no tag for this level, because this one is yours. You take the Level 3 bot and connect it to something you actually care about. That's where it stops being a course project and starts being useful.

```bash
git checkout -b my-agent level-3
```

## Pick a tool

Take something you look up all the time at work, or just something you find fun. A few ideas:

- **Your job scheduler.** Airflow, Dagster or Prefect all have REST APIs. "Which DAGs failed last night?" is a super useful question to answer from Slack.
- **Your database.** A read-only query against Postgres or DuckDB. "How many orders did we get yesterday?"
- **GitHub.** The public API works without a token for public repos: `https://api.github.com/repos/{owner}/{repo}`. "How many open issues does apache/airflow have?"
- **The weather, a currency rate, anything with a free API** if you just want to see it work.

If you're not sure, start with GitHub. No account setup, no credentials, and you'll have it running in 20 minutes.

## How to add it

Look at `get_pipeline_runs` in `agents/llm_langgraph.py`. Your tool follows exactly the same pattern:

```python
@tool
def get_github_repo_stats(repo: str) -> str:
    """
    Get basic stats for a public GitHub repository.

    Use this when the user asks about stars, forks or open issues
    of a GitHub repository.

    The input must be the repo in the format owner/name, for example apache/airflow.
    """
    try:
        response = requests.get(f"https://api.github.com/repos/{repo}", timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"Error retrieving repo stats: {exc}"

    data = response.json()
    return (
        f"{data['full_name']}: {data['stargazers_count']} stars, "
        f"{data['forks_count']} forks, {data['open_issues_count']} open issues"
    )
```

Then register it:

```python
tools = [get_pipeline_runs, get_github_repo_stats]
```

And add one sentence to the `system_prompt` in `create_agent` that tells the model when to use it.

Three things that really matter with tools:

1. **The docstring is the most important part.** The model only sees the name, the docstring and the arguments. If the docstring is vague, the model guesses. Write it like you'd explain it to a new colleague.
2. **Return errors as text, don't raise.** If your tool crashes, the bot goes silent. If it returns "Error: repo not found", the agent tells the user what went wrong.
3. **Keep the output small.** Don't dump a 2 MB JSON response into the model. Pick the five fields that answer the question, like `get_pipeline_runs` does with the last five events.

## Your challenge

You're done when all of this works:

1. You ask a question in Slack that needs your tool, and you see the tool call in the logs.
2. The answer in the thread uses the real data from your tool.
3. You ask a normal question ("What is a data lake?") and the agent does NOT call your tool.
4. You break it on purpose (wrong ID, wrong repo name) and the bot explains the error instead of going silent.

Number 3 is the one people skip, and it's the one that tells you whether your docstring is any good.

## Stretch goals

- **Two tools, one question.** Ask something that needs both the Databricks tool and yours, and watch the agent call them one after the other.
- **Route with LangGraph.** Add a node before the agent that checks the question and sends it to a different agent with different tools. That's the start of a real multi-agent setup.
- **Run it for your team.** Put the container on a small server so your bot answers even when your laptop is closed. Remember that Ollama has to run there too, or point `OLLAMA_API_URL` at a machine that has it.

## Show it off

Post a screenshot of your bot answering in Slack in the course community inside the Academy, and tell us which tool you connected. I want to see what you build with this.
