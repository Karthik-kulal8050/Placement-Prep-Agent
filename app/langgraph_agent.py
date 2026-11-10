import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from .tools import search_web, find_learning_resource
from .parse_inputs import read_pdf_text, read_txt

load_dotenv()   # ChatGroq reads GROQ_API_KEY from the environment


from typing import List
from pydantic import BaseModel

class GapReport(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    partial_matches: List[str]
    overall_fit_percent: int
    summary: str
    top_priority_to_learn: str
    learning_resource: str = ""
    additional_notes: str = ""

# 1. Tools: wrap your existing functions so LangChain knows their name,
#    arguments and description (the docstring replaces your TOOLS_SCHEMA)
@tool
def search_web_tool(query: str) -> str:
    """Search the web for current information, e.g. interview trends or what a skill means in practice."""
    return search_web(query)


@tool
def find_learning_resource_tool(skill: str) -> str:
    """Find a free course or tutorial for a skill gap. Use for the top 1-2 gaps only."""
    return find_learning_resource(skill)


TOOLS = [search_web_tool, find_learning_resource_tool]

# 2. The model, told which tools exist
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.1)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = SYSTEM_PROMPT = """You are a supportive, honest career coach. Compare the RESUME against the JOB DESCRIPTION.
You have two tools:
- search_web_tool: verify how important a skill is for this kind of role
- find_learning_resource_tool: only for the 1-2 most important gaps
Only these two tools exist. Do not call any other tool.

Frame gaps constructively: "focus on X next", not "you lack X".

When you are done researching, reply in plain text (no JSON) covering:
matched skills, missing skills, partial matches, an overall fit percent,
a 2-3 sentence summary, the ONE skill to learn next with a reason,
a learning resource link if you found one, and any other notes.
"""


# 3. Node: call the model with the whole message history
def call_model(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# 4. Build the graph
builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(TOOLS))        # runs whichever tool the model asked for

builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)   # tool requested -> "tools", else -> END
builder.add_edge("tools", "model")                        # after a tool runs, go back to the model

graph = builder.compile()


structured_llm = llm.with_structured_output(GapReport)


def langgraph_gap_analysis(resume_text, jd_text, user_question=None):
    content = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}"
    if user_question:
        content += f"\n\nADDITIONAL QUESTION: {user_question}"

    try:
        result = graph.invoke(
            {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=content)]},
            config={"recursion_limit": 11},
        )
        analysis_text = result["messages"][-1].content

        report = structured_llm.invoke([
            SystemMessage(content="Convert the analysis below into the report schema. Do not add new information."),
            HumanMessage(content=analysis_text),
        ])
        return report.model_dump()
    except Exception as e:
        return {"error": f"Agent did not finish: {e}"}



if __name__ == "__main__":
    resume = read_pdf_text("data/resume.pdf")
    jd = read_txt("data/jd2.txt")
    print(json.dumps(langgraph_gap_analysis(resume, jd), indent=2))