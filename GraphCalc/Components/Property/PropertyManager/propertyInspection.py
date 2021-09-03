import wx

from MyWx.wx import *
from MyWx.Collection.panels import ListComponent
from MyWx.Collection.format import expanded

from GraphCalc.Components.Property.property import PropertyObject
# Panel to show Properties
class PropInspectionPanel(GenericPanel):
    def __init__(self, manager, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self._manager = manager
        self._inspectedObj: PropertyObject = None
        self._contentPanel = GenericPanel(self)
        self._sizerComponent = ListComponent(self._contentPanel, sizerFlags=wx.EXPAND | wx.BOTTOM)

        self.SetSizer(expanded(self._contentPanel))

    def setActivePropObj(self, propertyObj: PropertyObject):
        assert isinstance(propertyObj, PropertyObject)
        self._inspectedObj = propertyObj

    def buildCurrentPropObj(self):
        self.buildByPropObj(self._inspectedObj)

    def buildByPropObj(self, propertyObj: PropertyObject):
        #TODO: How to sort property objects / How to update property objects / flickers a bit when builidng
        self._contentPanel.Show(False) #<- prevents unwanted overlapping of elements while object is build
        self._sizerComponent.emptyList()

        for i, p in enumerate(propertyObj._properties.values()):

            #TODO: export these values
            txtWidth = 100
            txtCtrlProportion = (1, 6)

            #background = wx.Panel(self)    #TODO: add styling
            #background.SetBackgroundColour((250, 250, 250))

            txt = wx.StaticText(parent=self._contentPanel, label=f"{p.getName().capitalize()}:", size=(txtWidth, 0))
            ctrl = p.getCtrl(parent=self._contentPanel)
            line = wx.StaticLine(self._contentPanel)

            s1 = wx.BoxSizer(wx.HORIZONTAL)
            s1.Add(txt, 1, wx.EXPAND)
            s1.Add(ctrl, 6, wx.EXPAND) #TODO: export proportions into separate file

            self._sizerComponent.addComponent(s1)
            self._sizerComponent.addComponent(line)
            #self._sizerComponent.addComponent(background)

        self._sizerComponent.clearSizer(deleteSizers=True, deleteWindows=True)

        self._contentPanel.SetSizer(self._sizerComponent.getSizerAndBuild())
        self._contentPanel.Layout()

        self._contentPanel.Show(True)