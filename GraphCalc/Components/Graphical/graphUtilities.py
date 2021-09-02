from MyWx.wx import *

from GraphCalc.Components.Property.property import GraphicalPanelObject, ToggleProperty
from GraphCalc._core.utilities import multiplesInInterval


class CartesianAxies(GraphicalPanelObject):
    def __init__(self):
        super().__init__()

        self.getProperty("name").setValue("Cartesian Coordinate-System")

    def setBasePlane(self, plane):
        # Properties must be set here, since update function requires panel
        super().setBasePlane(plane)
        self.addProperty(ToggleProperty("draw_sub_axis", True, updateFunction=self.refreshBasePlane))
        self.addProperty(ToggleProperty("draw_main_axis", True, updateFunction=self.refreshBasePlane))

    # blitUpdate must be implemented correctly (currently with old deviceContext logic for prototyping)
    # -> new version utilises blit from basePlane
    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext):  # TODO: update base class
        if self.getProperty("draw_sub_axis").getValue() is True:
            self.drawSubAxis(deviceContext, 50)
        if self.getProperty("draw_main_axis").getValue() is True:
            self.drawMainAxis(deviceContext)

    def drawSubAxis(self, deviceContext, axisPixelDistance):
        # deviceContext = self.basePlane.memoryDc

        p = wx.Pen(wx.Colour((128, 128, 128)))
        p.SetWidth(1)
        deviceContext.SetPen(p)
        xSubAxis = multiplesInInterval(axisPixelDistance, self._basePlane.db)
        ySubAxis = multiplesInInterval(axisPixelDistance, self._basePlane.wb)
        for x in xSubAxis:
            x, _ = self._basePlane.correctPosition(x, 0)
            deviceContext.DrawLine(x, 0, x, self._basePlane.h)
        for y in ySubAxis:
            _, y = self._basePlane.correctPosition(0, y)
            deviceContext.DrawLine(0, y, self._basePlane.w, y)

    def drawMainAxis(self, deviceContext):
        # deviceContext = self.basePlane.memoryDc

        p = wx.Pen(wx.Colour((0, 0, 0)))
        p.SetWidth(3)
        deviceContext.SetPen(p)
        if self._basePlane.db[0] < 0 < self._basePlane.db[1]:
            x0, _ = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(x0, 0, x0, self._basePlane.h)
        if self._basePlane.wb[0] < 0 < self._basePlane.wb[1]:
            _, y0 = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(0, y0, self._basePlane.w, y0)
