import wx

from MyWx.wx import *
from MyWx.Collection.templates import PanelWithHeaderAccordion
from MyWx.Collection.panels import ListPanel, ListComponent
from GraphCalc._core._sc import *

from GraphCalc.Components.Property.PropertyManager.propertyInspection import PropInspectionPanel
from GraphCalc.Components.Property.property import PropertyObject, PropCategoryDataClass


# Panel to Show PropertyObjects by Category
class PropObjectOverviewPanel(GenericMouseScrollPanel):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._activePanel = None
        self._categorySizerC = CategoryOverviewComponent(self)
        self.SetBackgroundColour((250, 250, 250))
        # TODO: implement ordering
        self.build()

    def build(self):
        self.SetSizer(self._categorySizerC.getSizerAndBuild())

    # build and refresh all contained panels
    @GenericMouseScrollPanel.rebuild
    def updatePropertyPanels(self):
        for p in self.getPropertyPanels():
            p.build()
        self.Refresh()  # TODO: Is this a hacky solution?
        # TODO: not working correctly, problem with text boxes

    # get all panels that represent property-objects
    def getPropertyPanels(self):
        panels = list()
        for i in self._categorySizerC._categories:
            if (content := i.getContent()) is not None:
                for j in content.getComponents():
                    panels.append(j)
        return panels

    # get all categorized propertyObjects
    def getPropertyObjects(self):
        propObjs = list()
        for i in self._categorySizerC._categories:
            if (content := i.getContent()) is not None:
                for j in content.getComponents():
                    propObjs.append(j.getPropertyObj())
        return propObjs

    # add a valid category panel
    @GenericMouseScrollPanel.rebuild
    def addCategoryPanel(self, category: PanelWithHeaderAccordion):
        assert isinstance(category, PanelWithHeaderAccordion)  # todo: add further type checking?
        self._categorySizerC.addCategoryComponent(category)

    # remove a valid category panel
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
    def addToCategory(self, propertyEntry: PropertyObject, createCategory: bool = True,
                      targetCategory: PropCategoryDataClass = None):
        assert isinstance(propertyEntry, PropertyObject)
        if targetCategory is None:
            categoryName = propertyEntry.getCategory().getName()
        else:
            categoryName = targetCategory.getName()  # <- could potentially cause conflicts in the future
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
        panel = PropertyObjPanel(parent=lp, propertyObject=propertyEntry,
                                 size=(0, 50))  # TODO: unfinished / does not display anything yet
        panel._text.Bind(wx.EVT_LEFT_UP, self._changeActiveProperty)

        lp.add(panel)
        lp.build()

    # remove property-object
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

    # set position of category
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

    # get all categories (accordion panels)
    def getCategories(self):
        return self._categorySizerC._categories

    # get a dict of all category names and their according content
    def categoryNameDict(self) -> Dict[str, PanelWithHeaderAccordion]:
        return self._categorySizerC.categoryNameDict()

    # get all category names
    def categoryNames(self):
        return self._categorySizerC.categoryNames()

    # get the panel of a specified property-object
    def getPanelOfProperty(self, propertyObj: PropertyObject):
        for p in self.getPropertyPanels():
            if propertyObj == p.getPropertyObj():
                return p
        return None

    # highlight a specified property-object
    def highlightProperty(self, propertyObj: PropertyObject):
        panel = self.getPanelOfProperty(propertyObj)
        if self._activePanel is not None:
            self._activePanel.SetBackgroundColour(PropertyObjPanel.STD_COLOR)
        panel.SetBackgroundColour(PropertyObjPanel.SELECT_COLOR)
        self._activePanel = panel
        self.Refresh()  # <- should this be called here?

    # Event handler for propertyObj selection
    def _changeActiveProperty(self, evt: wx.MouseEvent = None):
        txt = evt.GetEventObject()
        panel = txt.GetParent()
        self._manager.setActiveProperty(panel.getPropertyObj())


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

    # add new category as accordion panel
    def addCategoryComponent(self, accordionPanel: PanelWithHeaderAccordion):
        assert isinstance(accordionPanel, PanelWithHeaderAccordion)
        if accordionPanel.getLabelTxt() in self.categoryNames():
            raise MyWxException.AlreadyExists(f"Category of name '{accordionPanel.getLabelTxt()}' already exists")
        self._categories.append(accordionPanel)

    # remove an existing category
    def removeCategoryComponent(self, accordionPanel: PanelWithHeaderAccordion):
        assert isinstance(accordionPanel, PanelWithHeaderAccordion)
        self._categories.remove(accordionPanel)
        accordionPanel.destroy()

    # get all category names
    def categoryNames(self):
        return [i.getLabelTxt() for i in self._categories]

    # get all category names and their represented accordion panel
    def categoryNameDict(self):
        return {i.getLabelTxt(): i for i in self._categories}


# Panel to represent PropertyObjects
class PropertyObjPanel(GenericPanel):
    STD_COLOR = (250, 250, 250)
    SELECT_COLOR = (220, 220, 220)  # <- TODO: outsource values

    def __init__(self, parent, propertyObject: PropertyObject, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._property = propertyObject
        self.SetBackgroundColour(self.STD_COLOR)
        self._sizer = wx.BoxSizer(wx.VERTICAL)

        self._text = wx.StaticText(self, label=self._property._properties[PROPERTY_NAME].getValue(),
                                   style=wx.ALIGN_CENTER)

        self.build()

    # TODO: should be expanded in the future
    def build(self):
        self._sizer.Clear()
        name = self._property._properties[PROPERTY_NAME].getValue()
        self._text.SetLabel(name)
        font = wx.Font(13, wx.DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self._text.SetFont(font)
        self._sizer.Add(self._text, 1, wx.EXPAND)
        self.SetSizer(self._sizer)

    def getPropertyObj(self):
        return self._property

    def setPropertyObj(self, propertyObj: PropertyObject):
        self._property = propertyObj
