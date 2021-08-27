from MyWx.wx import *

import numpy as np
from GraphCalc.Components.Property._property import GraphicalPanelObject


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
        super().__init__(functionAsLambda)

        self.func = functionAsLambda
        self.definitionArea = definitionArea

        self.valueCoeff = 1

        self.properties["name"].setValue("Funktion2D")

    def calculateValueTuples(self, arguments):
        return [self.func(i) for i in arguments]

    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext):
        p = wx.Pen(wx.Colour((255, 0, 0)))
        p.SetWidth(2)
        deviceContext.SetPen(p)

        valueAmount = abs(int((self.basePlane.db[0] - self.basePlane.db[1]) * self.valueCoeff))

        arguments = np.linspace(*self.basePlane.db, valueAmount)

        values = self.calculateValueTuples(arguments)
        for i in range(1, len(arguments)):
            deviceContext.DrawLine(*self.basePlane.correctPosition(arguments[i - 1], values[i - 1]),
                                   *self.basePlane.correctPosition(arguments[i], values[i]))
