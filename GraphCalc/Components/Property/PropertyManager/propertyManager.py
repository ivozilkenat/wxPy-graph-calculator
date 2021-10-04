import wx

from MyWx.wx import *
from wx.lib.newevent import NewEvent

from GraphCalc.Components.Property.PropertyManager.propertyOverview import PropObjectOverviewPanel
from GraphCalc.Components.Property.PropertyManager.propertyInspection import PropInspectionPanel
from GraphCalc.Components.Property.property import IExprProperty, ExprProperty, PropertyObject, ManagerPropertyObject, PropertyObjCategory

from typing import Set


# TODO: -allow for sorting of properties and categorize them


# Base class to handle everything related to propertyObject organization
class PropertyManager:
    def __init__(self):
        self._propertyObjects: Set[PropertyObject] = set()
        self._activeProperty = None  # <- shown in the inspection panel / highlighted in the managed object (if possible)

        self._overviewPanel: PropObjectOverviewPanel = None
        self._inspectionPanel: PropInspectionPanel = None

        # Extend the PropertyManager-class to fit desired needs, e.g. Graph Plane

    # get all managed property-objects
    def getPropertyObjects(self):
        return self._propertyObjects

    # add property object / if initialized add property-object to the overview panel
    def addPropertyObject(self, propertyObject: PropertyObject, addToOverview=True):
        assert isinstance(propertyObject, ManagerPropertyObject)
        self._propertyObjects.add(propertyObject)
        propertyObject.setManager(self)
        if self._overviewPanel is not None and addToOverview is True and not propertyObject.isHidden():
            self._overviewPanel.addToCategory(propertyObject)

    # remove property object / if initialized remove property-object from overview panel
    def removePropObject(self, propertyObject: PropertyObject):
        assert isinstance(propertyObject, PropertyObject)
        self._propertyObjects.remove(propertyObject)
        if self._overviewPanel is not None:
            if propertyObject in self._overviewPanel.getPropertyObjects():
                self._overviewPanel.removeFromCategory(propertyObject)

    # undefines all expression properties of property-object
    def undefinePropObject(self, propertyObject: PropertyObject):
        if isinstance(propertyObject, IExprProperty):
            for p in propertyObject.getPropertyDict().values():
                if isinstance(p, ExprProperty):
                    p.undefine()

    def removeUndefinePropObject(self, propertyObject: PropertyObject):
        self.undefinePropObject(propertyObject)
        self.removePropObject(propertyObject)

    # get dict of categories and their property-objects
    def getPropertiesByCategory(self):

        categoryDic = PropertyObjCategory.categoryDict()
        for p in self._propertyObjects:
            categoryDic[p.getCategory()].append(p)
        return categoryDic

    # Set currently selected/Focused Property
    def setActiveProperty(self, propertyObject: PropertyObject):
        equal = self._activeProperty == propertyObject
        self._activeProperty = propertyObject
        if self.hasInspectionPanel() and not equal:
            self._inspectionPanel.setActivePropObj(self._activeProperty)
            self._inspectionPanel.buildInspectedPropertyObj()
        if self.hasOverviewPanel():
            self._overviewPanel.highlightProperty(propertyObject)

    def clearActiveProperty(self):
        if self.hasInspectionPanel():
            self._inspectionPanel.setActivePropObj(None)
            self._inspectionPanel.buildInspectedPropertyObj()
        if self.hasOverviewPanel():
            self._overviewPanel.clearHighlighting()
            self._overviewPanel._setActivePropertyPanel(None)

    # Get currently selected/Focused Property
    def getActiveProperty(self):
        return self._activeProperty

    # get overview-panel
    def getOverviewPanel(self):
        return self._overviewPanel

    # get inspection-panel
    def getInspectionPanel(self):
        return self._inspectionPanel

    # get tuple of overview and inspection panel
    def getOverviewInspectionPanels(self):
        return self._overviewPanel, self._inspectionPanel

    # Creates a panel which shows a overview of all objects in the propertyManager
    def createOverviewPanel(self, parent: wx.Window, **panelKwargs):
        self._overviewPanel = PropObjectOverviewPanel(manager=self, parent=parent, **panelKwargs)

    # Creates a panel which allows to get detailed information about all properties of a PropertyObject
    def createInspectionPanel(self, parent: wx.Window, **panelKwargs):
        self._inspectionPanel = PropInspectionPanel(manager=self, parent=parent, **panelKwargs)

    # Combines overview and inspection creation in a more convenient way
    def createOverviewInspectionPanels(self, parent):
        return self.createOverviewPanel(parent=parent), self.createInspectionPanel(parent=parent)

    # check if overview panel has been initialized
    def hasOverviewPanel(self):
        return False if self._overviewPanel is None else True

    # check if inspection panel has been initialized
    def hasInspectionPanel(self):
        return False if self._inspectionPanel is None else True

    # redefines expression of every single expression property
    def redefineAllExpressions(self):
        for o in self.getPropertyObjects():
            if o != self and isinstance(o, IExprProperty):
                for p in o.getPropertyDict().values():
                    if isinstance(p, ExprProperty):
                        p.redefineExisting()


ActiveSetEvent, EVT_ACT_PROP_SET = NewEvent()
ActiveChangedEvent, EVT_ACT_PROP_CH = NewEvent()


# extension that emits events, e.g. selection changed
class PropertyManagerPostEvent(PropertyManager):
    def __init__(self, parent: wx.Window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent

    def setActiveProperty(self, propertyObject: PropertyObject):
        new = propertyObject != self._activeProperty
        super().setActiveProperty(propertyObject)
        wx.PostEvent(self._parent.GetEventHandler(), ActiveSetEvent(selected=propertyObject))
        if new:
            wx.PostEvent(self._parent.GetEventHandler(), ActiveChangedEvent(selected=propertyObject))
