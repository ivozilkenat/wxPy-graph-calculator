import wx

from MyWx.wx import *
from MyWx.Collection.templates import PanelWithHeaderAccordion
from MyWx.Collection.panels import ListPanel, ListComponent
from MyWx.Collection._core import error

from GraphCalc.Components.Property._property import PropertyObject, Property, PropertyCategory

from typing import List, Set

from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Graphical.graphUtilities import CartesianAxies

# Base class to handle everything related to propertyObject organization
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
        categoryDic = PropertyCategory.categoryDict()
        for p in self._propertyObjects:
            categoryDic[p.getCategory()].append(p)
        return categoryDic

    # Set currently selected/Focused Property
    def setActiveProperty(self, propertyObject: PropertyObject):
        self._activeProperty = propertyObject

    # Get currently selected/Focused Property
    def getActiveProperty(self):
        return self._activeProperty

    # Creates a panel which shows a overview of all objects in the propertyManager
    def createOverviewPanel(self, parent: wx.Window, inspectionPanel):
        return PropObjectOverviewPanel(manager=self, inspectionPanel=inspectionPanel, parent=parent)

    # Creates a panel which allows to get detailed information about all properties of a PropertyObject
    def createInspectionPanel(self, parent: wx.Window):
        return PropInspectionPanel(manager=self, parent=parent)

    # Combines overview and inspection creation in a more convenient way
    def createOverviewInspectionPanels(self, parent):
        inspection = self.createInspectionPanel(parent=parent)
        return self.createOverviewPanel(parent=parent, inspectionPanel=inspection), inspection

# Panel to show Properties
class PropInspectionPanel(GenericPanel):
    def __init__(self, manager: PropertyManager, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self._manager = manager

    def setActiveProperty(self, property: PropertyObject):
        pass

# Panel to Show PropertyObjects by Category
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

    # Create a new Category by string
    def createCategory(self, name: str):
        newCategory = PanelWithHeaderAccordion(self, headline=name)
        newCategory.setAllowEmpty(True)
        newCategory.build()
        self.addCategoryPanel(newCategory)

    # Delete Category by String
    def deleteCategory(self, name: str):
        self.removeCategoryPanel(self.categoryNameDict()[name])

    # Add a propertyObj to its correlated category (toggle adding if category has not been created yet)
    # or create new category by string as target
    def addToCategory(self, propertyEntry: PropertyObject, createCategory: bool = True, targetCategory: str = None):
        assert isinstance(propertyEntry, PropertyObject)
        categoryName = propertyEntry.getCategory().value if targetCategory is None else targetCategory #<- could potentially cause conflicts in the future
        if not self.categoryExits(categoryName) and createCategory:
            self.createCategory(categoryName)
        else:
            MyWxException.NotExistent(f"Category '{categoryName}' does not exist")
        categoryTemp = self.categoryNameDict()[categoryName]
        if categoryTemp.isEmpty():
            lp = ListPanel(self)
            lp._listComponent = ListComponent(lp, sizerFlags=wx.EXPAND | wx.BOTTOM, padding=1)
            categoryTemp.setContent(lp)

        lp: ListPanel = categoryTemp.getContent()
        panel = PropertyObjPanel(parent=lp, propertyObject=propertyEntry, size=(0, 50))#TODO: unfinished / does not display anything yet
        lp.add(panel)
        lp.build()

    # Check if a category exists
    def categoryExits(self, categoryName: str):
        if categoryName in self.categoryNames():
            return True
        return False

    def getCategories(self):
        return self._categorySizerC._categories

    def categoryNameDict(self) -> Dict[str, PanelWithHeaderAccordion]:
        return self._categorySizerC.categoryNameDict()

    def categoryNames(self):
        return self._categorySizerC.categoryNames()

    # Setup a set of handlers to check if any propertyObj has been selected
    #TODO: Not implemented yet
    def _setupHandlers(self):
        for c in self.getCategories():
            tabs = c.getContent()
            for t in tabs:
                t.Bind(wx.EVT_LEFT_DOWN, self._changeActiveProperty)

    # Event handler for propertyObj selection
    def _changeActiveProperty(self, evt: wx.MouseEvent=None):
        #TODO: must be finished
        self._manager.setActiveProperty(evt.GetEventObject().GetPropertyObj())

# SizerComponent to manage accordionPanels
class CategoryOverviewComponent(SizerComponent):
    def __init__(self, parent):
        super().__init__(parent)
        self._categories: List[PanelWithHeaderAccordion, ...] = list()
        self._sizer = wx.BoxSizer(wx.VERTICAL)

    def build(self):
        self.clearSizer()
        for c in self._categories:
            self._sizer.Add(c.getSizer(), 0, wx.EXPAND | wx.BOTTOM, 5)  # border ?

    def addCategoryComponent(self, accordionPanel: PanelWithHeaderAccordion):
        assert isinstance(accordionPanel, PanelWithHeaderAccordion)
        if accordionPanel.getLabelTxt() in self.categoryNames():
            raise MyWxException.AlreadyExists(f"Category of name '{accordionPanel.getLabelTxt()}' already exists")
        self._categories.append(accordionPanel)

    def removeCategoryComponent(self, accordionPanel: PanelWithHeaderAccordion):
        assert isinstance(accordionPanel, PanelWithHeaderAccordion)
        self._categories.remove(accordionPanel)

    def categoryNames(self):
        return [i.getLabelTxt() for i in self._categories]

    def categoryNameDict(self):
        return {i.getLabelTxt(): i for i in self._categories}

# Panel to represent PropertyObjects
class PropertyObjPanel(GenericPanel):
    def __init__(self, parent, propertyObject: PropertyObject, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._property = propertyObject
        from MyWx.Collection._core.wxUtilities import randomRGBTriple

        self.SetBackgroundColour(randomRGBTriple())

    def getPropertyObj(self):
        return self._property

    def setPropertyObj(self, propertyObj: PropertyObject):
        self._property = propertyObj
        