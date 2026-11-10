from ddgs import DDGS


def _search(query, max_results):
    """Search with one retry. Returns a list of results, or [] if the search failed."""
    for attempt in range(2):
        try:
            with DDGS(timeout=8) as ddgs:
                return list(ddgs.text(query, max_results=max_results))
        except Exception as e:
            print(f"[search failed, attempt {attempt + 1}]: {e}")
    return []


def search_web(query, max_results=3):
    results = _search(query, max_results)
    if not results:
        return "Search is unavailable right now. Continue using only the resume and job description."
    return "\n".join(f"- {r['title']}: {r['body'][:200]}" for r in results)


def find_learning_resource(skill):
    results = _search(f"best free course {skill}", 3)
    stable = ["coursera.org", "youtube.com", "freecodecamp.org", "aws.amazon.com",
              "cloud.google.com", "huggingface.co", "kaggle.com"]
    for r in results:
        if any(d in r["href"] for d in stable):
            return f"{r['title']}: {r['href']}"
    q = skill.replace(" ", "+")
    return f"Search for current resources: https://www.google.com/search?q=free+course+{q}"


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information, e.g., about a specific technology, interview trends, or what a skill actually means in practice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_learning_resource",
            "description": "Find a specific free course or tutorial link to help close a skill gap. Use this for the top 1-2 most important missing skills, not every single one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string", "description": "The skill to find a learning resource for"}
                },
                "required": ["skill"]
            }
        }
    }
]
