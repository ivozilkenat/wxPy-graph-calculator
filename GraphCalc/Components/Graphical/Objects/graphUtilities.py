import wx

from MyWx.wx import *

from GraphCalc.Components.Property.property import IntProperty, ListProperty, GraphicalPanelObject, ToggleProperty, \
    PropertyObjCategory, StrProperty
from GraphCalc._core import vc

from GraphCalc._core.utilities import multiplesInInterval


class CartesianAxies(GraphicalPanelObject):
    def __init__(self):
        super().__init__(category=PropertyObjCategory.NO_CATEGORY)

        self.getProperty(vc.PROPERTY_NAME)._setValue("Cartesian Coordinate-System")

        self._subAxisInterval = 1

    def setBasePlane(self, plane):
        # Properties must be set here, since update function requires panel
        # todo: is there a design that makes implementing the super method redundant?
        super().setBasePlane(plane)
        self.getProperty(vc.PROPERTY_SELECTABLE)._setValue(False)
        self.addProperty(ToggleProperty(vc.PROPERTY_DRAW_SUB_AXIS, True, updateFunctions=self.refreshBasePlane))
        self.addProperty(ToggleProperty(vc.PROPERTY_DRAW_MAIN_AXIS, True, updateFunctions=self.refreshBasePlane))

        self.addProperty(ToggleProperty("draw_axle_labels", True, updateFunctions=self.refreshBasePlane))
        self.addProperty(ToggleProperty("draw_axle_arrows", True, updateFunctions=self.refreshBasePlane))
        self.addProperty(ToggleProperty("draw_values", True, updateFunctions=self.refreshBasePlane))

        self.addProperty(IntProperty("arrow_head_height", 10, updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("arrow_head_length", 15, updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("arrow_head_overlapping", 4, updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("arrow_draw_width", 1, updateFunctions=self.refreshBasePlane))

        self.addProperty(StrProperty("y_label", "Y", updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("y_axis_label_axis_distance", 15, updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("y_axis_label_border_distance", 10, updateFunctions=self.refreshBasePlane))
        self.addProperty(StrProperty("x_label", "X", updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("x_axis_label_axis_distance", 15, updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("x_axis_label_border_distance", 10, updateFunctions=self.refreshBasePlane))

        self.addProperty(IntProperty("value_label_x_axis_distance", 15, updateFunctions=self.refreshBasePlane))
        self.addProperty(IntProperty("value_label_y_axis_distance", 30, updateFunctions=self.refreshBasePlane))

        c = self.getProperty(vc.PROPERTY_COLOR)
        c._setValue(vc.COLOR_BLACK)
        c.setUpdateFunctions(self.refreshBasePlane)
        self.addProperty(c, override=True)
        self.addProperty(
            ListProperty(
                vc.PROPERTY_COL_SUB_AXIS,
                vc.COLOR_GRAY,
                fixedFieldAmount=3,
                validityFunction=lambda x: 0 <= x <= 255,
                updateFunctions=self.refreshBasePlane
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
        # print(self._basePlane.logicalYToPx(10))
        # print(self._basePlane.logicalYToPx(-10))
        # print(self._basePlane.pxYToLogical(500))
        # print()

    @GraphicalPanelObject.draw(vc.PROPERTY_COL_SUB_AXIS, vc.PROPERTY_SUB_AXIS_DRAW_WIDTH)
    def drawSubAxis(self, deviceContext):

        intervalUpdateFactor = 2  # interval always becomes a multiple of this, if update is necessary

        if self._basePlane.logicalXToPx(self._subAxisInterval) > self._basePlane.Px2LEx * intervalUpdateFactor:
            self._subAxisInterval /= intervalUpdateFactor
        elif self._basePlane.logicalXToPx(self._subAxisInterval) < self._basePlane.Px2LEx:
            self._subAxisInterval *= intervalUpdateFactor

        xSubAxisLog = multiplesInInterval(
            self._subAxisInterval, self._basePlane.getLogicalDB()
        )
        ySubAxisLog = multiplesInInterval(
            self._subAxisInterval, self._basePlane.getLogicalWB()
        )

        xSubAxisPx = [self._basePlane.logicalXToPx(x) for x in xSubAxisLog]
        ySubAxisPx = [self._basePlane.logicalYToPx(y) for y in ySubAxisLog]

        # todo: display numbers with more spacing
        decimalPlaces = 8
        dxLabel = self.getProperty("value_label_x_axis_distance").getValue()
        dyLabel = self.getProperty("value_label_y_axis_distance").getValue()
        labels = list()
        coords = list()

        # todo: fix labeling orientation bug / make transition smoother
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
            tw, th = deviceContext.GetTextExtent(v)
            wbStart, wbEnd = self._basePlane.wb
            labelY = self._basePlane.correctY(0) - dxLabel
            labelX = cx - 1 / 2 * tw

            # todo: maybe add more logic to make y mirroring more easily usable -> would make code extension more easily
            if labelY - dxLabel / 2 <= 0:
                labelY = self._basePlane.correctY((wbEnd if self._basePlane.yIsMirrored() else wbStart)) + dxLabel / 2
            else:
                if self._basePlane.yIsMirrored():
                    if wbStart > 0:
                        labelY = self._basePlane.correctY(wbStart) - dxLabel
                elif wbEnd < 0:
                    labelY = self._basePlane.correctY(wbEnd) - dxLabel

            labels.append(v)
            coords.append((
                labelX,
                labelY
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
            dbStart, dbEnd = self._basePlane.db
            labelY = cy - 1 / 2 * th
            labelX = self._basePlane.correctX(0) - dyLabel

            if labelX - dyLabel / 2 <= 0:
                labelX = self._basePlane.correctX(dbStart) + dyLabel / 2
            elif dbEnd < 0:
                labelX = self._basePlane.correctX(dbEnd) - dyLabel

            labels.append(v)
            coords.append((
                labelX,
                labelY
            ))

        # todo: can this be implemented without calculation overhead?
        if self.getProperty("draw_values").getValue() is True:
            deviceContext.DrawTextList(labels, coords)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_DRAW_WIDTH)
    def drawMainAxis(self, deviceContext):
        if self._basePlane.db[0] < 0 < self._basePlane.db[1]:
            x0, _ = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(x0, 0, x0, self._basePlane.h)
        if self._basePlane.wb[0] < 0 < self._basePlane.wb[1]:
            _, y0 = self._basePlane.correctPosition(0, 0)  # combine functions
            deviceContext.DrawLine(0, y0, self._basePlane.w, y0)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, "arrow_draw_width")
    def drawArrowHeads(self, deviceContext):
        headHeight = self.getProperty("arrow_head_height").getValue()
        headLength = self.getProperty("arrow_head_length").getValue()
        headOverlapping = self.getProperty("arrow_head_overlapping").getValue()

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
            (tipY[0] - headHeight, tipY[1] - headLength - headOverlapping),
            (tipY[0], tipY[1] - headLength),
            (tipY[0] + headHeight, tipY[1] - headLength - headOverlapping)
        ]

        deviceContext.DrawPolygon(xArrow)
        if self._basePlane.yIsMirrored():
            deviceContext.DrawPolygon(self._basePlane.mirrorPointsY(yArrow, tipY[1]))
        else:
            deviceContext.DrawPolygon(yArrow)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_SUB_AXIS_DRAW_WIDTH)
    def drawAxisLabels(self, deviceContext):
        label = self.getProperty("y_label").getValue()
        _, th = deviceContext.GetTextExtent(label)
        deviceContext.DrawText(
            label,
            *self._basePlane.correctPosition(
                self.getProperty("y_axis_label_axis_distance").getValue(),
                self._basePlane.wb[-1] - (0 if self._basePlane.yIsMirrored() else th) - self.getProperty(
                    "y_axis_label_border_distance").getValue())
        )
        label = self.getProperty("x_label").getValue()
        tw, th = deviceContext.GetTextExtent(label)
        deviceContext.DrawText(
            label,
            *self._basePlane.correctPosition(
                self._basePlane.db[-1] - tw - self.getProperty("x_axis_label_border_distance").getValue(),
                self.getProperty("x_axis_label_axis_distance").getValue() + (
                    th if self._basePlane.yIsMirrored() else 0))
        )
