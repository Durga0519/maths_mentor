from utils.openrouter_llm import call_llm
from tools.sympy_solver import derivative, solve_equation


def solver_agent(problem, context):

    text = problem.lower()

    # -----------------------------
    # Try SymPy for derivatives
    # -----------------------------
    if "derivative" in text or "d/dx" in text:

        try:

            expr = problem.split("of")[-1].strip()

            result = derivative(expr)

            return result

        except:
            pass

    # -----------------------------
    # Try SymPy for equations
    # -----------------------------
    if "=" in problem:

        try:

            result = solve_equation(problem)

            return result

        except:
            pass

    # -----------------------------
    # Otherwise use LLM
    # -----------------------------
    prompt = f"""
Solve this math problem.

Problem:
{problem}

Use the following knowledge if useful:
{context}

Return ONLY the final answer.
"""

    return call_llm(prompt)