import wx

from MyWx.wx import *

from GraphCalc.Components.Graphical.graphPlanes import GraphicalPanel, Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.PropertyManager.propertyManager import PropertyManager
from GraphCalc.Components.Property.property import PropertyObject, GraphicalPanelObject, NonGraphicalPanelObject
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
                          show=True,
                          setAsActive=True):  # TODO: decide if to change property here
        self.propertyManager.addPropertyObject(propertyObject)
        if isinstance(propertyObject, NonGraphicalPanelObject):
            propertyObject.setBasePlane(self._graphPlane)
        elif isinstance(propertyObject, GraphicalPanelObject):
            self._graphPlane.addGraphicalObject(propertyObject)
            if show:  # <- let this stay?
                propertyObject.getProperty(vc.PROPERTY_DRAW)._setValue(True)
            else:
                propertyObject.getProperty(vc.PROPERTY_DRAW)._setValue(False)
        if setAsActive:
            self.propertyManager.setActiveProperty(propertyObject)
            # todo: add feedback if object could be created or not, considering SeedException

    def removePropertyObject(self, propertyObject: Union[PropertyObject, GraphicalPanelObject]):
        self.propertyManager.removePropObject(propertyObject)
        if isinstance(propertyObject, GraphicalPanelObject):
            self._graphPlane.removeGraphicalObject(propertyObject)

    def removeUndefinePropertyObject(self, propertyObject: Union[PropertyObject, GraphicalPanelObject]):
        self.propertyManager.undefinePropObject(propertyObject)
        self.removePropertyObject(propertyObject)
        self.propertyManager.redefineAllExpressions()



# Defines interface between graphPlane and properties -> allows for graphical operations etc.
class Dy2DGraphPropertyManager(GraphPropertyManager):
    def __init__(self, parent):
        super().__init__(graphPlane=Dynamic2DGraphicalPlane(parent), propertyManager=PropertyManager())
        self._graphPlane._setActiveObj = self._setActiveObj
        # Is this a good implementation?

    def _setActiveObj(self, object):
        self.propertyManager.setActiveProperty(object)  # todo: potential bugs?
