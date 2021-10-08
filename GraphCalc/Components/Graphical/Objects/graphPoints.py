from MyWx.wx import *

from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Property.property import PropertyObjCategory, GraphicalPanelObject, SelectProperty, \
    ExprProperty, FloatProperty, IExprProperty, DependentProperty, ReadOnlyProperty, ExprReadOnlyProperty
from GraphCalc.Calc.graphCalculator import Point2DExpr

from GraphCalc._core.utilities import timeMethod
from GraphCalc._core import vc

from sympy import *

import numpy as np

class GraphPoint2D(GraphicalPanelObject, IExprProperty):
    _basePlane: Dynamic2DGraphicalPlane
    strName = "Point"

    def __init__(self, graphCalculator, pointExpression):
        GraphicalPanelObject.__init__(self, category=PropertyObjCategory.POINT)
        IExprProperty.__init__(self, graphCalculator, pointExpression)

    def setBasePlane(self, plane):
        super().setBasePlane(plane)
        self.getProperty(vc.PROPERTY_DRAW_WIDTH)._setValue(5)

        self.addProperty(
            ExprProperty(
                "point_definition",
                self._exprObj,
                self._graphCalc,
                updateFunctions=self.refreshBasePlane,
                updateExprFunction=self.redefineAllExpressions
            )
        )
        self.addProperty(
            DependentProperty(
                self.getProperty("point_definition"),
                ExprReadOnlyProperty(
                    "evaluation",
                    ""
                ),
                updateFunction=self._evalPoint,
                checkValidity=False
            )
        )

    def _evalPoint(self):
        return simplify(self._getPointExpr())

    def _getPointExpr(self):
        return self.getProperty("point_definition").getValue().expr()

    def _canBeDrawn(self):
        if any([not i.is_number for i in self._evalPoint()]):
            return False
        return True

    @GraphicalPanelObject.standardProperties
    def blitUpdate(self, deviceContext: wx.DC, needValueUpdate=True):
        if self._canBeDrawn():
            self.drawPoint(deviceContext)

    @GraphicalPanelObject.draw(vc.PROPERTY_COLOR, vc.PROPERTY_DRAW_WIDTH)
    def drawPoint(self, deviceContext):
        x, y = self._evalPoint().coordinates
        if self._basePlane.logicalPointInView(x, y):
            deviceContext.DrawCircle(
                *self._basePlane.logicalPointToCorrect(x, y),
                int(self.getProperty(vc.PROPERTY_DRAW_WIDTH).getValue()*0.5)
            )


