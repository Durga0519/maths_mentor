import sympy as sp

def solve_equation(expr):

    x = sp.symbols('x')

    equation = sp.sympify(expr)

    result = sp.solve(equation, x)

    return result


def derivative(expr):

    x = sp.symbols('x')

    f = sp.sympify(expr)

    return sp.diff(f, x)