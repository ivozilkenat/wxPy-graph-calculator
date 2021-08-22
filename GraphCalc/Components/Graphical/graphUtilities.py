from MyWx.wx import *

from GraphCalc.Components.Property._property import GraphicalPanelObject, ToggleProperty
from GraphCalc._core.utilities import multiplesInInterval


class CartesianAxes(GraphicalPanelObject):
    def __init__(self):
        super().__init__()

        self.addProperty(ToggleProperty("draw_sub_axis", True))
        self.addProperty(ToggleProperty("draw_main_axis", True))

    # blitUpdate must be implemented correctly (currently with old deviceContext logic for prototyping)
    # -> new version utilises blit from basePlane
    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext):  # TODO: update base class
        if self._properties["draw_sub_axis"].getValue() is True:
            self.drawSubAxis(deviceContext, 50)
        if self._properties["draw_main_axis"].getValue() is True:
            self.drawMainAxis(deviceContext)

    def drawSubAxis(self, deviceContext, axisPixelDistance):
        # deviceContext = self.basePlane.memoryDc

        p = wx.Pen(wx.Colour((128, 128, 128)))
        p.SetWidth(1)
        deviceContext.SetPen(p)
        xSubAxis = multiplesInInterval(axisPixelDistance, self.basePlane.db)
        ySubAxis = multiplesInInterval(axisPixelDistance, self.basePlane.wb)
        for x in xSubAxis:
            x, _ = self.basePlane.correctPosition(x, 0)
            deviceContext.DrawLine(x, 0, x, self.basePlane.h)
        for y in ySubAxis:
            _, y = self.basePlane.correctPosition(0, y)
            deviceContext.DrawLine(0, y, self.basePlane.w, y)

    def drawMainAxis(self, deviceContext):
        # deviceContext = self.basePlane.memoryDc

        p = wx.Pen(wx.Colour((0, 0, 0)))
        p.SetWidth(3)
        deviceContext.SetPen(p)
        if self.basePlane.db[0] < 0 < self.basePlane.db[1]:
            x0, _ = self.basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(x0, 0, x0, self.basePlane.h)
        if self.basePlane.wb[0] < 0 < self.basePlane.wb[1]:
            _, y0 = self.basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(0, y0, self.basePlane.w, y0)
