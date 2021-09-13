import wx

from MyWx.wx import *
from GraphCalc.Components.Property.property import GraphicalPanelObject
from GraphCalc._core import vc

from typing import Union, Tuple


# positions as tuples or individual arguments?
# add more assertions or further type checking
# add interactive selection of displayed objects
# 3 coordinate system

# Baseclass for Base-Panels
# -> Foundation of every layer-system
class GraphicalPanel(GenericPanel):
    def __init__(self, parent=None, size=None):
        super().__init__(parent, size)
        # self.bitmap = None
        # self.memoryDc = None

        self.Bind(wx.EVT_SIZE, self._resize)
        self.Bind(wx.EVT_PAINT, self._onPaint)  # Difference EVT_Paint, etc.
        self.Bind(wx.EVT_MOTION, self._mouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self._leftMouseUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._leftMouseUp)
        self.Bind(wx.EVT_MOUSEWHEEL, self._mousewheel)

        self.layers = list()  # Exchange with priority queue

        # self.SetDoubleBuffered(True)

        self.backgroundColor = (255, 255, 255)

    # self.addProperty(Property("background_color", (255, 255, 255))) # <- metaclass conflict (must be resolved) if derived from Property

    # returns current layers and order
    def getLayerOrder(self):
        return [(0, self)] + [(c + 1, o) for c, o in enumerate(self.layers)]

    # TODO: Change layer into a propertyObject to manage object order

    # adds gpo at desired position in layer-stack
    def addGraphicalObject(self, graphicalObject, priorityIndex=None, setBasePlane=True):
        if setBasePlane:
            graphicalObject.setBasePlane(self)
        if priorityIndex is None:
            self.layers.append(graphicalObject)
        else:
            self.layers.insert(priorityIndex, graphicalObject)

    def removeGraphicalObject(self, graphicalObject):
        self.layers.remove(graphicalObject)

    def _onPaint(self, event=None):
        """
        OnPaint-Event-Receiver
        """

    # Predefined Event-Receivers (design must be approved of)
    def updatePlaneData(self, event=None):
        """
        Updates values of plane
        """
        pass

    def _mouseMotion(self, event=None):
        """
        Mouse motion receiver
        Updates position of origin and refreshes frame
        """
        pass

    def _mousewheel(self, event=None):
        """
        Mousewheel movement receiver
        """
        pass

    def _leftMouseUp(self, event=None):
        """
        Left mouse button released receiver
        """
        pass

    def _resize(self, event=None):
        """
        Plane is resized receiver
        """
        self.Refresh()


# implement zooming / scaling
# implement highlighting
# getRect of plane

# todo: must have a color handler

# Interactive 2D-Base-Plane
class Dynamic2DGraphicalPlane(GraphicalPanel):
    ZOOMING_CONST = 0.15
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size)
        self.colorManager = PlaneColorHandler()

        self.mouseBefore = None
        self.origin = (0, 0)
        self.originUpdate = (0, 0)
        self.wb, self.db, self.w, self.h = None, None, None, None
        self.updatePlaneData()

        self.mouseCounter = 0

        self.Px2LEx = 50 / 1  # 20px on the x-axis correspond to 1LE
        self.Px2LEy = 50 / 1  # 20px on the y-axis correspond to 1LE

        self.zoomFactorX = 1
        self.zoomFactorY = 1

        self.hovered = None
        self.active = None

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # self.SetDoubleBuffered(True)

        # self.Bind(wx.EVT_LEFT_DOWN, self._leftMouseDown)

    # Update of all important class members
    def updatePlaneData(self, evt=None):
        self.w, self.h = self.GetSize()  # must be of parent (must be changed for more dynamic behaviour)
        self.origin = (self.origin[0] + self.originUpdate[0], self.origin[1] + self.originUpdate[1])
        self.originUpdate = (0, 0)
        oX, oY = self.origin
        self.db = (oX - 1 / 2 * self.w, oX + 1 / 2 * self.w)  # Definition-Classes
        self.wb = (oY - 1 / 2 * self.h, oY + 1 / 2 * self.h)

    def getLogicalWidth(self):
        return self.pxXToLogical(self.w)

    def getLogicalHeight(self):
        return self.pxYToLogical(self.h)

    def getLogicalOrigin(self):
        return self.pxXToLogical(self.origin[0]), self.pxXToLogical(self.origin[1])

    def getLogicalDB(self):
        return self.pxXToLogical(self.db[0]), self.pxXToLogical(self.db[1])

    def getLogicalWB(self):
        return self.pxXToLogical(self.wb[0]), self.pxXToLogical(self.wb[1])

    def logicalPointToPx(self, x, y):
        return self.logicalXToPx(x), self.logicalYToPx(y)

    def logicalXToPx(self, value):
        return value * self.Px2LEx * self.zoomFactorX

    def logicalYToPx(self, value):
        return value * self.Px2LEy * self.zoomFactorY

    def pxPointToLogical(self, x, y):
        return self.pxXToLogical(x), self.pxYToLogical(y)

    def pxXToLogical(self, value):
        return value / (self.Px2LEx * self.zoomFactorX)

    def pxYToLogical(self, value):
        return value / (self.Px2LEy * self.zoomFactorY)

    def _onPaint(self, evt=None):
        if 0 not in self.GetSize():

            self.updatePlaneData()

            dc = wx.BufferedPaintDC(self)
            dc.SetBackground(wx.Brush(self.backgroundColor))
            dc.Clear()

            self.colorManager.idBitmap = wx.Bitmap(*self.GetSize())
            mdc = wx.MemoryDC(self.colorManager.idBitmap)

            for object in self.layers:
                r = object.blitUpdateCopy(dc, mdc, self.colorManager.idOfObject(object), 6) #todo: add this constant
                # Performance testing
                if r is not None: #todo: remove this
                    print(f"{object.__class__.__name__}, drawtime: {r[1]:.5f}s")

                # runs at about 7ms for linear and 8-9ms for quadratic functions, at 1920x1080
                # draw time is mainly caused by bad graphical object optimization

    # Mousewheel event receiver (zooming)
    def _mousewheel(self, evt=None):
        #todo: should zoom towards mouse cursor
        if evt.GetWheelRotation() > 0:
            self.zoomFactorY += self.ZOOMING_CONST
            self.zoomFactorX += self.ZOOMING_CONST
        else:
            self.zoomFactorY -= self.ZOOMING_CONST
            self.zoomFactorX -= self.ZOOMING_CONST
        self.Refresh()
        evt.Skip()

    # def _leftMouseDown(self, evt=None):
    #     print("left down")

    # Resets mouseBefore-Status for dragging
    def _leftMouseUp(self, evt=None):
        self.mouseBefore = None
        if self.hovered is not None:
            self._setActiveObj(self.hovered)
        else:
            self._unsetActiveObj()

    def _setActiveObj(self, graphObject: GraphicalPanelObject):
        self.active = graphObject

    def _unsetActiveObj(self):
        self.active = None

    # Adjusts origin shift in proportion to mouse movement
    def _mouseMotion(self, event: wx.MouseEvent = None):  # todo: rename, since handles also left clicks

        relPos = event.GetPosition()
        if (hovered := self.objectBelowPos(relPos)) is not None:
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            self.hovered = hovered
        else:
            self.hovered = None

        # if propertyObjectAt(position of mouse):
        #   change mouse cursor
        #   event left down? -> select object as currently selected?

        self.mouseCounter += 1  # <- current fix to reduce drawCalls when mouseMotion is received
        if self.mouseCounter > 5:  # <- spurious fix / could be adjusted for stepwise scaling
            if event.Dragging() and event.leftIsDown:
                self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
                mX, mY = event.GetPosition()
                if self.mouseBefore is None:
                    self.mouseBefore = (mX, mY)
                self.originUpdate = self.mouseBefore[0] - mX, self.mouseBefore[1] - mY
                self.mouseBefore = (mX, mY)
                self.Refresh()
            else:
                self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

            self.mouseCounter = 0

    # Calculates relative position to (updated) origin
    def _adjustedOriginPointPos(self, x, y):
        return self._adjustOriginX(x), self._adjustOriginY(y)

    def _adjustOriginX(self, x):
        return x - self.origin[0]

    def _adjustOriginY(self, y):
        return y - self.origin[1]

    # Calculates position from upper left origin system to origin panel center system
    def _centerPosition(self, x, y):
        return self._centerX(x), self._centerY(y)

    def _centerX(self, x):
        return x + 1 / 2 * self.w

    def _centerY(self, y):
        return y + 1 / 2 * self.h

    # Calculates correct deviation
    def correctPosition(self, x, y):
        return self._centerPosition(*self._adjustedOriginPointPos(x, y))

    def correctY(self, y):
        return self._centerY(self._adjustOriginY(y))

    def correctX(self, x):
        return self._centerX(self._adjustOriginX(x))

    # change parent class to adjust for color restriction when adding objects
    def addGraphicalObject(self, graphicalObject, priorityIndex=None, setBasePlane=True):
        super().addGraphicalObject(graphicalObject, priorityIndex, setBasePlane)
        self.colorManager.addIdObject(graphicalObject)

    def objectBelowPos(self, relativePos):
        if (bmap := self.colorManager.idBitmap) is None:
            return
        dc = wx.MemoryDC(bmap)
        pixColor = dc.GetPixel(*relativePos)[:3]
        for object, objId in self.colorManager.objectColorsId():
            if pixColor == objId and object.getProperty("selectable").getValue():
                return object

    def highlight(self, graphObject: GraphicalPanelObject):
        pass  # todo: implement this


# todo: use alternative system with a second bitmap which uses id's for all objects
# creates id's based on colors -> id 1: (1, 0, 0), ... (allows for 256^3 (=16'777'216)combinations, more than enough)
# todo: implement and optimize
# Component of graphical Panel
class PlaneColorHandler:
    NONE_ID = (0, 0, 0)
    MAX_COL_VAL = 256

    def __init__(self):
        self._colorIds = dict()
        self._idCounter = 2 # Starts at 2, since 1 returns NONE_ID

        self.idBitmap = None

    # def updateIds(self):
    #     pass

    def idOfObject(self, graphObject: GraphicalPanelObject):
        return self._colorIds[graphObject]

    def addIdObject(self, graphObject: GraphicalPanelObject):
        newId = self.createColorId()
        self._colorIds[graphObject] = newId

    def removeIdObject(self, graphObject: GraphicalPanelObject):
        del self._colorIds[graphObject]

    # Method to create color-format-based id's
    # todo: Wenn Zeit vorhanden, neue Implementierung über dirkete arithmetische Operation (Logik bereits vorhanden)
    #       (-> Ähnlichkeit zur Umwandlungen vom römischen Zahlenformat)
    def createColorId(self):
        cId = list(self.NONE_ID)
        seed = self._idCounter
        while True:
            if seed > self.MAX_COL_VAL:
                seed -= self.MAX_COL_VAL
                for i, v in enumerate(cId[1:], 1):
                    if v < self.MAX_COL_VAL - 1:
                        cId[i] += 1
                        break
                    else:
                        if i < len(cId) - 1:
                            cId[i] = 0
                        else:
                            raise SeedException("The possible seed range of 16'777'215 has been exceeded")
            else:
                cId[0] = seed - 1
                break
        self._idCounter += 1
        return tuple(cId)

    def objectColors(self) -> Tuple[GraphicalPanelObject, Tuple[int, int, int, int]]:
        for o in self._colorIds:
            yield o, tuple(o.getProperty(vc.PROPERTY_COLOR).getValue())

    def objectColorsId(self):
        for o in self._colorIds:
            yield o, self._colorIds[o]

    def getColors(self) -> Tuple[int, int, int, int]:
        for o in self._colorIds:
            yield tuple(o.getProperty(vc.PROPERTY_COLOR).getValue())

    def colorExists(self, color: Tuple[int, int, int, int]):
        if color in self.getColors():
            return True
        return False

    def colorOfObjectExists(self, graphObject: GraphicalPanelObject):
        if self.colorExists(graphObject.getProperty(vc.PROPERTY_COLOR).getValue()):
            return True
        return False

class SeedException(Exception):
    def __init__(self, message="The maximum seed range has been exceeded"):
        super().__init__(message)