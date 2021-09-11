from MyWx.wx import *

from MyWx.Collection.panels import RandomGridPanel
from MyWx.Collection.panels import SplitterSideViewPanel


# TODO: set GraphProptertyManager as content
class PropertyObjectOverviewPanel(SplitterSideViewPanel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.addContentSizer(RandomGridPanel(self, 4).sizer)


class PropertyToolTipPanel(GenericPanel):
    def __init__(self, parent):
        super().__init__(parent=parent, size=(100, 100))
