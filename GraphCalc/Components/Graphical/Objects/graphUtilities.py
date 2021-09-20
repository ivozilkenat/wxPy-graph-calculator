import wx

from MyWx.wx import *

from GraphCalc.Components.Property.property import IntProperty, ListProperty, GraphicalPanelObject, ToggleProperty, \
    PropertyObjCategory
from GraphCalc._core import vc

from GraphCalc._core.utilities import multiplesInInterval


class CartesianAxies(GraphicalPanelObject):
    def __init__(self):
        super().__init__(category=PropertyObjCategory.NO_CATEGORY)

        self.getProperty(vc.PROPERTY_NAME).setValue("Cartesian Coordinate-System")


        self._subAxisInterval = 1

    def setBasePlane(self, plane):
        # Properties must be set here, since update function requires panel
        # todo: is there a design that makes implementing the super method redundant?
        super().setBasePlane(plane)
        self.getProperty(vc.PROPERTY_SELECTABLE).setValue(False)
        self.addProperty(ToggleProperty(vc.PROPERTY_DRAW_SUB_AXIS, True, updateFunction=self.refreshBasePlane))
        self.addProperty(ToggleProperty(vc.PROPERTY_DRAW_MAIN_AXIS, True, updateFunction=self.refreshBasePlane))
        self.addProperty(ToggleProperty("draw_axle_labels", True, updateFunction=self.refreshBasePlane))
        self.addProperty(ToggleProperty("draw_axle_arrows", True, updateFunction=self.refreshBasePlane))
        self.addProperty(ToggleProperty("draw_values", True, updateFunction=self.refreshBasePlane))
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

        if self.getProperty("draw_axle_arrows").getValue() is True:
            self.drawArrowHeads(deviceContext)
        if self.getProperty("draw_axle_labels").getValue() is True:
            self.drawAxisLabels(deviceContext)

    #todo: sub axis cause crash
    @GraphicalPanelObject.draw(vc.PROPERTY_COL_SUB_AXIS, vc.PROPERTY_SUB_AXIS_DRAW_WIDTH)
    def drawSubAxis(self, deviceContext):

        intervalUpdateFactor = 2

        if self._basePlane.logicalXToPx(self._subAxisInterval) > self._basePlane.Px2LEx * intervalUpdateFactor:
            self._subAxisInterval /= intervalUpdateFactor
        elif self._basePlane.logicalXToPx(self._subAxisInterval) < self._basePlane.Px2LEx / intervalUpdateFactor:
            self._subAxisInterval *= intervalUpdateFactor

        xSubAxisLog = multiplesInInterval(
            self._subAxisInterval, self._basePlane.getLogicalDB()
        )
        ySubAxisLog = multiplesInInterval(
            self._subAxisInterval, self._basePlane.getLogicalWB()
        )

        xSubAxisPx = [self._basePlane.logicalXToPx(x) for x in xSubAxisLog]
        ySubAxisPx =[self._basePlane.logicalYToPx(y) for y in ySubAxisLog]

        #todo: outsource this
        decimalPlaces = 8
        dxLabel = 15
        dyLabel = 30
        labels = list()
        coords = list()

        #todo: fix labeling orientation bug
        # Draw sub axis
        for x in xSubAxisPx:
            if x == 0:
                continue
            cx, _ = self._basePlane.correctPosition(x, 0)
            deviceContext.DrawLine(cx, 0, cx, self._basePlane.h)

            # add labeling
            v = str(
                round(self._basePlane.pxXToLogical(x), decimalPlaces)
            )
            tw, _ = deviceContext.GetTextExtent(v)
            if self._basePlane.wb[0] < 0 < self._basePlane.wb[1]:
                labels.append(v)
                coords.append((
                    cx - 1/2 * tw,
                    self._basePlane.correctY(0)-dxLabel
                ))
            else:
                labels.append(v)
                coords.append((
                    cx - 1 / 2 * tw,
                    self._basePlane.correctY(self._basePlane.wb[-1]) - dxLabel
                ))

        for y in ySubAxisPx:
            if y == 0:
                continue
            _, cy = self._basePlane.correctPosition(0, y)
            deviceContext.DrawLine(0, cy, self._basePlane.w, cy)

            # add labeling
            v = str(
                round(self._basePlane.pxYToLogical(y), decimalPlaces)
            )
            _, th = deviceContext.GetTextExtent(v)
            if self._basePlane.db[0] < 0 < self._basePlane.db[1]:
                labels.append(v)
                coords.append((
                    self._basePlane.correctX(0) - dyLabel,
                    cy - 1 / 2 * th
                ))
            else:
                labels.append(v)
                coords.append((
                    self._basePlane.correctX(self._basePlane.db[-1]) - dyLabel,
                    cy - 1 / 2 * th
                ))

        #todo: can this be implemented without calculation overhead?
        if self.getProperty("draw_values").getValue() is True:
            deviceContext.DrawTextList(labels, coords)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_DRAW_WIDTH)
    def drawMainAxis(self, deviceContext):
        # deviceContext = self.basePlane.memoryDc
        if self._basePlane.db[0] < 0 < self._basePlane.db[1]:
            x0, _ = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(x0, 0, x0, self._basePlane.h)
        if self._basePlane.wb[0] < 0 < self._basePlane.wb[1]:
            _, y0 = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(0, y0, self._basePlane.w, y0)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_SUB_AXIS_DRAW_WIDTH)
    def drawArrowHeads(self, deviceContext):
        headHeight = 10 # todo: outsource constants
        headLength = 15
        headOverlapping = 4

        # Vector-operations
        tipX = self._basePlane.correctPosition(self._basePlane.db[-1], 0)
        xArrow = [
            tipX,
            (tipX[0] - headLength - headOverlapping, tipX[1] + headHeight),
            (tipX[0] - headLength, tipX[1]),
            (tipX[0] - headLength - headOverlapping, tipX[1] - headHeight),
        ]

        tipY = self._basePlane.correctPosition(0, self._basePlane.wb[-1])
        yArrow = [
            tipY,
            (tipY[0]-headHeight, tipY[1]-headLength-headOverlapping),
            (tipY[0], tipY[1]-headLength),
            (tipY[0] + headHeight, tipY[1] - headLength - headOverlapping)
        ]

        deviceContext.DrawPolygon(xArrow)
        deviceContext.DrawPolygon(yArrow)


    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_SUB_AXIS_DRAW_WIDTH)
    def drawAxisLabels(self, deviceContext):
        dAxle = 15 # todo: outsource constants
        dBorder = 10
        yLabel = "Y"
        _, th = deviceContext.GetTextExtent(yLabel)
        deviceContext.DrawText(
            yLabel,
            *self._basePlane.correctPosition(dAxle, self._basePlane.wb[-1] - th - dBorder)
        )
        xLabel = "X"
        tw, _ = deviceContext.GetTextExtent(xLabel)
        deviceContext.DrawText(
            xLabel,
            *self._basePlane.correctPosition(self._basePlane.db[-1] - tw - dBorder, dAxle)
        )