from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Calc.graphCalculator import Function2DExpr
from GraphCalc.Calc.graphObjInterface import PropertyObj2DInterface

from GraphCalc.Calc.Tools.graphSelector import SelectionInterface, SelectionPattern, SelectionSequence
from GraphCalc.Calc.Tools.graphTools import GraphPropertyTool

from GraphCalc.Application.outputPrompt import IOutputExtension

from sympy import *

class AddTool(GraphPropertyTool, SelectionInterface, IOutputExtension):
    _name: str = "Add-Functions"
    _selectionInOrder = True
    _selectionPattern = SelectionPattern(
        desiredTypes= [
            GraphFunction2D,
            GraphFunction2D,
        ]
    )

    def __init__(self, graphPropertyManager: Dy2DGraphPropertyManager, graphObjInterface: PropertyObj2DInterface, output=None, *args, **kwargs):
        GraphPropertyTool.__init__(self, graphPropertyManager, *args, **kwargs)
        IOutputExtension.__init__(self, output)
        SelectionInterface.__init__(self)
        self._graphObjInterface = graphObjInterface

    def run(self, selectionSequence: SelectionSequence):
        selectionSequence = selectionSequence.getSelection()
        f1: GraphFunction2D = selectionSequence[0]
        f2: GraphFunction2D = selectionSequence[1]
        f1Expr, f2Expr = f1._getFuncExpr(), f2._getFuncExpr()
        self._graphObjInterface.addExprObj(
            Function2DExpr,
            f"{f1.getProperty('function_definition').getValue().name()}+{f2.getProperty('function_definition').getValue().name()}",
            f"{f1Expr + f2Expr}"
        )
