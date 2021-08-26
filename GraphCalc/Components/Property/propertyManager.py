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
        self._categorySizerC = CategoryOverviewComponent(self)
        #TODO: implement ordering
        self.build()

    def build(self):
        self.SetSizer(self._categorySizerC.getSizerAndBuild())

    @GenericMouseScrollPanel.rebuild
    def addCategoryPanel(self, category: PanelWithHeaderAccordion):
        assert isinstance(category, PanelWithHeaderAccordion)
        self._categorySizerC.addCategoryComponent(category)

    @GenericMouseScrollPanel.rebuild
    def removeCategoryPanel(self, category: PanelWithHeaderAccordion):
        assert isinstance(category, PanelWithHeaderAccordion)
        self._categorySizerC.removeCategoryComponent(category)

    def createCategory(self, name: str):
        newCategory = PanelWithHeaderAccordion(self, headline=name)
        newCategory.setAllowEmpty(True)
        newCategory.build()
        self.addCategoryPanel(newCategory)

    def deleteCategory(self, name: str):
        self.removeCategoryPanel(self.categoryNameDict()[name])

    def categoryNameDict(self):
        return {i.getLabelTxt(): i for i in self._categorySizerC.getCategories()}

    def categoryNames(self):
        return [i.getLabelTxt() for i in self._categorySizerC.getCategories()]

    #TODO: Not implemented yet
    def _setupHandlers(self):
        for c in self._categorySizerC.getCategories():
            tabs = c.getContent()
            for t in tabs:
                t.Bind(wx.EVT_LEFT_DOWN, self._changeActiveProperty)


    def _changeActiveProperty(self, evt: wx.MouseEvent=None):
        #TODO: must be finished
        self._manager.setActiveProperty(evt.GetEventObject().GetPropertyObj())


class CategoryOverviewComponent(SizerComponent):
    def __init__(self, parent):
        super().__init__(parent)
        self._categories: List[PanelWithHeaderAccordion, ...] = list()
        self._sizer = wx.BoxSizer(wx.VERTICAL)

    def getCategories(self):
        return self._categories

    def addCategoryComponent(self, sizerComponent: PanelWithHeaderAccordion):
        assert isinstance(sizerComponent, PanelWithHeaderAccordion)
        self._categories.append(sizerComponent)

    def removeCategoryComponent(self, sizerComponent: PanelWithHeaderAccordion):
        assert isinstance(sizerComponent, PanelWithHeaderAccordion)
        self._categories.remove(sizerComponent)

    def build(self):
        self._sizer.Clear()
        print(len(self._categories), self._sizer)
        for c in self._categories:
            print(c, "Category object")
            print(c.getLabelTxt())
            print(c.getSizer())
            print()
            #Child sizers are deleted, as a consequence of detachment
            self._sizer.Add(c.getSizer(), 0, wx.EXPAND | wx.BOTTOM, 5) #border ?


class PropertyObjPanel(GenericPanel):
    def __init__(self, parent, propertyObject: PropertyObject, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._property = propertyObject
        
    def getPropertyObj(self):
        return self._property

    def setPropertyObj(self, propertyObj: PropertyObject):
        self._property = propertyObj
        