from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.property import PropertyObjCategory, NonGraphicalPanelObject, SelectProperty, \
    ExprProperty, IntProperty, FloatProperty, IExprProperty, ReadOnlyProperty, ListProperty, DependentProperty, StrProperty, ToggleProperty
from sympy import *

#todo: implement this class (currently: work in progress)


class GraphFunctionGroup(NonGraphicalPanelObject, IExprProperty):
    _basePlane: Dynamic2DGraphicalPlane
    strName = "Kurvenschar"

    def __init__(self, graphCalculator, valueExpression):
        NonGraphicalPanelObject.__init__(self, category=PropertyObjCategory.VARIABLE)
        IExprProperty.__init__(self, graphCalculator, valueExpression)

        self._functions = set()

    def setBasePlane(self, plane):
        super().setBasePlane(plane)
        self.addProperties([
            ExprProperty(
                "function_definition",
                self._exprObj,
                self._graphCalc,
                updateFunctions=self.refreshBasePlane,
                updateExprFunction=self.redefineAllExpressions
            ),
            StrProperty("dependent_variable", "a", updateFunctions=self.refreshBasePlane),

            ListProperty("substitution_values", (1, 2, 3), updateFunctions=self.refreshBasePlane),
            ToggleProperty("use_substitution", False, updateFunctions=self.refreshBasePlane),

            IntProperty("function_amount", 3, updateFunctions=self.refreshBasePlane),
            FloatProperty("value_coefficient", 0.1, updateFunctions=self.refreshBasePlane, increment=0.01)

        ])

    def _updateFunctionDefinitions(self):
        # call update in dependent variable
        pass

    def setupFunctions(self):
        pass
