from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager

from GraphCalc.Calc.Tools.graphSelector import SelectionInterface

from GraphCalc.Application.outputPrompt import IOutputExtension

from abc import ABC, abstractmethod

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
    def __init__(self, graphPropertyManager: Dy2DGraphPropertyManager, *args, **kwargs):
        GraphTool.__init__(self, *args, **kwargs)

        self._graphPropManager = graphPropertyManager
