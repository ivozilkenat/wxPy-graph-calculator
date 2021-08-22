from MyWx.Collection.Adv.splitter import DynamicMultiSplitter
from MyWx.wx import *
from MyWx.Collection._core.wxUtilities import randomRGBTriple
from MyWx.Collection.format import expanded
from typing import Tuple


# Basic Panel, which implements generic buttons and adjacent event method
# minimizing is a feature preserved for splitter windows
class SplitterSideViewPanel(GenericPanel):
    minSize = 40  # <- should this be static or rather object specific, probably

    def __init__(self, parent, size=None, color=(255, 255, 255), minimizable=True):
        super().__init__(parent, size)
        self.SetBackgroundColour(color)
        self._vSizer = wx.BoxSizer(wx.VERTICAL)
        self.minimized = False  # <- guaranteed ?

        self.controlBar = PanelControlBar(self)

        if minimizable:  # outsource as generic feature or smth like that
            assert isinstance(self._parent, wx.SplitterWindow) or isinstance(self._parent, DynamicMultiSplitter)
            self._parent.SetMinimumPaneSize(SplitterSideViewPanel.minSize)
            self.minPlaceholder = self.MinimizationPlaceholderPanel(self._parent, self)
            self.minPlaceholder.Show(False)
            mBtt = PanelWindowController(self, bind=self._minimize)
            self.controlBar.addWindowControlBuild(mBtt)
            self.Bind(wx.EVT_SIZE, self._onSizeMinimize)

        self._vSizer.Add(self.controlBar.sizer, 0, wx.EXPAND)
        self.SetSizer(self._vSizer)

    def _onSizeMinimize(self, event=None):
        if self.GetSize()[0] < SplitterSideViewPanel.minSize + 1:  # and not self.minimized: #only accounts for width
            self._minimize()
        else:
            self._unminimize()
        event.Skip()

    def _minimize(self):
        # outsource whole function, maybe inherit
        if not self.minimized:
            # Implementation only accounts for wx.SplitterWindow and not for MultiSplitterWindows
            print("min")
            # otherWindow = self.parent.GetWindow1() if self.parent.GetWindow1() != self else self.parent.GetWindow2()
            # self.parent.Unsplit()
            # self.Show(False)
            # self.parent.SplitVertically(self.minPlaceholder, otherWindow, SideViewPanel.minSize)
            # self.minPlaceholder.Show(True)
            # maybe use replace
            self.minPlaceholder.Show(True)

            self._parent.ReplaceWindow(self, self.minPlaceholder)
            self.Show(False)

            self.minimized = True

    def _unminimize(self):
        if self.minimized:
            print("norm")
            # otherWindow = self.parent.GetWindow1() if self.parent.GetWindow1() != self else self.parent.GetWindow2()
            # self.parent.Unsplit()

            # self.minPlaceholder.Show(False)
            # self.parent.SplitVertically(self, otherWindow)
            # self.Show(True)

            self.Show(True)
            self._parent.ReplaceWindow(self.minPlaceholder, self)
            self.minPlaceholder.Show(False)

            self.minimized = False

    def addContentSizer(self, sizer):
        assert isinstance(sizer, wx.Sizer)
        self._vSizer.Add(sizer, 1, wx.EXPAND)
        self.SetSizer(self._vSizer)

    class MinimizationPlaceholderPanel(GenericPanel):
        def __init__(self, parent, coveredObject):
            super().__init__(parent)
            self.SetBackgroundColour((255, 0, 0))
            self.coveredObject = coveredObject

            self.Bind(wx.EVT_SIZE, self._onSize)
            self.Bind(wx.EVT_LEFT_DOWN, self._onClick)

        def _onSize(self, event=None):
            if self.GetSize()[0] >= SplitterSideViewPanel.minSize:
                self.coveredObject._unminimize()
            event.Skip()

        def _onClick(self, event=None):
            self.coveredObject._unminimize()
            event.Skip()


class PanelControlBar(SizerComponent):
    def __init__(self, parent, barHeight=30, color=(200, 200, 200), windowControllers=None):
        super().__init__(parent)
        self.color = color
        self.barHeight = barHeight

        if windowControllers is None:
            self.windowControllers = list()
        else:
            assert isinstance(windowControllers, list)
            self.windowControllers = windowControllers
        self.build()

    def addWindowControl(self, PanelWindowControl, index=None):
        assert isinstance(PanelWindowControl, PanelWindowController)
        if index is None:
            self.windowControllers.append(PanelWindowControl)
        else:
            self.windowControllers.insert(index, PanelWindowControl)

    def addWindowControlBuild(self, PanelWindowControl, index=None):
        self.addWindowControl(PanelWindowControl, index)
        self.build()

    def build(self):
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.emptySpace = wx.Panel(self._parent, size=(0, self.barHeight))
        self.sizer.Add(self.emptySpace, 1, wx.EXPAND)

        for wc in self.windowControllers:
            self.sizer.Add(wc, 0, wx.EXPAND)

        self.emptySpace.SetBackgroundColour(self.color)


# A panel which is bound to a callable (panel as button)
class PanelWindowController(GenericPanel):
    def __init__(self, parent, width=40, color=(255, 0, 0), icon=None, bind=None):
        super().__init__(parent, size=(width, 0))
        self.SetBackgroundColour(color)
        self.icon = icon  # <- icon support not implemented yet, maybe button-bitmap should be new subclass
        self.target = bind

        self.Bind(wx.EVT_LEFT_DOWN, self._onClick)
        self.Bind(wx.EVT_MOTION, self._onHover)

    def bindTo(self, callable):
        self.target = callable

    def _onClick(self, event=None):
        self.target()

    def _onHover(self, event=None):
        pass
# Could use custom hover effects or color highlighting


class PanelWithHeader(GenericPanel):
    def __init__(self, parent=None, size=None, headline="Headline"):
        super().__init__(parent, size)
        self.parent = parent
        self._content = None

        self._h = headline
        self._txt = None
        self._font = wx.Font(15, wx.DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self._txtBackground = None
        self._backColor = (200, 200, 200)
        self._hHeight = 25

        self.build()

    def build(self):
        self._mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._txtBackground = wx.Panel(self, size=(0, self._hHeight))
        self._txtBackground.SetBackgroundColour(self._backColor)
        self._txt = wx.StaticText(self._txtBackground, label=self._h, style=wx.ALIGN_CENTER_HORIZONTAL)
        self._txt.SetFont(self._font)

        self._txtBackground.SetSizer(expanded(self._txt))
        self._mainSizer.Add(self._txtBackground, 0, wx.EXPAND)
        if not self._content is None:
            self._mainSizer.Add(self._content, 1, wx.EXPAND)
        self.SetSizer(self._mainSizer)

    @GenericPanel.rebuild
    def setLabelTxt(self, headline):
        self._h = headline

    def getLabelTxt(self):
        return self._h

    @GenericPanel.rebuild
    def setContent(self, content):
        self._content = content

    def getContent(self):
        return self._content

    @GenericPanel.rebuild
    def setBackground(self, background):
        self._txtBackground = background

    def getBackground(self):
        return self._txtBackground

    @GenericPanel.rebuild
    def setLabelObj(self, staticTxt):
        self._txt = staticTxt

    def getLabelObj(self):
        return self._txt

    @GenericPanel.rebuild
    def setFont(self, font: wx.Font):
        self._font = font

    def getFont(self):
        return self._font

    @GenericPanel.rebuild
    def setHeadBackgroundColor(self, color: Tuple[int, int, int]):
        self._backColor = color

    def getHeadBackgroundColor(self):
        return self._backColor

    @GenericPanel.rebuild
    def setHeaderHeight(self, height):
        self._hHeight = height

    def getHeaderHeight(self):
        return self._hHeight


class RandomGridPanel(GenericPanel):
    def __init__(self, parent, n=3, size=None, hgap=5, vgap=5):
        super().__init__(parent=parent, size=size)
        self.sizer = wx.GridBagSizer(hgap=hgap, vgap=vgap)
        self.n = n
        for i in range(self.n ** 2):
            p = wx.Panel(self)
            p.SetBackgroundColour(randomRGBTriple())
            self.sizer.Add(p, pos=(i // self.n, i % self.n), flag=wx.EXPAND)
        for i in range(self.n):
            self.sizer.AddGrowableRow(i)
            self.sizer.AddGrowableCol(i)
        self.SetSizer(self.sizer)


class RandomPanel(GenericPanel):
    def __init__(self, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self.SetBackgroundColour(randomRGBTriple())
