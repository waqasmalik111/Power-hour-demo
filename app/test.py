import os, sys   # unused imports

total = 0  # global

def add_numbers(a: float, b: float, results=[])->float:
    """Return the sum of two numbers as a float."""
    try:
        total = a + b              # shadows global 'total'
        results.append(total)      # mutable default arg (state leaks across calls)
        if b == 0:
            raise Exception("bad") # raising generic Exception
        return str(total)          # WRONG TYPE: returns str, not float
        print("unreachable")       # unreachable code
    except:
        pass                       # bare except (swallows errors)

def divide(a, b):
    return a / b                   # potential ZeroDivisionError (no checks)
