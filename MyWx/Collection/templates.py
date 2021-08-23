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

    def __init__(self, parent):
        super().__init__(parent)

    def build(self,
              firstSashPos: int = None,
              secondSashPos: int = None,
              splitterProportion: Tuple[int, int, int] = (0, 1, 0),
              splitterStyle: int = wx.SP_THIN_SASH
              ):
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
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

    def setContent(self, panel1: wx.Window, panel2: wx.Window, panel3: wx.Window):
        self._content = [panel1, panel2, panel3]


class PanelWithHeader(SizerComponent):
    def __init__(self, parent=None, headline="Headline"):
        super().__init__(parent)
        self._content : wx.Window = None

        self._h : str = headline
        self._txt : wx.StaticText = None
        self._backColor: Tuple[int, int, int] = (200, 200, 200)
        self._hHeight: int = 25
        self._font : wx.Font = wx.Font(15, wx.DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self._txtBackground : wx.Panel = wx.Panel(self._parent, size=(0, self._hHeight))


        self.build()

    def build(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._txtBackground = wx.Panel(self._parent, size=(0, self._hHeight))
        self._txtBackground.SetBackgroundColour(self._backColor)
        self._txt = wx.StaticText(self._txtBackground, label=self._h, style=wx.ALIGN_CENTER_HORIZONTAL)
        self._txt.SetFont(self._font)

        self._txtBackground.SetSizer(expanded(self._txt))
        self._sizer.Add(self._txtBackground, 0, wx.EXPAND)
        if not self._content is None:
            self._sizer.Add(self._content, 1, wx.EXPAND)

    @SizerComponent.rebuild
    def setLabelTxt(self, headline):
        self._h = headline

    def getLabelTxt(self):
        return self._h

    @SizerComponent.rebuild
    def setContent(self, content):
        self._content = content

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

class PanelWithHeaderTab(PanelWithHeader):
    def __init__(self, parent=None, headline="Headline"):
        super().__init__(parent, headline=headline)
        self._referenceCopy = None

    def build(self):
        super().build()
        self._txt.Bind(wx.EVT_LEFT_DOWN, self._onClick)

    def setContent(self, content):
        super().setContent(content)
        self._referenceCopy = content

    def _onClick(self, evt = None):
        if self._content.IsShown():
            self.minimize()
        else:
            self.maximize()

    def minimize(self):
        self._content.Show(False)
        self._sizer.Detach(self._content)
        self.build()


        #TODO: update panel after change /udpate minimize logic, since _content can be None
        #add function to remove content

    #@SizerTemplate.rebuild
    def maximize(self):
        self._content.Show(True)
        self._sizer.Detach(self._content) #TODO: must this always be implemented (else already in sizer error)
        self.build()