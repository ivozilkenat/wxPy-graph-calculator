import wx

from MyWx.wx import *
from GraphCalc._core._sc import *

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, TypeVar, Set

# Probably unnecessary / Maybe nest Property-classes
class Property(ABC):
    def __init__(self, propertyName: str, value):
        self.setName(propertyName) #constant #TODO: Make dynamic
        self._value = value

    def getName(self):
        return self._name

    def setName(self, propertyName: str):
        self._name = propertyName.lower()

    def getValue(self):
        return self._value

    def setValue(self, value: Any):
        self._value = value

    def __str__(self):
        return self._name

# Superclass for property extension
class StandardCtrl(ABC):
    def __init__(self, updateFunction = None, constant = False):
        self._parameters: Dict = None
        self._updateFunction: callable = updateFunction
        self._control = None
        # Constant properties should not update something, that will be deleted!!! TODO: change implementation?
        self._constant: bool = constant # If a property is constant it won't be removed (only a hint, could be implemented differently)

    # Every child class must defined how the standard control is build
    @abstractmethod
    def getCtrl(self, parent):
        pass

    # Every child must define how the property value changes, when the value is manipulated
    @abstractmethod
    def updateValue(self):
        pass

    def setUpdateFunction(self, callable):
        self._updateFunction = callable

    # Define how control changes updated other dependencies
    def update(self, evt = None):
        self.updateValue()
        self.callUpdFunc(mustUpdate=False)
        evt.Skip()

    def callUpdFunc(self, mustUpdate = True):
        if self._updateFunction is None:
            if mustUpdate:
                raise MyWxException.MissingContent(ERROR_UPDATE_FUNCTION_MISSING)
        else:
            self._updateFunction()

    def isConstant(self):
        return self._constant

    def setConstant(self, state: bool):
        assert isinstance(state, bool)
        self._constant = state

# implement logic for bounds of properties / further implement necessary logic

class ToggleProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value, updateFunction = None, constant = False):
        assert isinstance(value, bool)
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self, updateFunction, constant)

    def getCtrl(self, parent):
        #del self._control #<- must control be deleted?
        self._control = wx.CheckBox(parent=parent)
        self._control.SetValue(self.getValue())
        self._control.Bind(wx.EVT_CHECKBOX, self.update)
        return self._control

    def updateValue(self):
        self.setValue(self._control.GetValue())


class NumProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value, updateFunction = None, constant = False):
        assert isinstance(value, (float, int))
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self, updateFunction, constant)

    def getCtrl(self, parent):
        self._control = wx.SpinCtrl(parent=parent, min=0, initial=self.getValue())
        self._control.Bind(wx.EVT_SPINCTRL, self.update)
        return self._control

    def updateValue(self):
        self.setValue(self._control.GetValue())# TODO: Not Tested


class StrProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value, updateFunction = None, constant = False):
        assert isinstance(value, str)
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self, updateFunction, constant)

    def getCtrl(self, parent):
        self._control = wx.TextCtrl(parent=parent, value=self.getValue(), style=wx.TE_PROCESS_ENTER) #TODO: Add character limit or change PropertyObjectPanel dynamically
        self._control.Bind(wx.EVT_TEXT_ENTER, self.update) #TODO: find out if other event might fit better (e.g. EVT_TEXT)
        return self._control

    def updateValue(self):
        self.setValue(self._control.GetValue())

#TODO: not fully implemented yet
class ContainerProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value, updateFunction = None, constant = False):
        assert isinstance(value, (list, tuple, set))
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self, updateFunction, constant)

    def getCtrl(self, parent):
        pass#TODO: not implemented yet

    def updateValue(self):
        pass#TODO: not implemented yet

class PropCategoryDataClass:
    def __init__(self, categoryName: str):
        self.name = categoryName

    # Convenient-method for readability
    def getName(self):
        return self.name

class PropertyCategory(Enum):
    FUNCTION = PropCategoryDataClass(PROPERTY_CAT_FUNC)
    SHAPES = PropCategoryDataClass(PROPERTY_CAT_SHAPE)
    NO_CATEGORY = PropCategoryDataClass(PROPERTY_CAT_MISC)

    # Needed for the object manager to sort by category
    @classmethod
    def categoryDict(cls) -> Dict[TypeVar, list]:
        return {i: [] for i in list(cls)}

    # Convenient-method for object creation
    @classmethod
    def CUSTOM_CATEGORY(cls, name: str) -> PropCategoryDataClass:
        return PropCategoryDataClass(name)

    def getName(self):
        return self.value.name

    def getCat(self):
        return self.value

### PROPERTY-OBJECTS

# Baseclass for all objects, with "properties" (will be ui-relevant)
class PropertyObject(ABC):
    def __init__(self, category: PropCategoryDataClass):
        self.setCategory(category)
        self._properties: Dict[str, Property] = {}  # Exchange with priority queue (or not?)

        self.addProperty(StrProperty(PROPERTY_NAME, PROPERTY_NAME_PLACEHOLDER, constant=True))
    def _validPropertyKey(method):
        def inner(object, key, *args, **kwargs):
            try:
                return method(object, key, *args, **kwargs)
            except KeyError:
                raise MyWxException.MissingContent(f"Property with name '{key}' does not exist") #todo: <- outource such strings?
        return inner

    def addProperty(self, property: Property, override = False):
        if not override:
            if (name := property.getName()) in self._properties:
                raise MyWxException.AlreadyExists(f"property with name '{name}' already exists")
        self._properties[property._name] = property


    @_validPropertyKey
    def removeProperty(self, name):
        del self._properties[name]

    @_validPropertyKey
    def getProperty(self, name):
        return self._properties[name]

    def getProperties(self):
        return tuple(self._properties.values())

    @_validPropertyKey
    def setPropertyName(self, oldName, newName):
        self._properties[newName] = self._properties.pop(oldName)
        self._properties[newName].setName(newName)

    def getCategory(self):
        return self._category

    def setCategory(self, category):
        assert isinstance(category, (PropCategoryDataClass, PropertyCategory))
        if isinstance(category, PropCategoryDataClass):
            self._category = category
        else:
            self._category = category.getCat()

    def clear(self, clearConstant = False):
        if clearConstant:
            self._properties = {}
        else:
            n = list()
            for i in self._properties:
                if self._properties[i].isConstant() is False:
                    n.append(i)
            for  i in n:
                self.removeProperty(i)

#TODO: This class and derived do not account for manager changing and thereby if any property is added dynamically,
#       they wont update the correct manager if manager is changed -> sol: 1. add support 2. disable dynamic properties
class ManagerPropertyObject(PropertyObject, ABC):
    def __init__(self, category: PropCategoryDataClass, manager=None):
        super().__init__(category)
        self._manager = manager  # TODO: Is this sensible


    def setManager(self, manager):
        self._manager = manager
        p = self.getProperty(PROPERTY_NAME)
        p.setUpdateFunction(self.updateOverviewPanel)
        self.addProperty(p, override=True)

    def hasManager(self):
        return True if self._manager is not None else False

    def getOverview(self):
        if self.hasManager():
            if self._manager.hasOverviewPanel():
                return self._manager.getOverviewPanel()
            else:
                raise MyWxException.MissingContent(ERROR_MISSING_INSPECTION)
        else:
            raise MyWxException.MissingContent(ERROR_MISSING_PROP_MAN)

    def updateOverviewPanel(self):
        self.getOverview().updatePropertyPanels()

# Baseclass for graphical objects, which lie on top of a base panel
class GraphicalPanelObject(ManagerPropertyObject, ABC):
    def __init__(self, basePlane=None, category=PropertyCategory.NO_CATEGORY):
        super().__init__(category=category)
        self._basePlane = basePlane

    def setBasePlane(self, plane):
        self.clear()
        self._basePlane = plane
        self.addProperty(ToggleProperty(PROPERTY_DRAW, True, updateFunction=self.refreshBasePlane))

    def refreshBasePlane(self):
        self._basePlane.Refresh()

    # Decorator for blitUpdateMethod to use standardized properties
    @staticmethod
    def standardProperties(blitUpdateMethod):
        def inner(graphicalPanelObject, deviceContext):
            assert isinstance(graphicalPanelObject, GraphicalPanelObject)

            if graphicalPanelObject.getProperty(PROPERTY_DRAW).getValue() is True: #<- standard property
                blitUpdateMethod(graphicalPanelObject, deviceContext)
        return inner

    # Called by basePlane if redraw is necessary
    @abstractmethod
    def blitUpdate(self, deviceContext):
        pass