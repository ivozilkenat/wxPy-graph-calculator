from MyWx.wx import *
from MyWx.Collection.panels import RandomPanel

class GenericPanelDev(wx.Panel):
	def __init__(self, parent = None, size = None, *args, **kwargs):
		if size is None:
			super().__init__(parent = parent, *args, **kwargs)
		else:
			super().__init__(parent = parent, size = size, *args, **kwargs)
		self.parent = parent

	# Returns a panel of random color as a placeholder for developing purposes
	def _asPlaceholder(self):
		self.Show(False)
		return RandomPanel(self.parent)
	def _resizeChecking(self):
		self.Bind(wx.EVT_SIZE, self.__printSize)
	def __printSize(self, evt = None):
		print(self.GetSize())
		evt.Skip()
