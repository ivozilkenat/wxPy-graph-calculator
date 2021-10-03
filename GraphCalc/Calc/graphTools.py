from MyWx.wx import *

from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Graphical.Objects.graphPropertyVariable import Variable

from GraphCalc.Calc.graphSelector import SelectionInterface, SelectionPattern, PropertySelector, SelectionSequence

from GraphCalc.Calc.graphCalculator import Function2DExpr

from GraphCalc.Application.outputPrompt import IOutputExtension

from abc import ABC, abstractmethod
from sympy import *


class GraphTool(ABC):
    _name: str = "Graphical-Tool"

    def __init__(self):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @classmethod
    def getName(cls):
        return cls._name

    @classmethod
    def hasSelectionInterface(cls):
        return True if SelectionInterface in cls.__bases__ else False

    @classmethod
    def hasOutputInterface(cls):
        return True if IOutputExtension in cls.__bases__ else False


class GraphPropertyTool(GraphTool, ABC):
    def __init__(self, graphPropertyManager, *args, **kwargs):
        GraphTool.__init__(self, *args, **kwargs)

        self._graphPropManager = graphPropertyManager


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
                intersections = solve(dExpr)
            except:
                self.sendlTry("Intersections cannot be calculated")
            if onlyReal:
                intersections = [i for i in intersections if i.is_real]
            f1Func, f2Func = lambdify(Function2DExpr.argumentSymbol, f1Expr), lambdify(Function2DExpr.argumentSymbol,
                                                                                       f2Expr)
            for i, intersection in enumerate(intersections):
                self.sendlTry(f"x{i} = {intersection}, y{i} = {f1Func(intersection)}")


# extend to use output prompt
class ToolManager(IOutputExtension):
    _tools = {
        IntersectionTool
    }

    #todo: add missing getter and setter
    def __init__(self, selector, output):
        super().__init__(output)
        self._selector: PropertySelector = None
        self.setSelector(selector)

    def getSelector(self):
        return self._selector

    def selectorUpdHandler(self):
        return self._selector.update

    def setSelector(self, selector: PropertySelector):
        self._selector = selector
        if self._selector is not None:
            self._selector.setOutput(self._output)

    def setOutput(self, output):
        super().setOutput(output)
        if self._selector is not None:
            self._selector.setOutput(self._output)

    def call(self, tool: GraphTool):
        assert type(tool) in self._tools,  f"Tool: '{type(tool)}' is not defined in ToolManager"
        if tool.hasSelectionInterface():
            self._selector.matchSelectionObjCall(tool)
        else:
            tool.run()

    def callable(self, tool: GraphTool):
        if tool.hasOutputInterface():
            if not tool.hasOutput():
                tool.setOutput(self._output)

        def _inner(*args, **kwargs):
            self.call(tool)
        return _inner