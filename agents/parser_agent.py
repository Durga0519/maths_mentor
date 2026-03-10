import json
from utils.openrouter_llm import call_llm

def parser_agent(question):

    prompt = f"""
    Extract structured information from the math problem.

    Problem:
    {question}

    Return JSON with:
    problem_text
    topic
    variables
    constraints
    needs_clarification
    """

    response = call_llm(prompt)

    try:
        data = json.loads(response)
    except:
        data = {
            "problem_text": question,
            "topic": "unknown",
            "variables": [],
            "constraints": [],
            "needs_clarification": False
        }

    return data