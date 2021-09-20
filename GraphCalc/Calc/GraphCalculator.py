from sympy import *

from typing import Tuple, Any, Optional
from abc import ABC, abstractmethod

class InvalidExpression(Exception):
	def __init__(self, message="Invalid Expression"):
		super().__init__(message)

class UncompatibleTypes(Exception):
	def __init__(self, message="Uncompatible types"):
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
		if not self._isValid():
			raise InvalidExpression(f"Provided expression is invalid for {self.__class__.__name__}")

	def name(self):
		return self.__name

	def expr(self):
		return self._expr

	def original(self):
		return self.__org

class ValueExpr(ExprObj):
	def __init__(self, name: str, definition, original):
		super().__init__(name, definition, original)
		self.isValid()

	def isValid(self):
		if isinstance(self.expr(), Expr):
			if Function2DExpr.argumentSymbol in self.expr().free_symbols:
				raise InvalidExpression(f"Function argument symbol: '{Function2DExpr.argumentSymbol}' not allowed for Value")
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
			if not self.argumentSymbol in self.expr().free_symbols:
				raise InvalidExpression(f"missing argument symbol: '{self.argumentSymbol}' for Function")
			return True

class GraphCalculator2D:
	allowedTypes = {
		Function2DExpr,
		Point2DExpr,
		ValueExpr
	}
	def __init__(self):
		self.parser = ExpressionStrParser()
		self._objects = dict()

	def get(self, name: str) -> Optional[ExprObj]: #todo: implement exceptions
		if name in self._objects:
			return self._objects[name]
		return None

	def define(self, objectType, name: str,  expressionAsString: str) -> bool:
		assert objectType in self.allowedTypes
		#try:
		exp, org = self.parser.parse(expressionAsString, original=True)
		# except (InvalidExpression, GeometryError):
		# 	return False

		self._objects[name] = objectType(name, exp, org)

		if objectType is Function2DExpr:
			self.parser.addDefinition(name, lambda x: exp)
		elif objectType is Point2DExpr:
			self.parser.addDefinition(name, Point(exp))
		elif objectType is ValueExpr:
			self.parser.addDefinition(name, exp)

		return True

	def undefine(self, name: str):
		del self._objects[name]

class ExpressionStrParser:
	def __init__(self):
		self._namespace = dict()

	def parse(self, string: str, original:bool = False):
		try:
			e = sympify(string, locals=self._namespace)
		except (TypeError, SympifyError) as e:
			raise InvalidExpression(f"Invalid expression: '{string}' -> {e}")

		return e if not original else e, string

	def addDefinition(self, var: str, value, override=True):
		assert isinstance(var, str)
		if not override:
			if var in self._namespace:
				return # todo: raise already exists error
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

calc = GraphCalculator2D()

# calc.define(Point2DExpr, "c", "(a, b)")
# print(calc.get("c").expr())
# print(calc.parser._namespace)

calc.define(Point2DExpr, "a", "(1, 5)")
# calc.define(Point2DExpr, "b", "(5, 3)")

calc.define(ValueExpr, "a", "2") #<= overrides old definition

print(calc.parser._namespace)


if calc.define(Function2DExpr, "p", "a + b + x"):
	print("could define!")
	#=Testing===========================

	print(calc.get("p").expr().evalf())
	print(calc.get("p").expr().diff("x"))

	#print(calc.parser._namespace)


	#===================================
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