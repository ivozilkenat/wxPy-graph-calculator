import wx

from MyWx.wx import *
from GraphCalc._core.utilities import *

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, TypeVar


# Probably unnecessary / Maybe nest Property-classes
class Property(ABC):
    def __init__(self, propertyName, value):
        self._name = str(propertyName)
        self._value = value

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def setValue(self, value: Any):
        self._value = value

    def __str__(self):
        return self._name

class StandardCtrl(ABC):
    def __init__(self):
        self._input = None
        self._parameters: Dict = None

    def getInputCtrl(self, parent, *args, **kwargs):
        if self._input is None:
            raise MyWxException.MissingContent("There was no standard wx.Control defined")
        return self._input(parent, *args, **self._parameters, **kwargs)

    def setInputCtrl(self, inputElement, parameters: Dict = dict()):
        self._input = inputElement
        self._parameters = parameters



# implement logic for bounds of properties / further implement necessary logic

class ToggleProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value):
        assert isinstance(value, bool)
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self)
        self.setInputCtrl(
            inputElement=wx.CheckBox,
        )


class NumProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value):
        assert isinstance(value, float) or isinstance(value, int)
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self)
        self.setInputCtrl(
            inputElement=wx.SpinCtrl,
            parameters={
                "min": "0",
                "initial": "0"
            }
        )

class StrProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value):
        assert isinstance(value, str)
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self)
        self.setInputCtrl(
            inputElement=wx.TextCtrl,
            parameters={
                "value": "PLACEHOLDER"
            }
        )


class ContainerProperty(Property, StandardCtrl):
    def __init__(self, propertyName, value):
        assert isinstance(value, (list, tuple, set))
        Property.__init__(self, propertyName, value)
        StandardCtrl.__init__(self)
        self.setInputCtrl(
            inputElement=wx.TextCtrl,
            parameters={
                "value": "PLACEHOLDER"
            }
        )

class PropCategoryDataClass:
    def __init__(self, categoryName: str):
        self.name = categoryName

    # Convenient-method for readability
    def getName(self):
        return self.name

class PropertyCategory(Enum):
    FUNCTION = PropCategoryDataClass("Funktionen")
    SHAPES = PropCategoryDataClass("Formen")
    NO_CATEGORY = PropCategoryDataClass("Weiteres")

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

# Baseclass for all objects, with "properties" (will be ui-relevant)
class PropertyObject(ABC):
    def __init__(self, category: PropCategoryDataClass):
        self.setCategory(category)
        self.properties: Dict[str, Property] = {}  # Exchange with priority queue (or not?)

        self.addProperty(StrProperty("name", "NO_NAME"))# <- TODO: outsource such constant values

    def addProperty(self, property: Property):
        self.properties[property._name] = property

    def getCategory(self):
        return self._category

    def setCategory(self, category):
        assert isinstance(category, (PropCategoryDataClass, PropertyCategory))
        if isinstance(category, PropCategoryDataClass):
            self._category = category
        else:
            self._category = category.getCat()


# Baseclass for graphical objects, which lie on top of a base panel
class GraphicalPanelObject(PropertyObject, ABC):
    def __init__(self, basePlane=None, category=PropertyCategory.NO_CATEGORY):
        super().__init__(category=category)
        self.basePlane = basePlane

        self.addProperty(ToggleProperty("draw", True))

    # Decorator for blitUpdateMethod to use standardized properties
    @staticmethod
    def standardProperties(blitUpdateMethod):
        def inner(graphicalPanelObject, deviceContext):
            assert isinstance(graphicalPanelObject, GraphicalPanelObject)
            if graphicalPanelObject.properties["draw"].getValue() is True: #<- standard property
                blitUpdateMethod(graphicalPanelObject, deviceContext)

        return inner

    # Called by basePlane if redraw is necessary
    @abstractmethod
    def blitUpdate(self, deviceContext):
        pass