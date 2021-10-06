import wx

from GraphCalc.Calc.graphCalculator import GraphCalculator2D, ExprObj, ValueExpr, Function2DExpr, InvalidExpression
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Graphical.Objects.graphPropertyVariable import Variable
from GraphCalc.Components.Graphical.Objects.graphFunctionGroup import GraphFunctionGroup
from GraphCalc.Components.Property.property import IExprProperty, GraphicalPanelObject, NonGraphicalPanelObject

from GraphCalc.Application.outputPrompt import IOutputExtension

from MyWx.wx import *
from MyWx.Collection._core.wxUtilities import randomRGBTriple

from enum import Enum
from abc import ABC, abstractmethod


class PropertyObj2DInterface:
    typeAssignments = {
        Function2DExpr: GraphFunction2D,
        ValueExpr: Variable
    }

    def __init__(self,
                 graphCalculator: GraphCalculator2D,
                 graphPropertyManager: Dy2DGraphPropertyManager,
                 updateFunction: callable = None
                 ):
        self._graphCalc = graphCalculator
        self._graphPropManager = graphPropertyManager
        self._updateFunction = updateFunction

    def addExprObj(self, exprType, name, expressionAsString):
        # parse expression and validate
        if exprType not in self.typeAssignments:
            raise InvalidExpression(f"Expression cannot be converted into any GraphicalProperty-object")

        try:
            successful = self._graphCalc.define(exprType, name, expressionAsString)
        except InvalidExpression as e:
            raise e  # todo: currently doesnt catch error, should this be handled in higher class?

        if not successful:
            raise InvalidExpression(f"Expression: '{expressionAsString}' couldn't be parsed successfully")
        # create object

        targetObject = self.typeAssignments[exprType]
        assert IExprProperty in (classBases := targetObject.__bases__)
        assert NonGraphicalPanelObject in classBases or GraphicalPanelObject in classBases

        newObj = targetObject(self._graphCalc, self._graphCalc.get(name))

        for p in self._graphPropManager.propertyManager.getPropertyObjects():
            if isinstance(p, IExprProperty):
                if p._exprObj.name() == name:  # object was defined before and is already in property manager
                    self._graphPropManager.removePropertyObject(p)  # prevents accidental multi definition
                    break

        # todo: !!!replace with better solution!!!
        newObj.getProperty("name")._setValue(self._graphCalc.get(name).nameFormatted())  # doesn't update definition when changed <- new property? or make static?

        self._graphPropManager.addPropertyObject(newObj)
        newObj.redefineAllExpressions()

        # todo: leave this? => use a sequence
        if isinstance(newObj, GraphicalPanelObject):
            newObj.getProperty("color")._setValue(randomRGBTriple())

        if self._updateFunction is not None:
            self._updateFunction()


class AddPanelComponent(SizerComponent, ABC):
    expressionType = None
    propertyObjectType = None

    def __init__(
			self,
			parent,
			graphObjectInterface: PropertyObj2DInterface,
			style=wx.VERTICAL,
			sizerFlags=wx.EXPAND,
			padding=5
		 ):
        assert isinstance(graphObjectInterface, PropertyObj2DInterface)
        super().__init__(parent=parent)
        self._interface = graphObjectInterface
        self._name = None
        self._exprStr = None

    @classmethod
    def setTypes(cls, expressionType, graphicalObjType):
        cls.expressionType = expressionType
        cls.propertyObjectType = graphicalObjType

    @classmethod
    def getPropertyTypeName(cls):
        assert cls.expressionType is not None
        assert cls.propertyObjectType is not None
        return cls.propertyObjectType.strRep()

    @classmethod
    def getAssignment(cls):
        assert cls.expressionType is not None
        assert cls.propertyObjectType is not None
        return cls.propertyObjectType.strRep(), cls

    @abstractmethod
    def formatIntoExpression(self):
        """
        Format control inputs into a valid expression string
        """

    @abstractmethod
    def build(self):
        pass

    def getExprStr(self):
        return self._exprStr

    def setExprStr(self, expressionAsString: str):
        self._exprStr = expressionAsString

    def getName(self):
        return self._name

    def setName(self, name: str, clean=True):
        self._name = self._cleanName(name)

    def _cleanName(self, name: str):
        return name.replace(" ", "_")

    def addExpr(self):
        assert self.expressionType is not None, "expression type not set"
        assert self.propertyObjectType is not None, "graphicalObjectType not set"
        self.formatIntoExpression()
        if len(self._name) > 0:
            self._interface.addExprObj(
                self.expressionType,
                self._name,
                self._exprStr
            )
        else:
            raise InvalidExpression("Name of expression must be set")


class AddPanelFunction(AddPanelComponent):
    expressionType = Function2DExpr
    propertyObjectType = GraphFunction2D

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._nameIn = None
        self._definitionIn = None

    def formatIntoExpression(self):
        self.setName(self._nameIn.GetValue())
        self.setExprStr(self._definitionIn.GetValue())

    def build(self):
        self.clearSizer()
        nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        definitionSizer = wx.BoxSizer(wx.HORIZONTAL)
        nameTxt = wx.StaticText(self._parent, label="Name:")
        definitionTxt = wx.StaticText(self._parent, label="Definition:")
        self._nameIn = wx.TextCtrl(self._parent)
        self._definitionIn = wx.TextCtrl(self._parent)

        nameSizer.Add(nameTxt, 1, wx.EXPAND)
        nameSizer.Add(self._nameIn, 2, wx.EXPAND)
        definitionSizer.Add(definitionTxt, 1, wx.EXPAND)
        definitionSizer.Add(self._definitionIn, 2, wx.EXPAND)

        self._sizer.Add(nameSizer, 0, wx.EXPAND | wx.BOTTOM, 5)
        self._sizer.Add(definitionSizer, 0, wx.EXPAND)


class AddPanelVariable(AddPanelComponent):
    expressionType = ValueExpr
    propertyObjectType = Variable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._nameIn = None
        self._definitionIn = None

    def formatIntoExpression(self):
        self.setName(self._nameIn.GetValue())
        self.setExprStr(self._definitionIn.GetValue())

    def build(self):
        self.clearSizer()
        nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        definitionSizer = wx.BoxSizer(wx.HORIZONTAL)
        nameTxt = wx.StaticText(self._parent, label="Name:")
        definitionTxt = wx.StaticText(self._parent, label="Value:")
        self._nameIn = wx.TextCtrl(self._parent)
        self._definitionIn = wx.TextCtrl(self._parent)

        nameSizer.Add(nameTxt, 1, wx.EXPAND)
        nameSizer.Add(self._nameIn, 2, wx.EXPAND)
        definitionSizer.Add(definitionTxt, 1, wx.EXPAND)
        definitionSizer.Add(self._definitionIn, 2, wx.EXPAND)

        self._sizer.Add(nameSizer, 0, wx.EXPAND | wx.BOTTOM, 5)
        self._sizer.Add(definitionSizer, 0, wx.EXPAND)


class PropertyAddPanel(GenericPanel, IOutputExtension):
    assignedTypes = dict([
        AddPanelFunction.getAssignment(),
        AddPanelVariable.getAssignment()
    ])

    def __init__(self, graphObjectInterface: PropertyObj2DInterface, parent=None, size=None):
        assert isinstance(graphObjectInterface, PropertyObj2DInterface)
        GenericPanel.__init__(self, parent=parent, size=size)
        IOutputExtension.__init__(self)
        self._interface = graphObjectInterface
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetBackgroundColour((255, 255, 255))
        self._box = wx.StaticBox(self, wx.ID_ANY, "Expression Entry")
        self._selectionCombobox = None
        self._addButton = None
        self._content = None
        self._feedbackLabel = None
        self._subSizer = wx.BoxSizer(wx.VERTICAL)  # todo: add class for generalization

        self.build()
        self.buildSelectedInput()

    def build(self):
        # build sizer based on addPanelComponent
        self._sizer.Clear()

        choicesStr = list(self.assignedTypes.keys())
        self._selectionCombobox = wx.ComboBox(parent=self._box, value=choicesStr[0], choices=choicesStr,
                                              style=wx.CB_READONLY)
        self._selectionCombobox.Bind(wx.EVT_COMBOBOX, self.buildSelectedInput)
        self._addButton = wx.Button(parent=self._box, label="Add Expression")
        self._addButton.Bind(wx.EVT_BUTTON, self._onClick)
        self._feedbackLabel = wx.StaticText(parent=self._box, label="")  # todo: create extra class

        self._subSizer.Add(self._selectionCombobox, 0, wx.EXPAND | wx.TOP, 20)
        self._box.SetSizer(self._subSizer)
        self._sizer.Add(self._box, 1, wx.EXPAND)
        self.SetSizer(self._sizer)

    def setFeedback(self, label: str):
        assert self._feedbackLabel is not None
        self._feedbackLabel.SetLabel(label)

    def buildSelectedInput(self, evt=None):
        if self._content is not None:
            self._content.clearSizer(True, True)
        self._subSizer.Clear()
        self._sizer.Clear()

        self._subSizer.Add(self._selectionCombobox, 0, wx.EXPAND | wx.TOP, 20)

        self._content = self.assignedTypes[self._selectionCombobox.GetValue()](
            parent=self._box,
            graphObjectInterface=self._interface
        )
        self._content.build()
        self._subSizer.Add(self._content.getSizer(), 0, wx.EXPAND | wx.ALL, 5)
        self._subSizer.Add(self._addButton, 0, wx.EXPAND | wx.ALL, 5)
        self._subSizer.Add(self._feedbackLabel, 0, wx.EXPAND | wx.ALL, 5)

        self._box.SetSizer(self._subSizer)
        self._sizer.Add(self._box, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(self._sizer)
        self.Layout()

    def _onClick(self, evt=None):
        try:
            self._content.addExpr()
            self.sendlTry(
                f"added '{self._content.getPropertyTypeName()}' :  {self._content.getName()} = {self._content.getExprStr()}"
            )
            self.setFeedback("Valid Entry")
        except InvalidExpression as e:
            self.sendlTry(e)
            self.setFeedback("Invalid Entry")

# todo: add standard color enumeration (with special functionality here?)
