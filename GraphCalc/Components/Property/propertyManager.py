import wx

from MyWx.wx import *
from MyWx.Collection.templates import PanelWithHeaderAccordion
from MyWx.Collection.panels import RandomPanel

from GraphCalc.Components.Property._property import PropertyObject

from typing import List, Set

from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Graphical.graphUtilities import CartesianAxies

class PropertyManager:
    def __init__(self):
        self._propertyObjects: Set[PropertyObject] = set()
        self._activeProperty = None #<- shown in the inspection panel / highlighted in the managed object (if possible)
        # Extend the PropertyManager-class to fit desired needs, e.g. Graph Plane

    def getPropObjects(self):
        return self._propertyObjects

    def addPropObject(self, propertyObject: PropertyObject):
        assert isinstance(propertyObject, PropertyObject)
        self._propertyObjects.add(propertyObject)

    def removePropObject(self, propertyObject: PropertyObject):
        assert isinstance(propertyObject, PropertyObject)
        self._propertyObjects.remove(propertyObject)

    def getPropertiesByCategory(self):
        categoryDic = PropertyObject.Category.categoryDict()
        for p in self._propertyObjects:
            categoryDic[p.getCategory()].append(p)
        return categoryDic

    def setActiveProperty(self, propertyObject: PropertyObject):
        self._activeProperty = propertyObject

    def getActiveProperty(self):
        return self._activeProperty

    def createOverviewPanel(self, parent: wx.Window, inspectionPanel):
        return PropObjectOverviewPanel(manager=self, inspectionPanel=inspectionPanel, parent=parent)

    def createInspectionPanel(self, parent: wx.Window):
        return PropInspectionPanel(manager=self, parent=parent)

    def createOverviewInspectionPanels(self, parent):
        inspection = self.createInspectionPanel(parent=parent)
        return self.createOverviewPanel(parent=parent, inspectionPanel=inspection), inspection


class PropInspectionPanel(GenericPanel):
    def __init__(self, manager: PropertyManager, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self._manager = manager

    def setActiveProperty(self, property: PropertyObject):
        pass

class PropObjectOverviewPanel(GenericMouseScrollPanel):
    def __init__(self, manager: PropertyManager, inspectionPanel: PropInspectionPanel, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._inspection = inspectionPanel

        self._categorySizerC = CategoryOverview(self)
        # self._categorySizerC.addCategoryPanel(TabPanel(self, (0, 60)))
        # self._categorySizerC.addCategoryPanel(TabPanel(self, (0, 60)))
        # self._categorySizerC.addCategoryPanel(TabPanel(self, (0, 60)))
        # self._categorySizerC.addCategoryPanel(TabPanel(self, (0, 60)))

        for i in range(10):
            self._categorySizerC.addCategoryComponent(
                PanelWithHeaderAccordion(parent=self, headline=f"Kategorie {i}", content=RandomPanel(self, (0, 100))).getBuild())


        # self._categorySizerC.addCategoryComponent(PanelWithHeaderAccordion(parent=self, headline="Kategorie", content=RandomPanel(self, (0, 50))))



        self.SetSizer(self._categorySizerC.getSizerAndBuild())


    def build(self, evt = None):
        pass

    def _changeActiveProperty(self):
        pass

    def _updatePanel(self): #should not be a extra method?
        self._sizer.build()


class CategoryOverview(SizerComponent):
    def __init__(self, parent):
        super().__init__(parent)
        self._categories = list()
        self._sizer = wx.BoxSizer(wx.VERTICAL)

    def addCategoryComponent(self, sizerComponent: PanelWithHeaderAccordion):
        assert isinstance(sizerComponent, PanelWithHeaderAccordion)
        self._categories.append(sizerComponent)

    def build(self):
        self._sizer.Clear()
        for c in self._categories:
            self._sizer.Add(c._sizer, 0, wx.EXPAND | wx.BOTTOM, 5) #border ?