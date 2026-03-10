import sympy as sp


def solve_equation(expr):

    x = sp.symbols('x')

    try:

        equation = sp.sympify(expr)

        result = sp.solve(equation, x)

        return str(result)

    except Exception as e:

        return f"SymPy error: {str(e)}"


def derivative(expr):

    x = sp.symbols('x')

    try:

        f = sp.sympify(expr)

        result = sp.diff(f, x)

        return str(result)

    except Exception as e:

        return f"Derivative error: {str(e)}"