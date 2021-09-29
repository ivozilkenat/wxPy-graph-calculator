import wx

from MyWx.wx import *
from GraphCalc._core import vc

from GraphCalc._core.utilities import timeMethod

from GraphCalc.Calc.GraphCalculator import ExprObj

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, TypeVar, Union, List, Tuple, Set, Callable


# Probably unnecessary / Maybe nest Property-classes
# todo: add priority to display in specified order
class Property(ABC):
    def __init__(self, propertyName: str, value):
        self.setName(propertyName)  # constant #TODO: Make dynamic
        self._value = value

    def getName(self):
        return self._name

    def setName(self, propertyName: str):
        self._name = propertyName.lower()

    def getValue(self):
        return self._value

    def _setValue(self, value: Any):
        self._value = value

    def __str__(self):
        return self._name


# Superclass for property extension
class PropertyCtrl(Property, ABC):
    # Import for Dependent property, since it sets value of its properties
    setterSupport: bool = False
    def __init__(self, propertyName, value, updateFunctions=None, validityFunction=None, constant=False):
        super().__init__(propertyName, value)
        self._parameters: Dict = None #todo: redundant?
        if not isinstance(updateFunctions, set):
            if isinstance(updateFunctions, (tuple, set)):
                updateFunctions = list(updateFunctions)
            else:
                updateFunctions = [updateFunctions]
        self._updateFunctions: List[Callable, ...] = updateFunctions
        self._control = None
        self._validityFunction: callable = validityFunction
        self._inputBeforeValidation = None

        # Constant properties should not update something, that will be deleted!!! TODO: change implementation?
        self._constant: bool = constant  # If a property is constant it won't be removed (only a hint, could be implemented differently)

        self._setupCtrlWrapper()

    # Every child class must defined how the standard control is build
    @abstractmethod
    def getCtrl(self, parent):
        pass

    # Every child must define how the property value changes, when the value is manipulated
    @abstractmethod
    def updateValue(self):
        pass

    def setUpdateFunctions(self, *callables):
        self._updateFunctions = list(callables)

    def addUpdateFunctions(self, *callables):
        self._updateFunctions += list(callables)

    def validInput(self, inputData):
        raise NotImplementedError

    # general method for validity checking, does not have to be implemented
    # -> logic can be implemented "manually" in setValue method
    def setValidValue(self, value, raiseInvalidTypeError=False):
        if value == self._inputBeforeValidation:
            return False  # todo: should this be False?
        if self._validityFunction is not None:
            try:
                if not self._validityFunction(value):
                    self._control.SetValue(self._inputBeforeValidation)
                    return False
            except TypeError:
                if raiseInvalidTypeError:
                    raise TypeError("the validity function has received an invalid argument type")
                else:
                    return False
        else:
            self._setValue(value)
            if self._control is not None:
                self._inputBeforeValidation = self._control.GetValue()
            return True

    def setValidValueCtrl(self, value, raiseInvalidTypeError):
        self.setValidValue(value, raiseInvalidTypeError)
        if self._control is not None:
            self._control.SetValue(self._value)

    # input not sanitized
    def _setValueCtrl(self, value):
        self._setValue(value)
        if self._control is not None:
            self._control.SetValue(self._value)

    # Define how control changes updated other dependencies
    def update(self, evt=None):
        self.updateValue()
        self.callUpdFunc(mustUpdate=False)
        # Skip must not be called on enter

    def callUpdFunc(self, mustUpdate=True):
        if self._updateFunctions is None:
            if mustUpdate:
                raise MyWxException.MissingContent(vc.ERROR_UPDATE_FUNCTION_MISSING)
        else:
            for f in self._updateFunctions:
                f()

    def __getCtrlWrapper(self, parent):
        r = self.__getCtrl(parent)
        self._inputBeforeValidation = r.GetValue()  # Set standardized value
        return r

    def _setupCtrlWrapper(self):
        self.__getCtrl = self.getCtrl
        self.getCtrl = self.__getCtrlWrapper

    def isConstant(self):
        return self._constant

    def setConstant(self, state: bool):
        assert isinstance(state, bool)
        self._constant = state

    @classmethod
    def hasSetterSupport(cls):
        return cls.setterSupport

# implement logic for bounds of properties / further implement necessary logic


class ToggleProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, value, updateFunctions=None, constant=False):
        assert isinstance(value, bool)
        super().__init__(propertyName=propertyName, value=value, updateFunctions=updateFunctions, constant=constant)

    def getCtrl(self, parent):
        # del self._control #<- must control be deleted?
        self._control = wx.CheckBox(parent=parent)
        self._control.SetValue(self.getValue())
        self._control.Bind(wx.EVT_CHECKBOX, self.update)
        return self._control

    def updateValue(self):
        self._setValue(self._control.GetValue())


class IntProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, value, updateFunctions=None, validityFunction=None, constant=False,
                 updateOnEnter=False):
        assert isinstance(value, int)
        super().__init__(propertyName=propertyName, value=value, updateFunctions=updateFunctions,
                         validityFunction=validityFunction, constant=constant)
        self._updateOnlyOnEnter = updateOnEnter

    def getCtrl(self, parent):
        self._control = wx.SpinCtrl(parent=parent, min=0, max=999999999, initial=self.getValue(),
                                    style=wx.TE_PROCESS_ENTER)
        self._control.Bind(wx.EVT_TEXT_ENTER, self.update)
        if not self._updateOnlyOnEnter:
            self._control.Bind(wx.EVT_SPINCTRL, self.update)
        return self._control

    def updateValue(self):
        self.setValidValue(self._control.GetValue())


class FloatProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, value, updateFunctions=None, validityFunction=None, constant=False, increment=0.1):
        assert isinstance(value, (float, int))
        super().__init__(propertyName=propertyName, value=value, updateFunctions=updateFunctions,
                         validityFunction=validityFunction, constant=constant)
        self._inc = increment

    def getCtrl(self, parent):
        # todo: Bug - ctrl not displayed after the program has been started; size of control slightly incorrect
        self._control = wx.SpinCtrlDouble(parent=parent, min=0, max=999999999, initial=self.getValue(), inc=self._inc)
        self._control.Bind(wx.EVT_SPINCTRLDOUBLE, self.update)
        return self._control

    def updateValue(self):
        self.setValidValue(self._control.GetValue())


class StrProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, value, updateFunctions=None, validityFunction=None, constant=False):
        assert isinstance(value, str)
        super().__init__(propertyName=propertyName, value=value, updateFunctions=updateFunctions,
                         validityFunction=validityFunction, constant=constant)

    def getCtrl(self, parent):
        self._control = wx.TextCtrl(parent=parent, value=self.getValue(),
                                    style=wx.TE_PROCESS_ENTER)  # TODO: Add character limit or change PropertyObjectPanel dynamically
        self._control.Bind(wx.EVT_TEXT_ENTER,
                           self.update)  # TODO: find out if other event might fit better (e.g. EVT_TEXT)
        return self._control

    def updateValue(self):
        self.setValidValue(self._control.GetValue())


class ReadOnlyProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, value, constant=False):
        assert isinstance(value, str)
        super().__init__(propertyName=propertyName, value=value, constant=constant)

    def getCtrl(self, parent):
        self._control = wx.TextCtrl(parent=parent, value=self.getValue(),
                                    style=wx.TE_READONLY)  # TODO: Add character limit or change PropertyObjectPanel dynamically
        return self._control

    def updateValue(self):
        pass


# todo: validity function behaviour not tested
class ExprProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, value, graphCalculator=None, updateExprFunction=None, updateFunctions=None,
                 validityFunction=None, constant=False):
        assert isinstance(value, ExprObj)
        super().__init__(propertyName=propertyName, value=value, updateFunctions=updateFunctions,
                         validityFunction=validityFunction, constant=constant)
        self._graphCalc = graphCalculator
        self._updateExprFunc = updateExprFunction

    def getCtrl(self, parent):
        self._control = wx.TextCtrl(parent=parent, value=self.getValue().original(),
                                    style=wx.TE_PROCESS_ENTER)
        self._control.Bind(wx.EVT_TEXT_ENTER,
                           self.update)
        return self._control

    def setValidValue(self, value, raiseInvalidTypeError=False):
        if value == self._inputBeforeValidation:
            return False

        if self._validityFunction is not None:
            try:
                if not self._validityFunction(value):
                    self._control.SetValue(self._inputBeforeValidation)
                    return False
            except TypeError:
                if raiseInvalidTypeError:
                    raise TypeError("the validity function has received an invalid argument type")
                else:
                    return False

        expr = self.getValue()
        exprType, exprName = type(expr), expr.name()

        if not self.redefineAs(exprType, exprName, value):
            self._control.SetValue(self._inputBeforeValidation)
            return False
        else:
            self._setValue(self._graphCalc.get(exprName))
            if self._updateExprFunc is not None:
                self._updateExprFunc()  # <- hook to update other expressions
            self._inputBeforeValidation = value
            return True

    def updateValue(self):
        self.setValidValue(self._control.GetValue())

    # Allows to define expression newly
    def redefineAs(self, exprType, exprName, exprStr):
        return self._graphCalc.define(
            exprType, exprName, exprStr, raiseDefExceptions=True
            # todo: raise exceptions later on, when they can be catched and viewed as user feedback
        )

    # Redefines expression (necessary if namespace changes -> e.g. other expression is changed)
    def redefineExisting(self):
        expr = self.getValue()
        self._graphCalc.define(
            type(expr), expr.name(), expr.original(), raiseDefExceptions=True
        )
        self._setValue(self._graphCalc.get(expr.name()))


class ExprReadOnlyProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, expression, constant=False):
        super().__init__(propertyName=propertyName, value=expression, constant=constant)

    def getCtrl(self, parent):
        self._control = wx.TextCtrl(parent=parent, value=str(self.getValue()), style=wx.TE_READONLY)
        return self._control

    def setValidValue(self, expression):
        self._setValue(expression)

    def setValidValueCtrl(self, expression):
        self.setValidValue(expression)
        if self._control is not None:
            self._control.SetValue(str(self.getValue()))

    def _setValueCtrl(self, expression):
        self._setValue(expression)
        if self._control is not None:
            self._control.SetValue(str(self.getValue()))

    def updateValue(self):
        pass


class ListProperty(PropertyCtrl):
    DELIMITER = ";"

    def __init__(self,
                 propertyName,
                 value,
                 fixedFieldAmount=None,
                 fixedType: type = None,
                 updateFunctions=None,
                 validityFunction=None,
                 constant=False):
        assert isinstance(value, (list, tuple, set))  # <- automatically converts into list
        super().__init__(propertyName=propertyName, value=list(value), updateFunctions=updateFunctions,
                         validityFunction=validityFunction,
                         constant=constant)  # types are not respected afterwards (int as string, will be converted to only int)
        self._fieldAmount = fixedFieldAmount
        assert fixedType is None or fixedType is str or fixedType is int or fixedType is float
        self._fieldType = fixedType

        if not self.validInput(self._value):
            raise ValueError(
                f"the initial value of '{self._value}' does not fit the requirements (e.g. field-amount, fixed-type or validity-function)")

    def getCtrl(self, parent):
        self._control = wx.TextCtrl(parent=parent, value=self.type2StringFormat(), style=wx.TE_PROCESS_ENTER)
        self._control.Bind(wx.EVT_TEXT_ENTER, self.update)
        return self._control

    def validInput(self, inputData, raiseInvalidTypeError=False):
        if self._fieldAmount is not None and self._fieldAmount != len(inputData):
            return False
        if self._fieldType != None:
            if any([type(i) != self._fieldType for i in inputData]):
                return False
        if self._validityFunction is not None:
            try:
                if any([not self._validityFunction(i) for i in inputData]):
                    return False
            except TypeError:
                if raiseInvalidTypeError:
                    raise TypeError("the validity function has received an invalid argument type")
                else:
                    return False
        return True

    # special override for this class (does not use setValidValue directly)
    def updateValue(self):
        if self.validInput((data := self.string2TypeFormat())):
            self._setValue(data)
            self._inputBeforeValidation = self._control.GetValue()
            return True
        else:
            self._control.SetValue(self._inputBeforeValidation)
            return False

    def type2StringFormat(self):
        return self.DELIMITER.join(map(str, self._value))

    def string2TypeFormat(self):
        content = self._control.GetValue()
        data = filter(None, content.split(self.DELIMITER))
        return list(map(self._correctType, data))

    # todo: good implementation?
    def _correctType(self, string: str):
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return string


class ColorProperty(PropertyCtrl):
    setterSupport = True

    def __init__(self, propertyName, value, updateFunctions=None, validityFunction=None, constant=False):
        assert isinstance(value, tuple)
        super().__init__(propertyName=propertyName, value=value, updateFunctions=updateFunctions,
                         validityFunction=validityFunction, constant=constant)

    def getCtrl(self, parent):
        self._control = wx.ColourPickerCtrl(parent=parent, colour=self.getValue())
        self._control.Bind(wx.EVT_COLOURPICKER_CHANGED,
                           self.update)
        self._control.GetValue = self.__getValueOverride  # override method <- hacky solution?
        return self._control

    def __getValueOverride(self):
        return self._control.GetColour()[:3]

    def updateValue(self):
        self.setValidValue(self._control.GetValue())


class SelectProperty(PropertyCtrl):
    # todo: every item is stored as a string <- make obvious to programmer or use special data class to store all types
    def __init__(self, propertyName, value, selectedIndex=0, updateFunctions=None, validityFunction=None,
                 constant=False):
        assert isinstance(value, tuple)
        super().__init__(propertyName=propertyName, value=value, updateFunctions=updateFunctions,
                         validityFunction=validityFunction, constant=constant)
        self._currentlySelected = value[selectedIndex]

    def getCtrl(self, parent):
        self._control = wx.ComboBox(parent=parent, value=self._currentlySelected, choices=self.getValue(),
                                    style=wx.CB_READONLY)
        self._control.Bind(wx.EVT_COMBOBOX, self.update)
        return self._control

    def getStrTuple(self):
        return tuple([self._control.GetString(i) for i in range(self._control.GetCount())])

    def getSelected(self):
        return self._currentlySelected
        # todo: what about GetValue()

    def updateValue(self):
        self._currentlySelected = self._control.GetValue()
        self.setValidValue(self.getStrTuple())


def DependentProperty(targetPropertyCtrl: PropertyCtrl, propertyCtrl: PropertyCtrl, updateFunction: callable, checkValidity=True):
    if not propertyCtrl.hasSetterSupport():
        raise NotImplementedError(f"Class '{targetPropertyCtrl.__class__.__name__}' does not support value setting")

    def _update():
        if checkValidity:
            propertyCtrl.setValidValueCtrl(updateFunction(), raiseInvalidTypeError=False)
        else:
            #this is not advised to use
            propertyCtrl._setValueCtrl(updateFunction())

    targetPropertyCtrl.addUpdateFunctions(
        _update
    )
    _update()
    return propertyCtrl


### Property Categories

class PropCategoryDataClass:
    def __init__(self, categoryName: str):
        self.name = categoryName

    # Convenient-method for readability
    def getName(self):
        return self.name


class PropertyObjCategory(Enum):
    FUNCTION = PropCategoryDataClass(vc.PROPERTY_CAT_FUNC)
    VARIABLE = PropCategoryDataClass("Variablen")
    POINT = PropCategoryDataClass("Punkte")
    VECTOR = PropCategoryDataClass("Vektor")
    SHAPE = PropCategoryDataClass(vc.PROPERTY_CAT_SHAPE)
    NO_CATEGORY = PropCategoryDataClass(vc.PROPERTY_CAT_MISC)

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

        self.addProperty(ReadOnlyProperty(vc.PROPERTY_NAME, vc.PROPERTY_NAME_PLACEHOLDER, constant=True))

    def _validPropertyKey(method):
        def inner(object, key, *args, **kwargs):
            try:
                return method(object, key, *args, **kwargs)
            except KeyError:
                raise MyWxException.MissingContent(
                    f"Property with name '{key}' does not exist")  # todo: <- outource such strings?

        return inner

    def addProperty(self, property: Property, override=False):
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

    def hasProperty(self, name):
        return name in self._properties.keys()

    def getPropertyNames(self):
        return tuple(self._properties.values())

    def getPropertyDict(self):
        return self._properties

    @_validPropertyKey
    def setPropertyName(self, oldName, newName):
        self._properties[newName] = self._properties.pop(oldName)
        self._properties[newName].setName(newName)

    def getCategory(self):
        return self._category

    def setCategory(self, category):
        assert isinstance(category, (PropCategoryDataClass, PropertyObjCategory))
        if isinstance(category, PropCategoryDataClass):
            self._category = category
        else:
            self._category = category.getCat()

    def clear(self, clearConstant=False):
        if clearConstant:
            self._properties = {}
        else:
            n = list()
            for i in self._properties:
                if self._properties[i].isConstant() is False:
                    n.append(i)
            for i in n:
                self.removeProperty(i)


# TODO: This class and derived do not account for manager changing and thereby if any property is added dynamically,
#       they wont update the correct manager if manager is changed -> sol: 1. add support 2. disable dynamic properties
class ManagerPropertyObject(PropertyObject, ABC):
    strName = None

    def __init__(self, category: Union[PropCategoryDataClass, PropertyObjCategory], manager=None):
        super().__init__(category)
        self._manager = manager  # TODO: Is this sensible
        self._show = True

    def setManager(self, manager):
        self._manager = manager
        p = self.getProperty(vc.PROPERTY_NAME)  # standard property
        p.setUpdateFunctions(self.updateOverviewPanel)
        self.addProperty(p, override=True)

    def hasManager(self):
        return True if self._manager is not None else False

    def getOverview(self):
        if self.hasManager():
            if self._manager.hasOverviewPanel():
                return self._manager.getOverviewPanel()
            else:
                raise MyWxException.MissingContent(vc.ERROR_MISSING_INSPECTION)
        else:
            raise MyWxException.MissingContent(vc.ERROR_MISSING_PROP_MAN)

    def updateOverviewPanel(self):
        self.getOverview().updatePropertyPanels()

    def show(self, state: bool = True):
        self._show = state

    def isHidden(self):
        return not self._show

    def redefineAllExpressions(self):  # todo: check runtime performance here
        if self._manager is not None:
            for o in self._manager.getPropertyObjects():
                if o != self and isinstance(o, IExprProperty):
                    for p in o.getPropertyDict().values():
                        if isinstance(p, ExprProperty):
                            print(o)
                            p.redefineExisting()

    @classmethod
    def strRep(cls):
        if cls.strName is not None:
            return cls.strName
        return cls.__name__


class NonGraphicalPanelObject(ManagerPropertyObject, ABC):
    def __init__(self, basePlane=None, category=PropertyObjCategory.NO_CATEGORY):
        super().__init__(category=category)
        self._basePlane = basePlane

    def setBasePlane(self, plane):
        self.clear()
        self._basePlane = plane

    def refreshBasePlane(self):
        if self._basePlane is not None:
            self._basePlane.Refresh()


# todo: is it possible to restrict access to change the pen color?
#       create new class for id system

# Baseclass for graphical objects, which lie on top of a base panel
class GraphicalPanelObject(ManagerPropertyObject, ABC):
    def __init__(self, basePlane=None, category=PropertyObjCategory.NO_CATEGORY):
        super().__init__(category=category)
        self._basePlane = basePlane

        self._colorOverride = None  # mandatory for id system
        self._extraWidth = None

        self._drawable = True

    def isDrawable(self):
        return self._drawable

    def setBasePlane(self, plane):
        self.clear()
        self._basePlane = plane
        self.addProperty(
            ToggleProperty(vc.PROPERTY_DRAW, True, updateFunctions=self.refreshBasePlane))  # standard property
        self.addProperty(
            ToggleProperty(vc.PROPERTY_SELECTABLE, True, updateFunctions=self.refreshBasePlane))  # standard property
        self.addProperty(IntProperty(vc.PROPERTY_DRAW_WIDTH, 3, updateFunctions=self.refreshBasePlane))
        self.addProperty(
            ListProperty(
                vc.PROPERTY_COLOR,
                (255, 0, 0),  # <- everything will be colored red if not specified
                fixedFieldAmount=3,
                validityFunction=lambda x: 0 <= x <= 255,  # function will be applied onto every single value
                updateFunctions=self.refreshBasePlane
            )
        )  # standard property
        # todo -custom control for color / custom property class
        #     -->add new color property, this is only a placeholder until then

    ### predefined update functions

    def refreshBasePlane(self):
        if self._basePlane is not None:
            self._basePlane.Refresh()

    # Decorator for blitUpdateMethod to use standardized properties
    def standardProperties(blitUpdateMethod: callable):
        def inner(graphicalPanelObject, deviceContext, **kwargs):
            assert isinstance(graphicalPanelObject, GraphicalPanelObject)
            if graphicalPanelObject.getProperty(vc.PROPERTY_DRAW).getValue() is True:  # <- standard property
                blitUpdateMethod(graphicalPanelObject, deviceContext, **kwargs)

        return inner

    # Called by basePlane if redraw is necessary (Pen Color should never be changed inside)
    @abstractmethod
    def blitUpdate(self, deviceContext: wx.DC, needValueUpdate=True):
        pass

    # !!!Id-System methods!!!

    @timeMethod
    # A function to allow "drawing" of id's <- actually could be implemented es extra extension of class
    # only works if functions called by blitUpdate use drawPropertyColor-decorator-else invalid id will be drawn to bitmap todo: fix?
    # mandatory for id system
    def blitUpdateCopy(self, deviceContext: wx.DC, memoryDeviceContext, idColor, detectableBorderWidth):
        self.blitUpdate(deviceContext)
        if self.getProperty(vc.PROPERTY_SELECTABLE).getValue():
            self._colorOverride = idColor
            self._extraWidth = detectableBorderWidth
            self.blitUpdate(memoryDeviceContext, needValueUpdate=False)
            self._colorOverride = None
            self._extraWidth = None

    # wraps any deviceContext draw method to handle color selection
    # mandatory for id-system #todo: what would could go wrong in this implementation
    def draw(nameOfColorProperty: str, nameOfWidthProperty: str):  # todo: standard constants should be outsourced
        def _draw(drawMethod: callable):
            def _inner(graphObject, deviceContext: wx.DC, *args, **kwargs):
                assert isinstance(graphObject, GraphicalPanelObject)
                if graphObject._colorOverride is None:
                    color = graphObject.getProperty(nameOfColorProperty).getValue()
                else:
                    color = graphObject._colorOverride
                if graphObject._extraWidth is None:
                    width = graphObject.getProperty(nameOfWidthProperty).getValue()
                else:
                    width = 2 * graphObject._extraWidth + graphObject.getProperty(nameOfWidthProperty).getValue()
                p = wx.Pen(wx.Colour(color))
                p.SetWidth(width)
                deviceContext.SetPen(p)
                deviceContext.SetBrush(wx.Brush(wx.Colour(color)))

                drawMethod(graphObject, deviceContext, *args, **kwargs)

            return _inner

        return _draw


# interface for uniformed object instantiation with expression property objects (objects, that *have* to define a graph calculator and expression)
class IExprProperty:
    def __init__(self, graphCalculator, expression):
        self._graphCalc = graphCalculator
        self._exprObj = expression
