import wx

from MyWx.wx import SizerComponent

# A Class to build very simple forms
class FormManager(SizerComponent):
	def __init__(self, parent, style = wx.VERTICAL):
		super().__init__()
		assert style in [wx.VERTICAL, wx.HORIZONTAL]
		self._parent = parent
		self._style = style
		self._sizer = wx.BoxSizer(self._style)
		self._components = list()
		self._form = self._Form()

	def addComponent(self, component : wx.Window, proportion = 0, sizerFlags = wx.EXPAND, padding = 5):
		self._components.append(self._Component(component, proportion, sizerFlags, padding))

	def addInformationComponent(self, component : wx.Window, informationCallable, proportion = 0, sizerFlags = wx.EXPAND, padding = 5):
		assert not isinstance(component, wx.Sizer), "Component should not be Sizer-object. Separate into addInformation() and addComponent()."
		self.addComponent(component, proportion, sizerFlags, padding)
		self._form.addFormItem(component, informationCallable)

	def addInformation(self, component : wx.Window, informationCallable):
		self._form.addFormItem(component, informationCallable)

	def addDivisionLine(self, proportion = 0, sizerFlags = wx.EXPAND, padding = 5):
		self.addComponent(wx.StaticLine(self._parent), proportion, sizerFlags, padding)

	def getForm(self):
		return self._form

	def build(self):
		self._sizer = wx.BoxSizer(self._style)
		for c in self._components:
			self._sizer.Add(c.comp, c.prop, c.flags, c.padding)

	def buildOverrideStyle(self, styleFlags = wx.EXPAND | wx.BOTTOM, padding = 5):
		self._sizer = wx.BoxSizer(self._style)
		for c in self._components:
			self._sizer.Add(c.comp, c.prop, styleFlags, padding)

	class _Component():
		def __init__(self, component, proportion = 0, sizerFlags = wx.EXPAND, padding = 5):
			self.comp = component
			self.prop = proportion
			self.flags = sizerFlags
			self.padding = padding

	class _Form():
		def __init__(self):
			self._items = list()

		def addFormItem(self, item, callable):
			# Item, callable, standard-value
			self._items.append((item, callable, callable()))

		def getFormItems(self):
			return self._items

		def getFormItemData(self):
			return [(i[0], i[1]()) for i in self._items]

		def getFormValueData(self):
			return [i[1]() for i in self._items]

		def resetForm(self):
			for i in self._items:
				i[0].SetValue(i[2])