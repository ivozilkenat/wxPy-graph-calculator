import wx

from MyWx.wx import *

from GraphCalc.Components.Graphical.graphPlanes import GraphicalPanel, Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.PropertyManager.propertyManager import PropertyManager
from GraphCalc.Components.Property.property import PropertyObject, GraphicalPanelObject
from GraphCalc._core import vc

from typing import Union


class GraphPropertyManager:
    _graphPlane: GraphicalPanel  # TODO: implement this sort of typing everywhere?
    propertyManager: PropertyManager

    def __init__(self, graphPlane: GraphicalPanel, propertyManager: PropertyManager):
        self._graphPlane = graphPlane
        self.propertyManager = propertyManager

    def getGraphPlane(self):
        return self._graphPlane

    def setGraphPlane(self, graphPlane: GraphicalPanel):
        self._graphPlane = graphPlane

    def getPropertyManager(self):
        return self.propertyManager

    def setPropertyManager(self, propertyManager: PropertyManager):
        self.propertyManager = propertyManager

    def addPropertyObject(self, propertyObject: Union[PropertyObject, GraphicalPanelObject],
                          show=True):  # TODO: decide if to change property here
        self.propertyManager.addPropertyObject(propertyObject)
        if isinstance(propertyObject, GraphicalPanelObject):
            self._graphPlane.addGraphicalObject(propertyObject)
            if show:  # <- let this stay?
                propertyObject.getProperty(vc.PROPERTY_DRAW).setValue(True)
            else:
                propertyObject.getProperty(vc.PROPERTY_DRAW).setValue(False)
            #todo: add feedback if object could be created or not, considering SeedException

    def removePropertyObject(self, propertyObject: Union[PropertyObject, GraphicalPanelObject]):
        self.propertyManager.removePropObject(propertyObject)
        if isinstance(propertyObject, GraphicalPanelObject):
            self._graphPlane.removeGraphicalObject(propertyObject)


# Defines interface between graphPlane and properties -> allows for graphical operations etc.
class Dy2DGraphPropertyManager(GraphPropertyManager):
    def __init__(self, parent):
        super().__init__(graphPlane=Dynamic2DGraphicalPlane(parent), propertyManager=PropertyManager())
        self._graphPlane._setActiveObj = self._setActiveObj
        # Is this a good implementation?

    def _setActiveObj(self, object):
        self.propertyManager.setActiveProperty(object)  # todo: potential bugs?


# Panel for adding property objects
class PropertyAddPanel(GenericPanel):
    def __init__(self, manager, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self._manager = manager
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetBackgroundColour(vc.COLOR_WHITE)

        self.build()

    def build(self):
        self._sizer.Clear()
        notebook = wx.Notebook(self)

        self._expressionPanel = GenericPanel(notebook)
        self._expressionPanel.SetBackgroundColour((255, 0, 0))
        self._shapePanel = GenericPanel(notebook)
        self._shapePanel.SetBackgroundColour((0, 255, 0))
        self._otherPanel = GenericPanel(notebook)
        self._otherPanel.SetBackgroundColour((0, 0, 255))

        notebook.AddPage(self._expressionPanel, text="Expression")
        notebook.AddPage(self._shapePanel, text="Shape")
        notebook.AddPage(self._otherPanel, text="Other")

        self._sizer.Add(notebook, 1, wx.EXPAND)

        self.SetSizer(self._sizer)
