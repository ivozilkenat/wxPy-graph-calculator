from MyWx.wx import *

from GraphCalc.Components.Property.property import IntProperty, ListProperty, GraphicalPanelObject, ToggleProperty, \
    PropertyObjCategory
from GraphCalc._core import vc

from GraphCalc._core.utilities import multiplesInInterval


class CartesianAxies(GraphicalPanelObject):
    def __init__(self):
        super().__init__(category=PropertyObjCategory.NO_CATEGORY)

        self.getProperty(vc.PROPERTY_NAME).setValue("Cartesian Coordinate-System")

    def setBasePlane(self, plane):
        # Properties must be set here, since update function requires panel
        # todo: is there a design that makes implementing the super method redundant?
        super().setBasePlane(plane)
        self.getProperty(vc.PROPERTY_SELECTABLE).setValue(False)
        self.addProperty(ToggleProperty(vc.PROPERTY_DRAW_SUB_AXIS, True, updateFunction=self.refreshBasePlane))
        self.addProperty(ToggleProperty(vc.PROPERTY_DRAW_MAIN_AXIS, True, updateFunction=self.refreshBasePlane))
        c = self.getProperty(vc.PROPERTY_COLOR)
        c.setValue(vc.COLOR_BLACK)
        c.setUpdateFunction(self.refreshBasePlane)
        self.addProperty(c, override=True)
        self.addProperty(
            ListProperty(
                vc.PROPERTY_COL_SUB_AXIS,
                vc.COLOR_GRAY,
                fixedFieldAmount=3,
                validityFunction=lambda x: 0 <= x <= 255,
                updateFunction=self.refreshBasePlane
            )
        )
        self.addProperty(IntProperty(vc.PROPERTY_SUB_AXIS_DRAW_WIDTH, 1, self.refreshBasePlane))

    # todo: add update function as paramter, so values are not newly calculated if id draw is happenening

    # blitUpdate must be implemented correctly (currently with old deviceContext logic for prototyping)
    # -> new version utilises blit from basePlane
    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext, **kwargs):  # TODO: update base class
        if self.getProperty(vc.PROPERTY_DRAW_SUB_AXIS).getValue() is True:
            self.drawSubAxis(deviceContext)
        if self.getProperty(vc.PROPERTY_DRAW_MAIN_AXIS).getValue() is True:
            self.drawMainAxis(deviceContext)

    #todo: sub axis cause crash
    @GraphicalPanelObject.draw(vc.PROPERTY_COL_SUB_AXIS, vc.PROPERTY_SUB_AXIS_DRAW_WIDTH)
    def drawSubAxis(self, deviceContext):

        zoom = self._basePlane.zoomFactorX

        interval = 1
        print("interval: ", interval)

        xSubAxis = multiplesInInterval(
            self._basePlane.logicalXToPx(interval), self._basePlane.db
        )
        ySubAxis = multiplesInInterval(
            self._basePlane.logicalYToPx(interval), self._basePlane.wb
        )

        for x in xSubAxis:
            x, _ = self._basePlane.correctPosition(x, 0)
            deviceContext.DrawLine(x, 0, x, self._basePlane.h)
        for y in ySubAxis:
            _, y = self._basePlane.correctPosition(0, y)
            deviceContext.DrawLine(0, y, self._basePlane.w, y)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_DRAW_WIDTH)
    def drawMainAxis(self, deviceContext):
        # deviceContext = self.basePlane.memoryDc
        if self._basePlane.db[0] < 0 < self._basePlane.db[1]:
            x0, _ = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(x0, 0, x0, self._basePlane.h)
        if self._basePlane.wb[0] < 0 < self._basePlane.wb[1]:
            _, y0 = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(0, y0, self._basePlane.w, y0)
