from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.property import PropertyObjCategory, NonGraphicalPanelObject, SelectProperty, \
    ExprProperty, IntProperty, FloatProperty, IExprProperty, ReadOnlyProperty, DependentProperty

from GraphCalc._core import vc

class Variable(NonGraphicalPanelObject, IExprProperty):
    _basePlane: Dynamic2DGraphicalPlane
    strName = "Variable"

    def __init__(self, graphCalculator, valueExpression):
        NonGraphicalPanelObject.__init__(self, category=PropertyObjCategory.VARIABLE)
        IExprProperty.__init__(self, graphCalculator, valueExpression)

    def setBasePlane(self, plane):
        super().setBasePlane(plane)
        self.addProperty(
            ExprProperty(
                "value",
                self._exprObj,
                self._graphCalc,
                updateExprFunction=self.redefineAllExpressions,
                updateFunctions=self.refreshBasePlane
            )
        )
        self.addProperty(
            DependentProperty(
                self.getProperty("value"),
                ReadOnlyProperty(
                    "evaluation",
                    ""
                ),
                updateFunction=self._evalExpression,
                checkValidity=False
            )
        )

        self.redefineAllExpressions()
        self.refreshBasePlane()

    def _evalExpression(self):
        return str(self.getProperty("value").getValue().expr().evalf())