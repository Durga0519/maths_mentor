import json
from utils.openrouter_llm import call_llm


def verifier_agent(problem, solution):

    prompt = f"""
You are verifying a math solution.

Problem:
{problem}

Solution:
{solution}

Check if the answer is correct.

Return JSON:

{{
 "confidence": number between 0 and 1,
 "comment": "short explanation"
}}
"""

    response = call_llm(prompt)

    try:
        data = json.loads(response)

    except:

        data = {
            "confidence": 0.5,
            "comment": "verification failed"
        }

    return data