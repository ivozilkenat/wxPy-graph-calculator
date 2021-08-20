from MyWx.Collection.Adv.splitter import DynamicMultiSplitter
from MyWx.wx import *
from typing import Tuple

#Todo:
# 		-what happens with equal scaling while resizing
#	    -implement system for minimum size or unsplit window
#		-add another random panel to try out functionality
class ThreePanelWorkspace(SizerTemplate):
	splitter : DynamicMultiSplitter
	def __init__(self, parent):
		super().__init__(parent)

	def build(self,
			  firstSashPos : int = None,
			  secondSashPos : int = None,
			  splitterProportion : Tuple[int, int, int] = (0, 1, 0),
			  splitterStyle : int = wx.SP_THIN_SASH
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

	def setContent(self, panel1 : wx.Window, panel2 : wx.Window, panel3 : wx.Window):
		self._content = [panel1, panel2, panel3]