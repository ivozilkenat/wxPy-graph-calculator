import wx

from MyWx.wx import *
from MyWx.Collection.templates import PanelWithHeaderAccordion
from MyWx.Collection.panels import ListPanel, ListComponent
from MyWx.Collection._core import error, wxUtilities
from MyWx.Collection.format import expanded

from GraphCalc.Components.Property.property import PropertyObject, Property, PropertyCategory, PropCategoryDataClass

from typing import List, Set

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
        self._activeProperty = propertyObject

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

# Panel to show Properties
class PropInspectionPanel(GenericPanel):
    def __init__(self, manager: PropertyManager, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self._manager = manager
        self._inspectedObj: PropertyObject = None
        self._sizerComponent = ListComponent(self, sizerFlags=wx.EXPAND | wx.BOTTOM)

    def setActivePropObj(self, propertyObj: PropertyObject):
        assert isinstance(propertyObj, PropertyObject)
        self._inspectedObj = propertyObj

    def buildCurrentPropObj(self):
        self.buildByPropObj(self._inspectedObj)

    def buildByPropObj(self, propertyObj: PropertyObject):
        #TODO: How to sort property objects / How to update property objects
        self._sizerComponent.clearSizer()


        for i, p in enumerate(propertyObj.properties.values()):
            print(p.getName())
            txtWidth = 100
            txtCtrlProportion = (1, 6)


            #background = wx.Panel(self)
            #background.SetBackgroundColour((250, 250, 250))

            txt = wx.StaticText(parent=self, label=f"{p.getName().capitalize()}:", size=(txtWidth, 0))
            ctrl = p.getInputCtrl(parent=self)

            s1 = wx.BoxSizer(wx.HORIZONTAL)
            s1.Add(txt, 1, wx.EXPAND)
            s1.Add(ctrl, 6, wx.EXPAND) #TODO: export proportions into separate file

            self._sizerComponent.addComponent(s1)
            self._sizerComponent.addComponent(wx.StaticLine(self))
            #self._sizerComponent.addComponent(background)

        self.SetSizer(self._sizerComponent.getSizerAndBuild())

# Panel to Show PropertyObjects by Category
class PropObjectOverviewPanel(GenericMouseScrollPanel):
    def __init__(self, manager: PropertyManager, inspectionPanel: PropInspectionPanel=None, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._inspection = inspectionPanel #<- can be None <- bind event handler dynamically
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
    def createCategory(self, name: str): #<- TODO: should a string object be used instead of PropertyCategory?
        newCategory = PanelWithHeaderAccordion(self, headline=name)
        newCategory.setAllowEmpty(True)
        newCategory.build()
        self.addCategoryPanel(newCategory)

    # Delete Category by String
    def deleteCategory(self, name: str):
        self.removeCategoryPanel(self.categoryNameDict()[name])

    # Add a propertyObj to its correlated category (toggle adding if category has not been created yet)
    # or create new category by string as target
    def addToCategory(self, propertyEntry: PropertyObject, createCategory: bool = True, targetCategory: PropCategoryDataClass = None):
        assert isinstance(propertyEntry, PropertyObject)
        if targetCategory is None:
            categoryName = propertyEntry.getCategory().getName()
        else:
            categoryName = targetCategory.getName() #<- could potentially cause conflicts in the future
            propertyEntry.setCategory(targetCategory)
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

    def removeFromCategory(self, propertyEntry: PropertyObject):
        assert isinstance(propertyEntry, PropertyObject)
        catName = propertyEntry.getCategory().getName()
        catTemp = self.categoryNameDict()[catName]
        lp: ListPanel = catTemp.getContent()
        for panel in lp.getComponents():
            if panel.getPropertyObj() == propertyEntry:
                lp.remove(panel)
                lp.build()
                return

    @GenericMouseScrollPanel.rebuild
    def setCategoryIndex(self, categoryName, newPos):
        assert categoryName in self.categoryNames()
        cat = self.getCategories()
        if newPos < 1:
            newPos = 1
        elif newPos > len(cat):
            newPos = len(cat)
        catObj = self.categoryNameDict()[categoryName]
        cat.remove(catObj)
        cat.insert(newPos, catObj)

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
        accordionPanel.destroy()

    def categoryNames(self):
        return [i.getLabelTxt() for i in self._categories]

    def categoryNameDict(self):
        return {i.getLabelTxt(): i for i in self._categories}

# Panel to represent PropertyObjects
class PropertyObjPanel(GenericPanel):
    def __init__(self, parent, propertyObject: PropertyObject, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._property = propertyObject
        self.SetBackgroundColour((250, 250, 250))
        self._sizer = wx.BoxSizer(wx.VERTICAL)

        self.build()

    #TODO: should be expanded in the future
    def build(self):
        self._sizer.Clear()
        name = self._property.properties["name"].getValue()
        font = wx.Font(13, wx.DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        txt = wx.StaticText(self, label=name, style=wx.ALIGN_CENTER)
        txt.SetFont(font)
        self._sizer.Add(txt, 1, wx.EXPAND)
        self.SetSizer(self._sizer)

    def getPropertyObj(self):
        return self._property

    def setPropertyObj(self, propertyObj: PropertyObject):
        self._property = propertyObj