from MyWx.wx import *
from GraphCalc.Components.Graphical.graphPlanes import GraphicalPanel, Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.propertyManager import PropertyManager
from GraphCalc.Components.Property._property import PropertyObject, GraphicalPanelObject
from typing import Union


class GraphPropertyManager:
    _graphPlane: GraphicalPanel
    propertyManager: PropertyManager

    def __init__(self, graphPlane : GraphicalPanel, propertyManager : PropertyManager):
        self._graphPlane = graphPlane
        self.propertyManager = propertyManager

    def getGraphPlane(self):
        return self._graphPlane

    def setGraphPlane(self, graphPlane : GraphicalPanel):
        self._graphPlane = graphPlane

    def getPropertyManager(self):
        return self.propertyManager

    def setPropertyManager(self, propertyManager : PropertyManager):
        self.propertyManager = propertyManager

    def addPropertyObject(self, propertyObject: Union[PropertyObject, GraphicalPanelObject], show=True): #TODO: decide if to change property here
        self.propertyManager.addPropertyObject(propertyObject)
        if isinstance(propertyObject, GraphicalPanelObject):
            self._graphPlane.addGraphicalObject(propertyObject)

    def removePropertyObject(self, propertyObject: Union[PropertyObject, GraphicalPanelObject]):
        self.propertyManager.removePropObject(propertyObject)
        if isinstance(PropertyObject, GraphicalPanelObject):
            self._graphPlane.removeGraphicalObject(propertyObject)


class Dy2DGraphPropertyManager(GraphPropertyManager):
    def __init__(self, parent):
        super().__init__(graphPlane=Dynamic2DGraphicalPlane(parent), propertyManager=PropertyManager())
