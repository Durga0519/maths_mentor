from utils.openrouter_llm import call_llm


def explainer_agent(problem, solution):

    prompt = f"""
You are a math tutor.

Explain the following solution step-by-step
for a student preparing for JEE.

Problem:
{problem}

Final Answer:
{solution}

Provide a clear explanation.
"""

    return call_llm(prompt)