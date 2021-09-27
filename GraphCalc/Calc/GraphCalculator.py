from sympy import *

from typing import Tuple, Any, Optional
from abc import ABC, abstractmethod


class InvalidExpression(Exception):
    def __init__(self, message="Invalid Expression"):
        super().__init__(message)


class IncompatibleTypes(Exception):
    def __init__(self, message="Incompatible types"):
        super().__init__(message)


class ExprObj(ABC):
    def __init__(self, name: str, definition, original):
        # If values are supposed to be changed, define new object
        self.__org = original
        self.__name = name
        self._expr = definition
        self._isValid = self.isValid
        self.isValid = self.__validWrapper

    # checks if given expression is valid
    @abstractmethod
    def isValid(self):
        return True

    def __validWrapper(self):
        if not self.__standardValidation() or not self._isValid():
            raise InvalidExpression(f"Provided expression is invalid for {self.__class__.__name__}")

    def __standardValidation(self):
        name = Symbol(self.name())
        if name in self.expr().free_symbols:
            raise InvalidExpression(f"Name '{name}' can't be in expression")
        elif not self.name().isalpha():
            raise InvalidExpression(f"Name has to be defined by alpha-characters")
        elif name == Function2DExpr.argumentSymbol:
            raise InvalidExpression(f"Name of expression can't be argument symbol")
        return True

    def name(self):
        return self.__name

    # extensible standard implementation
    def nameFormatted(self):
        return self.__name

    def expr(self):
        return self._expr

    def original(self):
        return self.__org


#todo: x is in expression, when using f(n), even though not actually given
class ValueExpr(ExprObj):
    def __init__(self, name: str, definition, original):
        super().__init__(name, definition, original)
        self.isValid()

    def isValid(self):
        if isinstance(self.expr(), Expr):
            if Function2DExpr.argumentSymbol in self.expr().free_symbols:
                raise InvalidExpression(
                    f"Function argument symbol: '{Function2DExpr.argumentSymbol}' not allowed for Value"
                )
            return True


class Point2DExpr(ExprObj):
    def __init__(self, name: str, definition, original):
        super().__init__(name, definition, original)
        self.isValid()

    def isValid(self):
        if isinstance(self.expr(), tuple):
            self._expr = Point(self.expr())
            return True
        return False


class Function2DExpr(ExprObj):
    argumentSymbol = Symbol("x")

    def __init__(self, name: str, definition, original):
        super().__init__(name, definition, original)
        self.isValid()

    def isValid(self):
        if isinstance(self.expr(), Expr):
            if self.argumentSymbol not in self.expr().free_symbols:
                raise InvalidExpression(f"Missing argument symbol: '{self.argumentSymbol}' for Function")
            return True

    def nameFormatted(self):
        return f"{self.name()}({self.argumentSymbol})"


class GraphCalculator2D:
    allowedTypes = {
        Function2DExpr,
        Point2DExpr,
        ValueExpr
    }

    def __init__(self):
        self.parser = ExpressionStrParser()
        self._objects = dict()

    def get(self, name: str) -> Optional[ExprObj]:  # todo: implement exceptions
        if name in self._objects:
            return self._objects[name]
        return None

    def define(self, exprType, name: str, expressionAsString: str, raiseDefExceptions=True) -> bool:
        assert exprType in self.allowedTypes
        try:
            expr, org = self.parser.parse(expressionAsString, original=True)
        except (InvalidExpression, GeometryError) as e:
            raise e  # todo: not catched here currently

        try:
            self._objects[name] = exprType(name, expr, org)
        except InvalidExpression as e:
            if raiseDefExceptions:
                raise e
            else:
                return False

        # todo: potentially simplify by conversion
        if exprType is Function2DExpr:
            self.parser.addDefinition(name, lambda x: expr)
        elif exprType is Point2DExpr:
            self.parser.addDefinition(name, Point(expr))
        elif exprType is ValueExpr:
            self.parser.addDefinition(name, expr)

        return True

    def undefine(self, name: str):
        del self._objects[name]


class ExpressionStrParser:
    def __init__(self):
        self._namespace = dict()

    def parse(self, string: str, original: bool = False):
        try:
            e = sympify(string, locals=self._namespace)  # rational=True?
        except (TypeError, SympifyError) as e:
            raise InvalidExpression(f"Invalid expression: '{string}' -> {e}")

        return e if not original else e, string

    def addDefinition(self, var: str, value, override=True):
        assert isinstance(var, str)
        if not override:
            if var in self._namespace:
                return  # todo: raise already exists error
        # if point towards def, check if exsting
        if isinstance(value, str):
            if value in self._namespace:
                self._namespace[var] = self._namespace[value]
        else:
            self._namespace[var] = value

    def addDefinitions(self, vars: Tuple[str, ...], values: Tuple[Any, ...], override=True):
        for var, value in zip(vars, values):
            self.addDefinition(var, value, override)

    def getValue(self, var: str):
        return self._namespace[var]


if __name__ == "__main__":
    calc = GraphCalculator2D()

    # calc.define(Point2DExpr, "c", "(a, b)")
    # print(calc.get("c").expr())
    # print(calc.parser._namespace)

    calc.define(Point2DExpr, "a", "(1, 5)")
    # calc.define(Point2DExpr, "b", "(5, 3)")

    calc.define(ValueExpr, "a", "2")  # <= overrides old definition

    print(calc.parser._namespace)

    if calc.define(Function2DExpr, "p", "a + b + x"):
        print("could define!")
        # =Testing===========================

        print(calc.get("p").expr().evalf())
        print(calc.get("p").expr().diff("x"))

    # print(calc.parser._namespace)

    # ===================================
    else:
        print("could not define!")

# calc.parser.addDefinition("func", lambda x: x**2)
# calc.define("f", "a+b+c+x+sin(x)+func(x)")
#
# print("f:", calc.get("f").original())
# print("f:", calc.get("f").expr())
# print()
#
# calc.define("g", "f(x)")
# print("g:", calc.get("g").original())
# print("g:", calc.get("g").expr())
# print()
#
# print(calc.get("g").expr())
