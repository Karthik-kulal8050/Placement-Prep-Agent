import os
import json
from dotenv import load_dotenv
from groq import Groq
from .parse_inputs import read_pdf_text, read_txt
from .tools import search_web, TOOLS_SCHEMA, find_learning_resource
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOL_FUNCTIONS = {
    "search_web": search_web,
    "find_learning_resource": find_learning_resource,
}

def gap_analysis(resume_text, jd_text):
    system = """You are a supportive, honest career coach AI, not a critic. Compare the RESUME against the JOB DESCRIPTION.

You have two tools:
- search_web: for verifying how important/common a skill is for this type of role
- find_learning_resource: to suggest ONE concrete way to close the 1-2 most important gaps (don't look up a resource for every single missing skill, only the top priority ones)

Frame gaps constructively: not "you lack X" but "focus on X next, here's a place to start." The goal is to help the candidate prioritize and act, not to discourage them.

Return ONLY valid JSON in exactly this format:
{
  "matched_skills": ["skill1"],
  "missing_skills": ["skill1"],
  "partial_matches": ["skill1"],
  "overall_fit_percent": 0,
  "summary": "2-3 sentence honest but encouraging assessment",
  "top_priority_to_learn": "the ONE most important skill to focus on next, with a brief reason",
  "learning_resource": "a specific link if found, else empty string",
  "additional_notes": "any other useful context from research, empty string if none"
}"""

    user = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}"

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    # safety: strip markdown fences if the model adds them anyway
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)

def agentic_gap_analysis(resume_text, jd_text, user_question=None):
    system = """You are a supportive, honest career coach AI, not a critic. Compare the RESUME against the JOB DESCRIPTION.

You have two tools:
- search_web: for verifying how important/common a skill is for this type of role
- find_learning_resource: to suggest ONE concrete way to close the 1-2 most important gaps (don't look up a resource for every single missing skill, only the top priority ones)

Frame gaps constructively: not "you lack X" but "focus on X next, here's a place to start." The goal is to help the candidate prioritize and act, not to discourage them.

Return ONLY valid JSON in exactly this format:
{
"matched_skills": ["skill1"],
"missing_skills": ["skill1"],
"partial_matches": ["skill1"],
"overall_fit_percent": 0,
"summary": "2-3 sentence honest but encouraging assessment",
"top_priority_to_learn": "the ONE most important skill to focus on next, with a brief reason",
"learning_resource": "a specific link if found, else empty string",
"additional_notes": "any other useful context from research, empty string if none"
}"""

    user_content = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}"
    if user_question:
        user_content += f"\n\nADDITIONAL QUESTION: {user_question}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]

    # Loop: the model might call a tool, get results, then respond again
    for i in range(5):
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS_SCHEMA if i < 4 else None,  # force a final answer on the last round, no more tool calls allowed
            temperature=0.1,
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                func_name = tool_call.function.name
                args_raw = tool_call.function.arguments

                if func_name =="json":
                    return json.loads(args_raw)

                args = json.loads(args_raw)
                func = TOOL_FUNCTIONS[func_name]
                print(f"[Agent calling {func_name}]: {args}")
                result = func(**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
            continue
        else:
            raw = message.content.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(raw)

    return {"error": "Agent took too many steps without finishing."}


if __name__ == "__main__":
    resume = read_pdf_text("data/resume.pdf")
    jd = read_txt("data/jd2.txt")

    result = agentic_gap_analysis(
        resume, jd,
        user_question="Is LangChain commonly asked about in interviews for roles like this? Search if needed."
    )
    print(json.dumps(result, indent=2))
    