import wx

from MyWx.wx import *
from MyWx.Collection.panels import ListComponent
from MyWx.Collection.format import expanded

from GraphCalc.Components.Property.property import PropertyObject

# Panel to further inspect properties of PropertyObject
class PropInspectionPanel(GenericPanel):
    def __init__(self, manager, parent=None, size=None):
        super().__init__(parent=parent, size=size)
        self._manager = manager
        self._inspectedObj: PropertyObject = None
        self._contentPanel = GenericMouseScrollPanel(self)

        self._sizerComponent = ListComponent(self._contentPanel, sizerFlags=wx.EXPAND | wx.BOTTOM)
        self.SetBackgroundColour((250, 250, 250))

        self._layoutSizer = wx.BoxSizer(wx.VERTICAL)
        self._headline = wx.StaticText(self, label="Properties", style=wx.ALIGN_CENTER)
        font = wx.Font(10, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        self._headline.SetFont(font)
        self._layoutSizer.Add(self._headline, 0, wx.EXPAND | wx.ALL, 5)
        self._layoutSizer.Add(wx.StaticLine(self), 0, wx.EXPAND)
        self._layoutSizer.Add(self._contentPanel, 1, wx.EXPAND)

        self.SetSizer(self._layoutSizer)
    # set currently active property-object
    def setActivePropObj(self, propertyObj: PropertyObject):
        assert isinstance(propertyObj, PropertyObject)
        self._inspectedObj = propertyObj

    # build panel by currently active property-object
    def buildCurrentPropObj(self):
        self.buildByPropObj(self._inspectedObj)

    # build panel by specified propertyObject
    def buildByPropObj(self, propertyObj: PropertyObject):
        #TODO: How to sort property objects / How to update property objects / flickers a bit when builidng
        self._contentPanel.Show(False) #<- prevents unwanted overlapping of elements while object is build
        self._sizerComponent.emptyList()
        valueAmount = len(propertyObj._properties.values())

        for i, p in enumerate(propertyObj._properties.values()):
            #TODO: export these values
            txtWidth = 100
            txtCtrlProportion = (1, 6)

            #background = wx.Panel(self)    #TODO: add styling
            #background.SetBackgroundColour((250, 250, 250))

            txt = wx.StaticText(
                parent=self._contentPanel,
                label=f"{p.getName().capitalize()}:",
                size=(txtWidth, 0),
                style = wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_END
            )
            ctrl = p.getCtrl(parent=self._contentPanel)

            s1 = wx.BoxSizer(wx.HORIZONTAL)
            s1.Add(txt, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 5)
            s1.Add(ctrl, 1, wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM, 5) #TODO: export proportions into separate file


            self._sizerComponent.addComponent(s1)
            if i < valueAmount-1:
                self._sizerComponent.addComponent(wx.StaticLine(self._contentPanel))
            #self._sizerComponent.addComponent(background)

        self._sizerComponent.clearSizer(deleteSizers=True, deleteWindows=True)

        self._contentPanel.SetSizer(self._sizerComponent.getSizerAndBuild())
        self._contentPanel.FitInside()

        #self._contentPanel.Layout()
        self._contentPanel.Show(True)
        #self._parent.Layout() #<- should this be layout here?


