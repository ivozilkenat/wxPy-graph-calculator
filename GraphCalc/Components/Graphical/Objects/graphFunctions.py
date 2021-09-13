from MyWx.wx import *

from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.property import PropertyObjCategory, GraphicalPanelObject, FloatProperty
from GraphCalc._core.utilities import timeMethod
from GraphCalc._core import vc

import numpy as np


# Current implementation only for testing purposes / lacks optimization

class MathFunction():
    def __init__(self, functionAsLambda):
        self.functionAsLambda = functionAsLambda


class DefinitionArea():
    vCoeff = 10

    def __init__(self, closedInterval, valueAmount=None):
        if len(closedInterval) != 2:
            raise ValueError("Valid interval must be of Type (start, end)")

        self.closedInterval = closedInterval

        if closedInterval != -1:
            if valueAmount is not None:
                self.valueAmount = valueAmount
            else:
                self.valueAmount = abs(int((self.closedInterval[0] - self.closedInterval[1]) * DefinitionArea.vCoeff))
            self.values = np.linspace(*self.closedInterval, self.valueAmount)
        else:
            self.value = None

    def __iter__(self):
        if self.closedInterval == -1:
            return -1  # extra Object ? smth. like infinite interval
        else:
            return iter(self.values)


class GraphFunction2D(GraphicalPanelObject, MathFunction):
    _basePlane: Dynamic2DGraphicalPlane
    def __init__(self, functionAsLambda, definitionArea=None):
        MathFunction.__init__(self, functionAsLambda)
        GraphicalPanelObject.__init__(self, category=PropertyObjCategory.FUNCTION)

        self.func = functionAsLambda
        self.definitionArea = definitionArea

        self.valueAmount = None
        self.arguments = None
        self.values = None

        self.getProperty(vc.PROPERTY_NAME).setValue("Funktion2D")

    def setBasePlane(self, plane):
        # Properties must be set here, since update function requires panel
        # todo: is there a design that makes implementing the super method redundant?
        super().setBasePlane(plane)
        self.addProperty(FloatProperty(vc.PROPERTY_FUNC_COEFF, 3.5, updateFunction=self.refreshBasePlane, increment=0.1))
        #todo: distinguish by type of function (e.g linear functions can be drawn with less detail)

    def calculateValueTuples(self, arguments):
        return [self.func(i) for i in arguments]

    def calculateData(self):
        self.valueAmount = abs(int((self._basePlane.getLogicalDB()[0] - self._basePlane.getLogicalDB()[1]) * self.getProperty(vc.PROPERTY_FUNC_COEFF).getValue()))
        self.arguments = np.linspace(*self._basePlane.getLogicalDB(), self.valueAmount)
        self.values = self.calculateValueTuples(self.arguments)

    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext, needValueUpdate=True):
        # a lot of redundant calculation, since everything is done twice
        # todo: due to new structure, values should only be recalculated if updated is needed
        if needValueUpdate:
            self.calculateData()
        self.draw(deviceContext)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_DRAW_WIDTH)
    def draw(self, deviceContext):
        for i in range(1, len(self.arguments)):
            x1, y1 = self._basePlane.logicalPointToPx(
                self.arguments[i - 1],
                self.values[i - 1]
            )
            x2, y2 = self._basePlane.logicalPointToPx(
                self.arguments[i],
                self.values[i]
            )


            #todo: just a quick implementation for testing purposes
            #todo: implement after using logical coordinates
            yBottom, yTop = self._basePlane.wb
            # only check if y, since x is always in db-area
            if yBottom <= y1 <= yTop or yBottom <= y2 <= yTop:
                deviceContext.DrawLine(
                    *self._basePlane.correctPosition(x1, y1),
                    *self._basePlane.correctPosition(x2, y2)
                )

