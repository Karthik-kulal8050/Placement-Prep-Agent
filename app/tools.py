from ddgs import DDGS


def search_web(query, max_results=3):
    """Search the web and return a few short results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found for this query."
        formatted = []
        for r in results:
            formatted.append(f"- {r['title']}: {r['body'][:200]}")
        return "\n".join(formatted)
    except Exception as e:
        return f"Search temporarily unavailable ({str(e)}). Proceed with the information you already have."


def find_learning_resource(skill):
    """Return a reliable way to start learning a skill, favoring stable platforms over possibly-dead deep links."""
    with DDGS() as ddgs:
        results = list(ddgs.text(f"best free course {skill}", max_results=3))

    # Prefer well-known, stable platforms if they appear in results
    stable_domains = ["coursera.org", "youtube.com", "freecodecamp.org", "aws.amazon.com",
                       "cloud.google.com", "docs.python.org", "huggingface.co", "kaggle.com"]

    for r in results:
        if any(domain in r["href"] for domain in stable_domains):
            return f"{r['title']}: {r['href']}"

    # Fallback: a guaranteed-stable search link instead of a specific article
    query = skill.replace(" ", "+")
    return f"Search for current resources: https://www.google.com/search?q=free+course+{query}"

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
