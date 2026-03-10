from utils.openrouter_llm import call_llm
import json

TOPICS = ["algebra", "probability", "calculus", "linear_algebra", "geometry", "other"]

def router_agent(problem: str) -> dict:
    """
    Classifies the problem type and returns routing info.
    Returns:
      {
        "topic":      "calculus",
        "subtopic":   "derivatives",
        "strategy":   "symbolic_solver" | "llm" | "rag_only",
        "use_sympy":  true | false
      }
    """
    prompt = f"""You are a math problem classifier for a JEE tutor app.

Classify this math problem and decide the best solution strategy.

Problem:
{problem}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "topic": one of {TOPICS},
  "subtopic": short string e.g. "derivatives", "quadratic equations", "matrix operations",
  "strategy": one of ["symbolic_solver", "llm", "rag_only"],
  "use_sympy": true if the problem can be solved symbolically with SymPy else false
}}

Rules:
- strategy = "symbolic_solver" for equations, derivatives, integrals
- strategy = "rag_only" for conceptual / definition questions  
- strategy = "llm" for word problems or mixed reasoning
- use_sympy = true only for algebraic equations and calculus
"""
    response = call_llm(prompt)

    try:
        # Strip markdown fences if present
        clean = response.strip().strip("```json").strip("```").strip()
        data  = json.loads(clean)
    except Exception:
        # Fallback: keyword-based classification
        text = problem.lower()
        if any(k in text for k in ["derivative", "d/dx", "differentiate", "limit", "integrate"]):
            topic, subtopic, strategy, use_sympy = "calculus", "calculus", "symbolic_solver", True
        elif any(k in text for k in ["probability", "P(", "P (", "random", "event"]):
            topic, subtopic, strategy, use_sympy = "probability", "probability", "llm", False
        elif any(k in text for k in ["matrix", "determinant", "eigenvalue", "vector"]):
            topic, subtopic, strategy, use_sympy = "linear_algebra", "matrices", "llm", False
        else:
            topic, subtopic, strategy, use_sympy = "algebra", "algebra", "symbolic_solver", True

        data = {"topic": topic, "subtopic": subtopic, "strategy": strategy, "use_sympy": use_sympy}

    return data