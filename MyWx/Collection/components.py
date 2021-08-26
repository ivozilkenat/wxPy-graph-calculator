import wx

from MyWx.wx import *
from MyWx.Collection.format import expanded

from typing import Tuple



# A Class to build very simple forms
class FormManager(SizerComponentStyle):
    def __init__(self, parent, style=wx.VERTICAL):
        super().__init__(parent)
        assert style in [wx.VERTICAL, wx.HORIZONTAL]
        self._style = style
        self._sizer = wx.BoxSizer(self._style)
        self._components = list()
        self._form = self._Form()

    def addComponent(self, component: wx.Window, proportion=0, sizerFlags=wx.EXPAND, padding=5):
        self._components.append(SizerContent(component, proportion, sizerFlags, padding))

    def addInformationComponent(self, component: wx.Window, informationCallable, proportion=0, sizerFlags=wx.EXPAND,
                                padding=5):
        assert not isinstance(component,
                              wx.Sizer), "Component should not be Sizer-object. Separate into addInformation() and addComponent()."
        self.addComponent(component, proportion, sizerFlags, padding)
        self._form.addFormItem(component, informationCallable)

    def addInformation(self, component: wx.Window, informationCallable):
        self._form.addFormItem(component, informationCallable)

    def addDivisionLine(self, proportion=0, sizerFlags=wx.EXPAND, padding=5):
        self.addComponent(wx.StaticLine(self._parent), proportion, sizerFlags, padding)

    def getForm(self):
        return self._form

    def buildOverrideStyle(self, styleFlags=wx.EXPAND | wx.BOTTOM, padding=5):
        self._sizer = wx.BoxSizer(self._style)
        for c in self._components:
            self._sizer.Add(c.comp, c.prop, styleFlags, padding)

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

# Simple Component to align items in row or column
class ListComponent(SizerComponent):
    def __init__(self, parent, style=wx.VERTICAL, sizerFlags=wx.EXPAND, padding=5):
        super().__init__(parent=parent)
        assert style in [wx.VERTICAL, wx.HORIZONTAL]
        self._style = style
        self._sizer = wx.BoxSizer(self._style)
        self._sizerFlags = sizerFlags
        self._padding = padding
        self._components = list()

    def addComponent(self, component: wx.Window):
        self._components.append(component)

    def removeComponent(self, component: wx.Window):
        self._components.remove(component)

    def build(self):
        self.clearSizer()
        for i in self._components:
            self._sizer.Add(i, 0, self._sizerFlags, self._padding)