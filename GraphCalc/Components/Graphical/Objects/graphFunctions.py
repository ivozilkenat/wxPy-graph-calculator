from MyWx.wx import *

from GraphCalc.Components.Property.property import PropertyObjCategory, GraphicalPanelObject
from GraphCalc._core.utilities import timeMethod

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
    def __init__(self, functionAsLambda, definitionArea=None):
        MathFunction.__init__(self, functionAsLambda)
        GraphicalPanelObject.__init__(self, category=PropertyObjCategory.FUNCTION)

        self.func = functionAsLambda
        self.definitionArea = definitionArea

        self.valueCoeff = 0.3

        self.valueAmount = None
        self.arguments = None
        self.values = None

        self.getProperty("name").setValue("Funktion2D")

    def calculateValueTuples(self, arguments):
        return [self.func(i) for i in arguments]

    def calculateData(self):
        self.valueAmount = abs(int((self._basePlane.db[0] - self._basePlane.db[1]) * self.valueCoeff))
        self.arguments = np.linspace(*self._basePlane.db, self.valueAmount)
        self.values = self.calculateValueTuples(self.arguments)

    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext, **kwargs):
        # a lot of redundant calculation, since everything is done twice
        # todo: due to new structure, values should only be recalculated if updated is needed
        self.calculateData()
        self.draw(deviceContext)

    @GraphicalPanelObject.draw("color", "draw_width")
    def draw(self, deviceContext):
        for i in range(1, len(self.arguments)):
            deviceContext.DrawLine(*self._basePlane.correctPosition(self.arguments[i - 1], self.values[i - 1]),
                                   *self._basePlane.correctPosition(self.arguments[i], self.values[i]))
