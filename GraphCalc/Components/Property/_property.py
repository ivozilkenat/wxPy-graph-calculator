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

    def __str__(self):
        return self._name


# implement logic for bounds of properties / further implement necessary logic

class ToggleProperty(Property):
    def __init__(self, propertyName, value):
        assert isinstance(value, bool)
        super().__init__(propertyName, value)


class NumProperty(Property):
    def __init__(self, propertyName, value):
        assert isinstance(value, float) or isinstance(value, int)
        super().__init__(propertyName, value)


class StrProperty(Property):
    def __init__(self, propertyName, value):
        assert isinstance(value, str)
        super().__init__(propertyName, value)


class ContainerProperty(Property):
    def __init__(self, propertyName, value):
        assert isinstance(value, (list, tuple, set))
        super().__init__(propertyName, value)


# Baseclass for all objects, with "properties" (will be ui-relevant)
class PropertyObject(ABC):
    def __init__(self, category):
        self.setCategory(category)
        self._properties: Dict[str, Property] = {}  # Exchange with priority queue (or not?)

    def getProperties(self):
        return self._properties

    def addProperty(self, property: Property):
        self._properties[property._name] = property

    def getCategory(self):
        return self._category

    def setCategory(self, category):
        assert isinstance(category, PropertyCategory)
        self._category = category

class PropertyCategory(Enum):
    FUNCTION = "Funktionen"
    SHAPES = "Formen"
    NO_CATEGORY = "Weiteres"

    # Needed for the object manager to sort by category
    @classmethod
    def categoryDict(cls) -> Dict[TypeVar, list]:
        return {i: [] for i in list(cls)}


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
            if graphicalPanelObject._properties["draw"].getValue() is True:
                blitUpdateMethod(graphicalPanelObject, deviceContext)

        return inner

    # Called by basePlane if redraw is necessary
    @abstractmethod
    def blitUpdate(self, deviceContext):
        pass
