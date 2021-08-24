import wx
from abc import ABC, abstractmethod
from enum import Enum

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
        self._yOffset = 0
        self._scrollFactor = 0.5
        self._scrollDirectionFactor = self.Direction.DOWN.value

        self.SetScrollRate(10, 10)
        print(self.GetScrollPixelsPerUnit())

        self.Bind(wx.EVT_MOUSEWHEEL, self._onScroll)

    def setScrollDirection(self, direction):
        assert isinstance(direction, self.Direction)
        self._scrollDirectionFactor = direction.value

    #Only implements vertical scrolling
    def _onScroll(self, evt: wx.MouseEvent = None):
        sizeY = self.GetSize().GetHeight()
        contentSizeY = self.GetBestSize().GetHeight()
        # No scrolling possible, since all objects in view
        if sizeY > contentSizeY: #TODO: what if object change while scrolling
            return
        lowerBound, upperBound = 0, contentSizeY - sizeY

        scrollAmount = evt.GetWheelRotation()
        scrollDistance = scrollAmount * self._scrollFactor * self._scrollDirectionFactor

        self._yOffset += scrollDistance
        if self._yOffset < 0 or self._yOffset > upperBound:
            self._yOffset -= scrollDistance
        else:
            print("scrolling", scrollDistance, self._yOffset)
            self.Scroll(0, scrollDistance * self._scrollDirectionFactor)


    def _adjustScroll(self):
        self.Scroll(0, self._yOffset * self._scrollDirectionFactor)
        print("Scroll update", self._yOffset * self._scrollDirectionFactor)

    class Direction(Enum):
        UP = 1
        DOWN = -1 # Normal scrolling behaviour


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

    def clearSizer(self):
        self._sizer.Clear()

    def getSizer(self):
        if self._sizer is None:  # If sizer is None, building automatically could be implemented
            raise MyWxException.SizerNotBuild()
        return self._sizer

    def getSizerAndBuild(self):
        self.build()
        return self.getSizer()


# A sizer-template represents a sizer-component which is also already formatted but displayed
# objects are not initialized with the object, thus can be added after object-init
class SizerTemplate(SizerComponent, ABC):
    def __init__(self, parent=None, content=None):
        super().__init__(parent)
        self._content : wx.Window = content
        self.__build = self.build
        self.build = self.__buildWrapper

    @abstractmethod
    def build(self):
        pass

    def __buildWrapper(self):
        if self._content is None:
            raise MyWxException.MissingContent()
        self.__build()

    def setContent(self, content):
        self._content = content
