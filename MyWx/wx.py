import wx
from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, List, Dict, Any

from MyWx.Collection._core.error import MyWxException


# Extends the wx.Panel-Class and grants a bit of genericity
class GenericPanel(wx.Panel):
    # can *args be placed after keyword argument?
    def __init__(self, parent=None, size=None, *args, **kwargs):
        if size is None:
            super().__init__(parent=parent, *args, **kwargs)
        else:
            super().__init__(parent=parent, size=size, *args, **kwargs)
        self._parent: wx.Window = parent

    # A decorator which rebuilds the panel, if wrapped method is called
    @staticmethod
    def rebuild(method):
        def inner(obj, *args, **kwargs):
            assert isinstance(obj, GenericPanel)
            r = method(obj, *args, **kwargs)
            obj.build()
            return r
        return inner

    def build(self):
        pass


class GenericMouseScrollPanel(wx.ScrolledWindow):
    # can *args be placed after keyword argument?
    def __init__(self, parent=None, size=None, *args, **kwargs):
        if size is None:
            super().__init__(parent=parent, *args, **kwargs)
        else:
            super().__init__(parent=parent, size=size, *args, **kwargs)
        self._parent = parent

        self.Bind(wx.EVT_PAINT, self._setUpScrolling)

    # A decorator which rebuilds the panel, if wrapped method is called
    #TODO: is it possible to add @rebuild
    @staticmethod
    def rebuild(method):
        def inner(obj, *args, **kwargs):
            assert isinstance(obj, GenericMouseScrollPanel)
            r = method(obj, *args, **kwargs)
            obj.build()
            return r

        return inner

    def build(self):
        pass

    def _setUpScrolling(self, evt=None):
        self.FitInside()
        self.SetScrollRate(0, 10)
        evt.Skip()

# Base class for classes which represent a sizer abstraction
# e.g.: A sub-panel, with features, which is outsourced into another class
class SizerComponent(ABC):
    def __init__(self, parent=None):
        self._parent: wx.Window = parent
        self._sizer: wx.Sizer = None

    # Implement instructions on how to create sizer configuration
    @abstractmethod
    def build(self):
        pass

    # return object after it has been build (mostly for inline object creation) <- Maybe redundant
    def getBuild(self):
        self.build()
        return self

    # Wrap method to rebuild sizer
    @staticmethod
    def rebuild(method):
        def inner(obj, *args, **kwargs):
            assert isinstance(obj, SizerComponent)
            r = method(obj, *args, **kwargs)
            obj.build()
            return r
        return inner

    # Wrap method to rebuild and live-update layout of parent (used for user interaction)
    @staticmethod
    def rebuildAndLayout(method):
        def inner(obj, *args, **kwargs):
            assert isinstance(obj, SizerComponent)
            r = method(obj, *args, **kwargs)
            obj.build()
            obj.layoutParent()
            return r
        return inner

    def layoutParent(self):
        self._parent.Layout()

    # Detaches all windows and deletes all sizers
    def clearSizer(self, deleteSizers = False):
        if deleteSizers:
            self._sizer.Clear()
        else:
            for i in range(self._sizer.GetItemCount()-1, -1, -1):
                self._sizer.Detach(i)

    def destroy(self):
        self._sizer.Clear(True)
        self._sizer.Destroy()

    def getSizer(self):
        if self._sizer is None:  # If sizer is None, building automatically could be implemented
            raise MyWxException.SizerNotBuild()
        return self._sizer

    def getSizerAndBuild(self):
        self.build()
        return self.getSizer()

# Sizer Component which uses SizerContent to specify sizer building
# Used if components need different styling
class SizerComponentStyle(SizerComponent):
    def __init__(self, parent):
        super().__init__(parent)
        self._components: List[SizerContent, ...] = list()

    def build(self):
        self.clearSizer()
        for c in self._components:
            self._sizer.Add(c.comp, c.prop, c.flags, c.padding)

    def buildOverrideStyle(self, styleFlags=wx.EXPAND | wx.BOTTOM, padding=5):
        self._sizer = wx.BoxSizer(self._style)
        for c in self._components:
            self._sizer.Add(c.comp, c.prop, styleFlags, padding)

# Dataclass to hold information about sizer content style
class SizerContent():
    def __init__(self, component, proportion=0, sizerFlags=wx.EXPAND, padding=5):
        self.comp: wx.Window = component
        self.prop: int  = proportion
        self.flags: wx.SizerFlags = sizerFlags
        self.padding: int = padding


# A sizer-template represents a sizer-component which is also already formatted but displayed
# objects are not initialized with the object, thus can be added after object-init
class SizerTemplate(SizerComponent, ABC):
    def __init__(self, parent=None, content=None):
        super().__init__(parent)
        self._allowEmpty: bool = False
        self._content: wx.Window = content
        self.__build = self.build
        self.build = self.__buildWrapper

    def allowEmpty(self):
        return self._allowEmpty

    def setAllowEmpty(self, state: bool = True):
        assert isinstance(state, bool)
        self._allowEmpty = state

    def isEmpty(self):
        return True if self._content is None else False

    @abstractmethod
    def build(self):
        pass

    def __buildWrapper(self):
        if not self._allowEmpty and self._content is None: #TODO: use Enum as none content / maybe emptyPanel as content
            raise MyWxException.MissingContent()
        self.__build()

    def setContent(self, content: wx.Window):
        assert isinstance(content, wx.Window)
        self._content = content

    def getContent(self):
        return self._content