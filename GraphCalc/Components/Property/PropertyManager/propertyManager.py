import wx

from MyWx.wx import *
from MyWx.Collection._core import error, wxUtilities
from MyWx.Collection.format import expanded

from GraphCalc.Components.Property.PropertyManager.propertyOverview import PropObjectOverviewPanel
from GraphCalc.Components.Property.PropertyManager.propertyInspection import PropInspectionPanel
from GraphCalc.Components.Property.property import PropertyObject, Property, PropertyCategory, PropCategoryDataClass

from typing import Set

from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Graphical.graphUtilities import CartesianAxies

#TODO: -allow for sorting of properties and categorize them

# Base class to handle everything related to propertyObject organization
class PropertyManager:
    def __init__(self):
        self._propertyObjects: Set[PropertyObject] = set()
        self._activeProperty = None #<- shown in the inspection panel / highlighted in the managed object (if possible)

        self._overviewPanel: PropObjectOverviewPanel = None
        self._inspectionPanel: PropInspectionPanel = None

        # Extend the PropertyManager-class to fit desired needs, e.g. Graph Plane

    def getPropertyObjects(self):
        return self._propertyObjects

    def addPropertyObject(self, propertyObject: PropertyObject):
        assert isinstance(propertyObject, PropertyObject)
        self._propertyObjects.add(propertyObject)
        propertyObject.setManager(self)
        if self._overviewPanel is not None:
            self._overviewPanel.addToCategory(propertyObject)

    def removePropObject(self, propertyObject: PropertyObject):
        assert isinstance(propertyObject, PropertyObject)
        self._propertyObjects.remove(propertyObject)
        if self._overviewPanel is not None:
            self._overviewPanel.removeFromCategory(propertyObject)

    def getPropertiesByCategory(self):
        categoryDic = PropertyCategory.categoryDict()
        for p in self._propertyObjects:
            categoryDic[p.getCategory()].append(p)
        return categoryDic

    # Set currently selected/Focused Property
    def setActiveProperty(self, propertyObject: PropertyObject):
        equal = self._activeProperty == propertyObject
        self._activeProperty = propertyObject
        if self.hasInspectionPanel() and not equal:
            self._inspectionPanel.setActivePropObj(self._activeProperty)
            self._inspectionPanel.buildCurrentPropObj()

    # Get currently selected/Focused Property
    def getActiveProperty(self):
        return self._activeProperty

    def getOverviewPanel(self):
        return self._overviewPanel

    def getInspectionPanel(self):
        return self._inspectionPanel

    def getOverviewInspectionPanels(self):
        return self._overviewPanel, self._inspectionPanel

    # Creates a panel which shows a overview of all objects in the propertyManager
    def createOverviewPanel(self, parent: wx.Window, inspectionPanel = None):
        if inspectionPanel is None and self._inspectionPanel is not None:
            inspectionPanel = self._inspectionPanel
        else:
            pass #TODO: should something happen if None?
        self._overviewPanel = PropObjectOverviewPanel(manager=self, inspectionPanel=inspectionPanel, parent=parent)

    # Creates a panel which allows to get detailed information about all properties of a PropertyObject
    def createInspectionPanel(self, parent: wx.Window):
        self._inspectionPanel = PropInspectionPanel(manager=self, parent=parent)

    # Combines overview and inspection creation in a more convenient way
    def createOverviewInspectionPanels(self, parent):
        self.createInspectionPanel(parent=parent)
        inspection = self._inspectionPanel
        self.createOverviewPanel(parent=parent, inspectionPanel=inspection), inspection

    def hasOverviewPanel(self):
        return False if self._overviewPanel is None else True

    def hasInspectionPanel(self):
        return False if self._inspectionPanel is None else True



