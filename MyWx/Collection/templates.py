import wx

from MyWx.wx import *
from MyWx.Collection.Adv.splitter import DynamicMultiSplitter
from MyWx.Collection.format import expanded
from typing import Tuple


# Todo:
# 		-what happens with equal scaling while resizing
#	    -implement system for minimum size or unsplit window
#		-add another random panel to try out functionality
class ThreePanelWorkspace(SizerTemplate):
    splitter: DynamicMultiSplitter

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)

    def build(self,
              firstSashPos: int = None,
              secondSashPos: int = None,
              splitterProportion: Tuple[int, int, int] = (0, 1, 0),
              splitterStyle: int = wx.SP_THIN_SASH
              ):
        self._sizer.Clear()
        self.splitter = DynamicMultiSplitter(self._parent, style=splitterStyle)
        self.splitter.SetOrientation(wx.HORIZONTAL)

        for c in self._content:
            self.splitter.AppendWindow(c)

        self.splitter.SetProportions(splitterProportion)

        if firstSashPos is None:
            firstSashPos = self.splitter.GetWidth() * 0.15
        if secondSashPos is None:
            secondSashPos = -self.splitter.GetWidth() * 0.15
        self.splitter.SetSashAbsPosition(0, firstSashPos)
        self.splitter.SetSashAbsPosition(1, secondSashPos)

        self._sizer.Add(self.splitter, 1, wx.EXPAND)

    def setWindows(self, panel1: wx.Window, panel2: wx.Window, panel3: wx.Window):
        self._content = [panel1, panel2, panel3]

    # redundant, only exists to override setContent and setWindows should be used instead
    def setContent(self, content: Tuple[wx.Window, wx.Window, wx.Window]):
        assert len(content) == 3 and all([isinstance(type(i), wx.Window) for i in content])
        self._content = content

class PanelWithHeader(SizerTemplate):
    def __init__(self, parent=None, headline="Headline", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._h : str = headline
        self._txt : wx.StaticText = None
        self._backColor: Tuple[int, int, int] = (200, 200, 200)
        self._hHeight: int = 25
        self._font : wx.Font = wx.Font(15, wx.DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self._txtBackground : wx.Panel = wx.Panel(self._parent, size=(0, self._hHeight))

        self._sizer = wx.BoxSizer(wx.VERTICAL)

    #TODO: is building in the constructor redundant
    def build(self):
        self._sizer.Clear()
        self._txtBackground.Destroy()
        self._txtBackground = wx.Panel(self._parent, size=(0, self._hHeight))
        self._txtBackground.SetBackgroundColour(self._backColor)
        self._txt = wx.StaticText(self._txtBackground, label=self._h, style=wx.ALIGN_CENTER_HORIZONTAL)
        self._txt.SetFont(self._font)

        self._txtBackground.SetSizer(expanded(self._txt))
        self._sizer.Add(self._txtBackground, 0, wx.EXPAND)
        if self._content is not None:
            self._sizer.Add(self._content, 1, wx.EXPAND)

    @SizerComponent.rebuild
    def setLabelTxt(self, headline):
        self._h = headline

    def getLabelTxt(self):
        return self._h

    @SizerComponent.rebuild
    def setContent(self, content):
        super().setContent(content)

    def getContent(self):
        return self._content

    @SizerComponent.rebuild
    def setBackground(self, background):
        self._txtBackground = background

    def getBackground(self):
        return self._txtBackground

    @SizerComponent.rebuild
    def setLabelObj(self, staticTxt):
        self._txt = staticTxt

    def getLabelObj(self):
        return self._txt

    @SizerComponent.rebuild
    def setFont(self, font: wx.Font):
        self._font = font

    def getFont(self):
        return self._font

    @SizerComponent.rebuild
    def setHeadBackgroundColor(self, color: Tuple[int, int, int]):
        self._backColor = color

    def getHeadBackgroundColor(self):
        return self._backColor

    @SizerComponent.rebuild
    def setHeaderHeight(self, height):
        self._hHeight = height

    def getHeaderHeight(self):
        return self._hHeight

class PanelWithHeaderAccordion(PanelWithHeader):
    def __init__(self, parent=None, headline="Headline", *args, **kwargs):
        super().__init__(parent, headline=headline, *args, **kwargs)

    def build(self):
        super().build()
        self._txt.Bind(wx.EVT_LEFT_DOWN, self._onClick)

    def setContent(self, content):
        super().setContent(content)

    def _onClick(self, evt = None):
        if self._content is not None:
            if self._content.IsShown(): #TODO: maybe replace none condition with panel size zero
                self.minimize()
            else:
                self.maximize()

    @SizerTemplate.rebuildAndLayout
    def minimize(self):
        self._content.Show(False)

        #add function to remove content -> Set content None

    @SizerTemplate.rebuildAndLayout
    def maximize(self):
        self._content.Show(True)