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
    """Search for a free course or tutorial for a specific skill."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"free course OR tutorial {skill} 2026", max_results=2))
        if not results:
            return f"No specific resource found for {skill}."
        formatted = []
        for r in results:
            formatted.append(f"- {r['title']}: {r['href']}")
        return "\n".join(formatted)
    except Exception as e:
        return f"Resource search temporarily unavailable ({str(e)}). Suggest a general approach instead."


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
