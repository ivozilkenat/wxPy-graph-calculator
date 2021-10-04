from MyWx.wx import *

from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.property import PropertyObjCategory, GraphicalPanelObject, SelectProperty, \
    ExprProperty, FloatProperty, IExprProperty, DependentProperty, ReadOnlyProperty, ExprReadOnlyProperty
from GraphCalc.Calc.graphCalculator import Function2DExpr

from GraphCalc._core.utilities import timeMethod
from GraphCalc._core import vc

from sympy import *

import numpy as np

# ignores warnings, which may appear by calculating with illegal arguments (e.g. sqrt(-1))
np.seterr(all="ignore")


# todo: utilize this class for defined intervals for functions
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


# Current implementation only for testing purposes / lacks optimization
# class MathFunction():
#     def __init__(self, funcExpression):
#         self._funcExpression = funcExpression

# todo:
#   -defy definition loops
#   -allow for definition intervals to be utilized
#   -optimization depending on the function type

class GraphFunction2D(GraphicalPanelObject, IExprProperty):  # MathFunction):
    _basePlane: Dynamic2DGraphicalPlane
    strName = "Function"
    def __init__(self, graphCalculator, functionExpression, definitionArea=None):
        GraphicalPanelObject.__init__(self, category=PropertyObjCategory.FUNCTION)
        IExprProperty.__init__(self, graphCalculator, functionExpression)

        self.definitionArea = definitionArea

        self.valueAmount = None
        self.arguments = None
        self.values = None

        self._functionAsCallable = None

        self.getProperty(vc.PROPERTY_NAME)._setValue("Function2D")

    def setBasePlane(self, plane):
        # Properties must be set here, since update function requires panel
        # todo: use color property
        # todo: is there a design that makes implementing the super method redundant?
        super().setBasePlane(plane)
        self.addProperty(
            FloatProperty(vc.PROPERTY_FUNC_COEFF, 0.1, updateFunctions=self.refreshBasePlane, increment=0.01)
        )
        # todo: distinguish by type of function (e.g linear functions can be drawn with less detail)
        #       -> optimize draw speed

        self.addProperty(
            ExprProperty(
                "function_definition",
                self._exprObj,
                self._graphCalc,
                updateFunctions=self.refreshBasePlane,
                updateExprFunction=self.redefineAllExpressions
            ))

        self.addProperty(
            DependentProperty(
                self.getProperty("function_definition"),
                ExprReadOnlyProperty(
                    "function_simplified",
                    ""
                ),
                updateFunction=self._simplifiedFunction,
                checkValidity=False
            )
        )

        self.addProperty(
            DependentProperty(
                self.getProperty("function_definition"),
                ExprReadOnlyProperty(
                    "intersections",
                    ""
                ),
                updateFunction=self._calcIntersections,
                checkValidity=False
            )
        )

        self.addProperty(
            DependentProperty(
                self.getProperty("function_definition"),
                ExprReadOnlyProperty(
                    "first_derivative",
                    ""
                ),
                updateFunction=self._calcDiff1,
                checkValidity=False
            )
        )

        self.addProperty(
            DependentProperty(
                self.getProperty("function_definition"),
                ExprReadOnlyProperty(
                    "second_derivative",
                    ""
                ),
                updateFunction=self._calcDiff2,
                checkValidity=False
            )
        )

        self.addProperty(
            DependentProperty(
                self.getProperty("function_definition"),
                ExprReadOnlyProperty(
                    "third_derivative",
                    ""
                ),
                updateFunction=self._calcDiff3,
                checkValidity=False
            )
        )

        self.addProperty(
            DependentProperty(
                self.getProperty("function_definition"),
                ExprReadOnlyProperty(
                    "integral",
                    ""
                ),
                updateFunction=self._calcIntegral,
                checkValidity=False
            )
        )

        self.addProperty(
            SelectProperty(
                "point_interval_approximation",
                (
                    "linearFirstValue",
                    "interval",
                    "slope",
                    "linear"
                ),
                selectedIndex=0,
                updateFunctions=self.refreshBasePlane
            )
        )

        # add more properties?

    def _simplifiedFunction(self):
        return simplify(self._getFuncExpr())

    def _calcIntersections(self):
        try:
            return solve(self._getFuncExpr(), quick=True, simplify=True, rational=False)
        except NotImplementedError:
            return "Not solvable"

    def _calcDiff1(self):
        try:
            return diff(self._getFuncExpr(), Function2DExpr.argumentSymbol)
        except NotImplementedError:
            return "Not derivable"

    def _calcDiff2(self):
        try:
            return diff(self.getProperty("first_derivative").getValue(), Function2DExpr.argumentSymbol)
        except NotImplementedError:
            return "Not derivable"

    def _calcDiff3(self):
        try:
            return diff(self.getProperty("second_derivative").getValue(), Function2DExpr.argumentSymbol)
        except NotImplementedError:
            return "Not derivable"

    def _calcIntegral(self):
        try:
            return integrate(self._getFuncExpr(), Function2DExpr.argumentSymbol)
        except NotImplementedError:
            return "Not integrable"

    def _getFuncExpr(self):
        return self.getProperty("function_definition").getValue().expr()

    def exprIsEvaluable(self):
        expr = self.getProperty("function_definition").getValue()
        # testing if evaluable, by trying to get a number value for x = 1 | x != 0 todo: can values be not continuously
        res = expr.expr().subs(Function2DExpr.argumentSymbol, 1)
        return res.is_number  # todo: test this

    def getFuncAsCallable(self):
        return self._functionAsCallable

    @timeMethod
    def calculateData(self):
        if self.exprIsEvaluable():
            # todo: optimize -> calculate values based on dominant areas of point density
            #   -stop using class attributes
            self.valueAmount = int(self._basePlane.getDBLength() * self.getProperty(vc.PROPERTY_FUNC_COEFF).getValue())
            # completely overhaul argument calculation -> thereby value calculation
            # todo: calculate all arguments, which are expected to give valid results:
            #       -find max -> prevent calculating points out of view -> point density
            #       -calc valid values for expression to prevent invalid arguments
            exprObj = self.getProperty("function_definition").getValue().expr()

            #   get values for which the function is defined
            self._functionAsCallable = lambdify(Function2DExpr.argumentSymbol, exprObj)

            # todo: use precalculation
            #       -check for values inside after calc and recalc
            #       -add standardFirstValue to interval algo -> make new standard
            #       -rename "standard" algorithm
            #       -other approach: calc nearly all values -> calc necessary points (check slope in intervals)
            #       -bug: linearFirstValue glitching, when not zoomed in any way (sometimes, drawlines error)

            algo = self.getProperty("point_interval_approximation").getSelected()
            if algo == "linear":
                self.linearApproximation()
            elif algo == "linearFirstValue":
                self.linearFindStartApproximation()
            elif algo == "slope":
                self.slopeApproximation(20)
            elif algo == "interval":
                self.intervalApproximation()
            else:
                self.values = None
        else:
            self.values = None

    def linearApproximation(self):
        self.arguments = np.linspace(*self._basePlane.getLogicalDB(), self.valueAmount)
        self.values = np.array([[self._functionAsCallable(i) for i in self.arguments]])
        self.arguments = np.array([self.arguments])

    def linearFindStartApproximation(self, approximationThreshold=0.001, fast=False):
        self.linearApproximation()
        deltaX = self._basePlane.getLogicalDBLength() / self.valueAmount
        threshold = deltaX * approximationThreshold
        values, args = self.values[0], self.arguments[0]
        inserts = 0
        for index, value in enumerate(values):
            if not np.isnan(value) and np.isnan(values[index - 1]):
                k = 2
                oldArg = args[index]
                newArg = oldArg
                newDelta = -(deltaX / k)
                while abs(newDelta) > threshold:
                    newArg += newDelta
                    newVal = self._functionAsCallable(newArg)
                    k *= 2
                    if np.isnan(newVal):
                        newDelta = (deltaX / k)
                    else:
                        newDelta = -(deltaX / k)

                if np.isnan(newVal):
                    if fast:
                        newArg = oldArg
                    else:
                        while newArg < oldArg:
                            newArg += abs(newDelta)
                            if not np.isnan(self._functionAsCallable(newArg)):
                                break
                        else:
                            newArg = oldArg

                self.arguments = np.array([np.insert(self.arguments[0], index + inserts, newArg)])
                self.values = np.array([np.insert(self.values[0], index + inserts, self._functionAsCallable(newArg))])

                inserts += 1

    def slopeApproximation(self, n, minValFactor=0.075):
        # divide db into n intervals and check median slope, determine proportion -> assign values
        minValues = int(self.valueAmount * minValFactor)
        if minValues <= 2:
            minValues = 2
        dbStart, dbEnd = self._basePlane.getLogicalDB()
        step = self._basePlane.getLogicalDBLength() / n
        intervals = list()
        intervals.append((dbStart, dbStart + step))
        while len(intervals) < n:
            intervals.append(
                (intervals[-1][-1], intervals[-1][-1] + step)
            )
        slopes = list()
        for x0, x1 in intervals:
            y0, y1 = self._functionAsCallable(x0), self._functionAsCallable(x1)
            if any(np.isnan(v) for v in (y0, y1)):  # check if nan in calculated values
                continue
            slopes.append(
                ((x0, x1), abs(((y1 - y0) / (x1 - x0)) ** -1))
            )
        sumSlopes = sum([s[1] for s in slopes])
        arguments = list()
        for interval, m in slopes:
            x0, x1 = interval
            va = int(self.valueAmount * (m / sumSlopes))
            if va <= 1:
                va = minValues
            arguments.append(
                np.linspace(x0, x1, va, dtype=np.float)
            )
        # calculate arguments
        self.arguments = np.concatenate(arguments)

        # calculate values
        self.values = np.array(
            [np.fromiter(map(lambda x: self._functionAsCallable(x), self.arguments), dtype=np.float)]
        )

        self.arguments = np.array([self.arguments])

    def intervalApproximation(self):
        # todo: redundant?
        # -> to slow, with to many errors
        visibleIntervals = self.findArgsInVisible(self._functionAsCallable, 150, precision=0.05)
        if (visibleAmount := len(visibleIntervals)) == 0:
            self.values = None
            return
        else:
            amountPerInterval = int(self.valueAmount / visibleAmount)

        self.arguments = np.array([
            np.linspace(i[0], i[1], amountPerInterval) for i in visibleIntervals
        ])

        self.values = np.array([
            np.fromiter(map(lambda x: self._functionAsCallable(x), interval), dtype=np.float) for interval in self.arguments
        ])
        # todo: decide by average value, if function should be drawn
        #       or by size of interval

    def inLogicalWbList(self, *values):
        lowerWb, upperWb = self._basePlane.getLogicalWB()
        return [lowerWb <= v <= upperWb for v in values]

    def inLogicalWb(self, *values):
        lowerWb, upperWb = self._basePlane.getLogicalWB()
        return any([lowerWb <= v <= upperWb for v in values])

    def findArgsInVisible(self, callableExpr, checkAmount, precision=0.01, approximationThreshold=0.0001):
        lowerLimit, upperLimit = self._basePlane.getLogicalDB()
        deltaX = self._basePlane.getLogicalDBLength() / checkAmount
        deltaXAdjust = deltaX * precision

        checkArgs = np.linspace(lowerLimit - deltaXAdjust, upperLimit + deltaXAdjust, checkAmount)
        values = np.fromiter(map(callableExpr, checkArgs), dtype=np.float)

        visibleIntervals = []
        for arg, value in zip(checkArgs, values):
            if self.inLogicalWb(value):
                if visibleIntervals != []:
                    last = visibleIntervals[-1]
                    if last[0] - deltaXAdjust <= arg <= last[1] + deltaXAdjust:
                        continue

                interval = []
                # left side
                outOfDB = False
                newArg = arg - deltaXAdjust
                while self.inLogicalWb(callableExpr(newArg)):
                    newArg -= deltaXAdjust
                    if not lowerLimit - deltaXAdjust < newArg:
                        newArg = lowerLimit - deltaXAdjust
                        outOfDB = True
                        break

                    if visibleIntervals != []:
                        last = visibleIntervals[-1]
                        if last[0] + deltaXAdjust >= newArg:
                            break

                if not outOfDB:
                    assert approximationThreshold <= 1
                    aMin, aMax = newArg - deltaXAdjust, newArg + deltaXAdjust
                    deltaA = aMax - aMin
                    threshold = deltaA * approximationThreshold
                    k = 2
                    newDelta = deltaA / k
                    while abs(newDelta) > threshold:
                        newArg -= newDelta
                        k *= 2
                        if self.inLogicalWb(callableExpr(newArg)):
                            newDelta = (deltaA / k)
                        else:
                            newDelta = -(deltaA / k)

                interval.append(newArg)

                # right side
                outOfDB = False
                newArg = arg + deltaXAdjust
                while self.inLogicalWb(callableExpr(newArg)):
                    newArg += deltaXAdjust
                    if not newArg < upperLimit + deltaXAdjust:
                        newArg = upperLimit + deltaXAdjust
                        outOfDB = True
                        break

                # todo: outsource into method?
                if not outOfDB:
                    assert approximationThreshold <= 1
                    aMin, aMax = newArg - deltaXAdjust, newArg + deltaXAdjust
                    print(aMin, aMax, newArg)
                    deltaA = aMax - aMin
                    threshold = deltaA * approximationThreshold
                    k = 2
                    newDelta = deltaA / k
                    while abs(newDelta) > threshold:
                        newArg += newDelta
                        k *= 2
                        if self.inLogicalWb(callableExpr(newArg)):
                            newDelta = (deltaA / k)
                        else:
                            newDelta = -(deltaA / k)

                interval.append(newArg)
                visibleIntervals.append(interval)
        return visibleIntervals

    # todo: redundant?
    # to slow
    def getWBIntersections(self, expression):
        lowerY, upperY = self._basePlane.getLogicalWB()  # todo: test if working wrong when not mirrored

        upperInter = solve(expression - lowerY, quick=True)
        lowerInter = solve(expression - upperY, quick=True)
        return list(filter(lambda x: x.is_real, upperInter)), list(filter(lambda x: x.is_real, lowerInter))

    # todo: redundant?
    # def calcMaxAndMin(self, expression):
    #     maxs, mins = list(), list()
    #     diff1 = diff(expression, Function2DExpr.argumentSymbol)
    #     diff2 = diff(diff1, Function2DExpr.argumentSymbol)
    #
    #     if not diff2.is_zero:
    #         sol = solve(diff1)
    #         for s in sol:
    #             r = diff2.subs(Function2DExpr.argumentSymbol, s)
    #             if r.is_real:
    #                 if r > 0:
    #                     mins.append(s)
    #                 elif r < 0:
    #                     maxs.append(s)
    #     return maxs, mins

    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext, needValueUpdate=True):
        # a lot of redundant calculation, since everything is done twice
        # todo: due to new structure, values should only be recalculated if updated is needed
        if needValueUpdate:
            # todo: optimization for values, which don't have to be computed
            r = self.calculateData()
            # print(f"time needed: {r}s")
        if self.values is None:
            self._drawable = False
            return  # -> expression is not evaluable
        else:
            self._drawable = True

        self.draw(deviceContext)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_DRAW_WIDTH)
    def draw(self, deviceContext):
        points = list()
        # arguments and values must be nested to allow for drawing of separate intervals
        for i, interval in enumerate(self.values):
            for j in range(1, len(interval)):
                a0, ax, = self.arguments[i][j - 1], self.arguments[i][j]
                v0, vx = self.values[i][j - 1], self.values[i][j]

                if any(np.isnan(v) or v == float("inf") for v in (v0, vx)):  # check if nan in calculated values
                    continue

                x1, y1 = self._basePlane.logicalPointToPx(
                    a0, v0
                )
                x2, y2 = self._basePlane.logicalPointToPx(
                    ax, vx
                )

                # todo: just a quick implementation for testing purposes
                # todo: implement after using logical coordinates
                yBottom, yTop = self._basePlane.wb
                # only check if y, since x is always in db-area
                if yBottom <= y1 <= yTop or yBottom <= y2 <= yTop:
                    points.append([
                        *self._basePlane.correctPosition(x1, y1),
                        *self._basePlane.correctPosition(x2, y2)
                    ])
        if len(points) > 0:
            deviceContext.DrawLineList(points)
