from GraphCalc.Calc.GraphCalculator import GraphCalculator2D, Function2DExpr, InvalidExpression
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Property.property import IExprProperty

class GraphObj2DInterface:
	typeAssignments = {
		Function2DExpr : GraphFunction2D
	}
	def __init__(self,
				 graphCalculator: GraphCalculator2D,
				 graphPropertyManager: Dy2DGraphPropertyManager
				 ):
		self._graphCalc = graphCalculator
		self._graphPropManager = graphPropertyManager

	def addExprObj(self, exprType, name, expressionAsString):
		# parse expression and validate
		if exprType not in self.typeAssignments:
			raise InvalidExpression(f"Expression cannot be converted into any GraphicalProperty-object")

		try:
			successful = self._graphCalc.define(exprType, name, expressionAsString)
		except InvalidExpression as e:
			raise e #todo: currently doesnt catch error, should this be handled in higher class?

		if not successful:
			raise InvalidExpression(f"Expression: '{expressionAsString}' couldn't be parsed successfully")
		# create object

		targetObject = self.typeAssignments[exprType]
		newObj = targetObject(self._graphCalc, self._graphCalc.get(name))

		for p in self._graphPropManager.propertyManager.getPropertyObjects():
			if isinstance(p, IExprProperty):
				if p._exprObj.name() == name: # object was defined before and is already in property manager
					self._graphPropManager.removePropertyObject(p) # prevents accidental multi definition
					break

		self._graphPropManager.addPropertyObject(newObj)