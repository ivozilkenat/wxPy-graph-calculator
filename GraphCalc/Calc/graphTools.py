from MyWx.wx import *
from abc import ABC, abstractmethod

from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Property.PropertyManager.propertyManager import ActiveChangedEvent, EVT_ACT_PROP_CH

from typing import Union
# rework this whole file
# -use concept with more extensibility
# -more logical class structure


class Selector:
    def __init__(self):
        self._selection = set()
        self._matching = None

    def selected(self):
        return self._selection

    def reset(self):
        self._selection = set()

    def addSelect(self, selected):
        self._selection.add(selected)

    def removeSelect(self, selected):
        self._selection.remove(selected)

    def matchSelectionObjCall(self, selectionObj, *args, **kwargs):
        assert SelectionInterface in selectionObj.__bases__
        self.reset()
        self._matching = selectionObj

        #selectionObj(*args, **kwargs)

    def update(self, evt: ActiveChangedEvent=None):
        if self._matching is None:
            return
        newObj = evt.selected
        self.addSelect(newObj)

        evt.Skip()


class SelectionInterface(ABC):
    def __init__(self):
        pass

    # Check if selected objects are desired types
    @abstractmethod
    def validSelector(self):
        pass


class GraphTool(ABC):
    _name: str = "Grafisches Werkzeug"

    def __init__(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @classmethod
    def getName(cls):
        return cls._name

    @classmethod
    def hasSelection(cls):
        return True if SelectionInterface in cls.__bases__ else False


class GraphPropertyTool(GraphTool, ABC):
    def __init__(self, graphPropertyManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._graphPropManager = graphPropertyManager


# extra tool or parameter for creating point at intersection pos
class IntersectionTool(GraphPropertyTool, SelectionInterface):
    _name: str = "Schnittpunkt-Berechnung"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        pass

    def validSelector(self):
        pass


# extend to use output prompt
class ToolManager:
    _tools = {
        IntersectionTool
    }

    def __init__(self, graphPropertyManager, selector):
        self._graphPropManager: Dy2DGraphPropertyManager = graphPropertyManager
        self._selector: Selector = selector

    def getSelector(self):
        return self._selector

    def setSelector(self, selector: Selector):
        self._selector = selector

    def call(self, tool: Union[GraphTool, GraphPropertyTool]):
        assert tool in self._tools, f"Tool: '{tool}' is not defined in ToolManager"
        if isinstance(GraphTool, GraphPropertyTool):
            tool = GraphTool(self._graphPropManager)
        else:
            tool = GraphTool()
        if GraphTool.hasSelection():
            self._selector.matchSelectionObjCall(tool)
        else:
            tool.run()

#toolManager = ToolManager
#toolManager.call(IntersectionTool)

class NewTool:
    def __init__(self):
        pass
