from MyWx.wx import *
from MyWx.Collection.panels import ListComponent

from GraphCalc.Components.Property.property import PropertyObject
# Panel to show Properties
class PropInspectionPanel(GenericPanel):
    def __init__(self, manager, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self._manager = manager
        self._inspectedObj: PropertyObject = None
        self._sizerComponent = ListComponent(self, sizerFlags=wx.EXPAND | wx.BOTTOM)

    def setActivePropObj(self, propertyObj: PropertyObject):
        assert isinstance(propertyObj, PropertyObject)
        self._inspectedObj = propertyObj

    def buildCurrentPropObj(self):
        self.buildByPropObj(self._inspectedObj)

    def buildByPropObj(self, propertyObj: PropertyObject):
        #TODO: How to sort property objects / How to update property objects
        self._sizerComponent.clearSizer()
        self._sizerComponent.emptyList()

        for i, p in enumerate(propertyObj._properties.values()):

            #TODO: export these values
            txtWidth = 100
            txtCtrlProportion = (1, 6)

            #background = wx.Panel(self)    #TODO: add styling
            #background.SetBackgroundColour((250, 250, 250))

            txt = wx.StaticText(parent=self, label=f"{p.getName().capitalize()}:", size=(txtWidth, 0))
            ctrl = p.getCtrl(parent=self)

            s1 = wx.BoxSizer(wx.HORIZONTAL)
            s1.Add(txt, 1, wx.EXPAND)
            s1.Add(ctrl, 6, wx.EXPAND) #TODO: export proportions into separate file

            self._sizerComponent.addComponent(s1)
            self._sizerComponent.addComponent(wx.StaticLine(self))
            #self._sizerComponent.addComponent(background)

        self.SetSizer(self._sizerComponent.getSizerAndBuild())