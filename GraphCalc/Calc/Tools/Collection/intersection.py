from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D

from GraphCalc.Calc.Tools.graphSelector import SelectionInterface, SelectionPattern, SelectionSequence
from GraphCalc.Calc.Tools.graphTools import GraphPropertyTool

from GraphCalc.Application.outputPrompt import IOutputExtension

from sympy import *

# extra tool or parameter for creating point at intersection pos
class IntersectionTool(GraphPropertyTool, SelectionInterface, IOutputExtension):
    _name: str = "Intersection-Calculation"
    _selectionInOrder = True
    _selectionPattern = SelectionPattern(
        desiredTypes= [
            GraphFunction2D,
            GraphFunction2D,
        ]
    )

    def __init__(self, graphPropertyManager: Dy2DGraphPropertyManager, output=None, *args, **kwargs):
        GraphPropertyTool.__init__(self, graphPropertyManager, *args, **kwargs)
        IOutputExtension.__init__(self, output)
        SelectionInterface.__init__(self)

    def run(self, selectionSequence: SelectionSequence, onlyReal=True):
        selectionSequence = selectionSequence.getSelection()
        f1: GraphFunction2D = selectionSequence[0]
        f2: GraphFunction2D = selectionSequence[1]
        f1Expr, f2Expr = f1._getFuncExpr(), f2._getFuncExpr()

        self.sendlTry(f"Intersections:")
        # check if equal
        dExpr = f1Expr-f2Expr

        equal = simplify(dExpr) == 0
        if equal:
            self.sendlTry("infinte solutions (functions are equal)")
        else:
            # calc intersections
            try:
                intersections = solve(dExpr, quick=True, simplify=True, rational=False)
            except:
                self.sendlTry("Intersections cannot be calculated")
                return
            if onlyReal:
                intersections = [i for i in intersections if i.is_real]
            f1Func, f2Func = f1.getFuncAsCallable(), f2.getFuncAsCallable()
            if len(intersections) > 0:
                self.sendlTry("L = {")
                for i, intersection in enumerate(intersections):
                    self.sendlTry(f"x{i} = {intersection} | y{i} = {f1Func(intersection)}")
                self.sendlTry("}")
            else:
                self.sendlTry("L = {}")