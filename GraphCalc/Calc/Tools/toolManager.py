from GraphCalc.Application.outputPrompt import IOutputExtension

from GraphCalc.Calc.Tools.Collection import intersection
from GraphCalc.Calc.Tools.graphSelector import PropertySelector
from GraphCalc.Calc.Tools.graphTools import GraphTool


class ToolManager(IOutputExtension):
    _tools = {
        intersection.IntersectionTool
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