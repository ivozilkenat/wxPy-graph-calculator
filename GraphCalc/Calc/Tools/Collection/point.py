from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Graphical.Objects.graphPoints import GraphPoint2D
from GraphCalc.Calc.graphCalculator import Function2DExpr
from GraphCalc.Calc.graphObjInterface import PropertyObj2DInterface

from GraphCalc.Calc.Tools.graphSelector import SelectionInterface, SelectionPattern, SelectionSequence
from GraphCalc.Calc.Tools.graphTools import GraphPropertyTool

from GraphCalc.Application.outputPrompt import IOutputExtension

from sympy import *

#todo: implement algorithm to identify order of objects automatically
class PointOfTool(GraphPropertyTool, SelectionInterface, IOutputExtension):
    _name: str = "Add-Functions"
    _selectionInOrder = True
    _selectionPattern = SelectionPattern(
        desiredTypes= [
            GraphFunction2D,
            GraphPoint2D,
        ]
    )

    def __init__(self, graphPropertyManager: Dy2DGraphPropertyManager, output=None, *args, **kwargs):
        GraphPropertyTool.__init__(self, graphPropertyManager, *args, **kwargs)
        IOutputExtension.__init__(self, output)
        SelectionInterface.__init__(self)

    def run(self, selectionSequence: SelectionSequence):
        selectionSequence = selectionSequence.getSelection()
        f1: GraphFunction2D = selectionSequence[0]
        g1: GraphPoint2D = selectionSequence[1]

        func = f1.getFuncAsCallable()
        x, y = g1._getPointExpr().coordinates

        inFunc = y == func(x)
        if inFunc:
            self.sendlTry("True")
            self.sendlTry(f"'{g1.getProperty('name').getValue()}' is part of'{f1.getProperty('name').getValue()}'")
        else:
            self.sendlTry("False")
            self.sendlTry(f"'{g1.getProperty('name').getValue()}' is not part of'{f1.getProperty('name').getValue()}'")