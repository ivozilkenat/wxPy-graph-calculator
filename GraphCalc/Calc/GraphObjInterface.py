import wx

from GraphCalc.Calc.GraphCalculator import GraphCalculator2D, ExprObj, Function2DExpr, InvalidExpression
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Property.property import IExprProperty

from MyWx.wx import *
from MyWx.Collection._core.wxUtilities import randomRGBTriple

from enum import Enum
from abc import ABC, abstractmethod

class PropertyObj2DInterface:
	typeAssignments = {
		Function2DExpr: GraphFunction2D
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
			raise e #todo: currently doesnt catch error, should this be handled in higher class?

		if not successful:
			raise InvalidExpression(f"Expression: '{expressionAsString}' couldn't be parsed successfully")
		# create object

		targetObject = self.typeAssignments[exprType]
		newObj = targetObject(self._graphCalc, self._graphCalc.get(name))

		for p in self._graphPropManager.propertyManager.getPropertyObjects():
			if isinstance(p, IExprProperty):
				if p._exprObj.name() == name: # object was defined before and is already in property manager
					self._graphPropManager.removePropertyObject(p) # prevents accidental multi definition
					break

		#todo: !!!replace with better solution!!!
		newObj.getProperty("name").setValue(name) #doesn't update definition when changed <- new property? or make static?
		self._graphPropManager.addPropertyObject(newObj)
		# todo: leave this? => use a sequence
		newObj.getProperty("color").setValue(randomRGBTriple())

		if self._updateFunction is not None:
			self._updateFunction()


class AddPanelComponent(SizerComponent, ABC):
	expressionType = None
	propertyObjectType = None

	def __init__(self, parent, graphObjectInterface: PropertyObj2DInterface, style=wx.VERTICAL, sizerFlags=wx.EXPAND, padding=5):
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

	def setName(self, name: str):
		self._name = name

	def addExpr(self):
		assert self.expressionType is not None, "expression type not set"
		assert self.propertyObjectType is not None, "graphicalObjectType not set"
		self.formatIntoExpression()
		assert len(self._name) > 0, "name of function not set"
		self._interface.addExprObj(
			self.expressionType,
			self._name,
			self._exprStr
		)


class AddPanelFunction(AddPanelComponent):
	expressionType = Function2DExpr
	propertyObjectType = GraphFunction2D
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._sizer = wx.BoxSizer(wx.VERTICAL)
		self._nameIn = None
		self._definitionIn = None

	def formatIntoExpression(self):
		self.setName(f"{self._nameIn.GetValue()}({Function2DExpr.argumentSymbol})")
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

class PropertyAddPanel(GenericPanel):
	assignedTypes = dict([
		AddPanelFunction.getAssignment()
	])

	def __init__(self, graphObjectInterface: PropertyObj2DInterface, parent=None, size=None):
		assert isinstance(graphObjectInterface, PropertyObj2DInterface)
		super().__init__(parent=parent, size=size)
		self._interface = graphObjectInterface
		self._sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetBackgroundColour((255, 255, 255))
		self._box = wx.StaticBox(self, wx.ID_ANY, "Expression Entry")
		self._selectionCombobox = None
		self._addButton = None
		self._content = None
		self._feedbackLabel = None
		self._subSizer = wx.BoxSizer(wx.VERTICAL) #todo: add class for generalization

		self.build()
		self.buildSelectedInput()

	def build(self):
		# build sizer based on addPanelComponent
		self._sizer.Clear()

		choicesStr = list(self.assignedTypes.keys())
		self._selectionCombobox = wx.ComboBox(parent=self._box, value=choicesStr[0], choices=choicesStr,
											  style=wx.CB_READONLY)
		self._addButton = wx.Button(parent=self._box, label="Add Expression")
		self._addButton.Bind(wx.EVT_BUTTON, self._onClick)
		self._feedbackLabel = wx.StaticText(parent=self._box, label="") #todo: create extra class

		self._subSizer.Add(self._selectionCombobox, 0, wx.EXPAND | wx.TOP, 20)
		self._box.SetSizer(self._subSizer)
		self._sizer.Add(self._box, 1, wx.EXPAND)
		self.SetSizer(self._sizer)

	def setFeedback(self, label: str):
		assert self._feedbackLabel is not None
		self._feedbackLabel.SetLabel(label)

	def buildSelectedInput(self):
		self._sizer.Clear()
		self._subSizer.Clear()

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

	def _onClick(self, evt=None):
		try:
			self._content.addExpr()
			self.setFeedback("Valid Entry")
		except InvalidExpression as e:
			self.setFeedback("Invalid Entry")

#todo: add standard color enumeration (with special functionality here?)
