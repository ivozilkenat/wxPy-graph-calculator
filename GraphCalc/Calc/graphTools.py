from MyWx.wx import *
from abc import ABC, abstractmethod

from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Property.PropertyManager.propertyManager import ActiveChangedEvent, EVT_ACT_PROP_CH

from GraphCalc.Application.outputPrompt import IOutputExtension

from typing import Union
# rework this whole file
# -use concept with more extensibility
# -more logical class structure
# -potentially use interruption to use selector


# Stores selected objects inorder or not in order
class SelectionSequence:
    def __init__(self, inOrder: bool = False):
        self._selection = list()
        self._inOrder = inOrder

    def getSelection(self):
        return self._selection

    def getSelectedTypes(self):
        return list(map(lambda x: type(x), self._selection))

    def isOrdered(self):
        return self._inOrder

    def reset(self):
        self._selection = list()

    def setOrdered(self, state: bool):
        self._inOrder = state

    def add(self, item):
        self._selection.append(item)

    def remove(self, item):
        self._selection.remove(item)

    def matches(self, selectionPattern, onlyBool=False):
        assert isinstance(selectionPattern, SelectionPattern)
        missing = list()
        selected = self.getSelectedTypes()
        print(selected)
        if self._inOrder:
            pass
        else:
            for o in selectionPattern.desiredObjs:
                if o not in self._selection:
                    missing.append(o)
            pass

        return True


# A selection pattern can be compared with a SelectionSequence and returns True, False or the missing types
#todo: implement further type checking and limitations
class SelectionPattern:
    def __init__(self, desiredObjects, fixedAmount=None):
        self.desiredObjs = desiredObjects
        assert self.validObjSelection(self.desiredObjs), "Expected list of classes"
        self.fixedAmount = fixedAmount

    @classmethod
    def validObjSelection(cls, objSelection):
        if any([not isinstance(i, type) for i in objSelection]):
            return False
        return True


class PropertySelector(IOutputExtension):
    def __init__(self):
        super().__init__()
        self._selection = None
        self._matching = None

    def setSelector(self, selector: SelectionSequence):
        self._selection = selector

    def selected(self):
        return self._selection

    def matchSelectionObjCall(self, selectionObj):
        assert SelectionInterface in type(selectionObj).__bases__
        self._matching = selectionObj
        self.setSelector(
            SelectionSequence(self._matching.selectInOrder())
        )

        self.sendlTry(f"Selected tool: '{selectionObj.getName()}'")
        self.sendlTry(f"Select:")

        #selectionObj(*args, **kwargs)

    def _matched(self):
        self._selection = None
        self._matching = None

    def update(self, evt: ActiveChangedEvent=None):
        if self._matching is None:
            return
        newObj = evt.selected
        self._selection.add(newObj)
        if missing := self._validSelection():
            self._matching.run()
            self._matched()
        else:
            self.sendlTry(f"Select: {missing}")

        evt.Skip()

    def _validSelection(self):
        print(self._selection.getSelection())


class SelectionInterface(ABC):
    _selectionInOrder = False
    def __init__(self):
        pass

    # Check if selected objects are desired types
    @abstractmethod
    def validSelector(self, selectorSequence):
        pass

    @classmethod
    def selectInOrder(cls):
        return cls._selectionInOrder


class GraphTool(ABC):
    _name: str = "Grafisches Werkzeug"

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
    _name: str = "Schnittpunkt-Berechnung"
    _selectionInOrder = False

    def __init__(self, graphPropertyManager, output=None, *args, **kwargs):
        GraphPropertyTool.__init__(self, graphPropertyManager, *args, **kwargs)
        IOutputExtension.__init__(self, output)
        SelectionInterface.__init__(self)

    def run(self, selectionSequence):
        print("run")

    def validSelector(self, selectionSequence):
        pass


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

        def _inner():
            self.call(tool)
        return _inner

    # def instantiateTool(self, tool: Union[GraphTool, GraphPropertyTool]):
    #     assert tool in self._tools, f"Tool: '{tool}' is not defined in ToolManager"
    #     assert isinstance(tool, (GraphTool, GraphPropertyTool)), f"Invalid Type of tool: '{type(tool)}'"
    #     if isinstance(GraphTool, GraphPropertyTool):
    #         toolObj = GraphTool(self._graphPropManager)
    #     else:
    #         toolObj = GraphTool()
    #     if tool.hasOutputInterface():
    #         toolObj.setOutput(self._output)
    #     return toolObj


#toolManager = ToolManager
#toolManager.call(
#   IntersectionTool(
# )
