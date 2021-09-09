import wx

from MyWx.wx import *

from typing import Union

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

        #self.SetDoubleBuffered(True)

        self.backgroundColor = (255, 255, 255)

    # self.addProperty(Property("background_color", (255, 255, 255))) # <- metaclass conflict (must be resolved) if derived from Property

    # returns current layers and order
    def getLayerOrder(self):
        return [(0, self)] + [(c + 1, o) for c, o in enumerate(self.layers)]

    #TODO: Change layer into a propertyObject to manage object order

    # adds gpo at desired position in layer-stack
    def addGraphicalObject(self, graphicalObject, priorityIndex=None):
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

# 2D-Base-Plane
class Dynamic2DGraphicalPlane(GraphicalPanel):
    def __init__(self, parent, size=None):
        super().__init__(parent=parent, size=size)
        self.mouseBefore = None
        self.origin = (0, 0)
        self.originUpdate = (0, 0)
        self.wb, self.db, self.w, self.h = None, None, None, None
        self.updatePlaneData()

        self.mouseCounter = 0

        self.Px2LEx = 20 / 1  # 20px on the x-axis correspond to 1LE
        self.Px2LEy = 20 / 1  # 20px on the y-axis correspond to 1LE

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        #self.SetDoubleBuffered(True)

        #self.Bind(wx.EVT_LEFT_DOWN, self._leftMouseDown)

    # Update of all important class members
    def updatePlaneData(self, evt=None):
        self.w, self.h = self.GetSize()  # must be of parent (must be changed for more dynamic behaviour)
        self.origin = (self.origin[0] + self.originUpdate[0], self.origin[1] + self.originUpdate[1])
        self.originUpdate = (0, 0)
        oX, oY = self.origin
        self.db = (oX - 1 / 2 * self.w, oX + 1 / 2 * self.w)  # Definition-Classes
        self.wb = (oY - 1 / 2 * self.h, oY + 1 / 2 * self.h)

    def _onPaint(self, evt=None):
        if 0 not in self.GetSize():

            self.updatePlaneData()

            dc = wx.BufferedPaintDC(self)
            dc.SetBackground(wx.Brush(self.backgroundColor))
            dc.Clear()


            for object in self.layers:
                r = object.blitUpdate(dc)
                # Performance testing
                if r is not None: #todo: remove this
                    print(f"{object.__class__.__name__}, drawtime: {r[1]:.5f}s")

                    # runs at about 7ms for linear and 8-9ms for quadratic functions, at 1920x1080
                    # draw time is mainly caused by bad graphical object optimization


    # Mousewheel event receiver (zooming)
    def _mousewheel(self, evt=None):
        pass

    # def _leftMouseDown(self, evt=None):
    #     print("left down")

    # Resets mouseBefore-Status for dragging
    def _leftMouseUp(self, evt=None):
        self.mouseBefore = None

    # Adjusts origin shift in proportion to mouse movement
    def _mouseMotion(self, event: wx.MouseEvent=None): #todo: rename, since handles also left clicks

        relPos = event.GetPosition()
        self.objectBelowMouse(relPos)

        #if propertyObjectAt(position of mouse):
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
        return x - self.origin[0], y - self.origin[1]

    # Calculates position from upper left origin system to origin panel center system
    def _centerPosition(self, x, y):
        return x + 1 / 2 * self.w, y + 1 / 2 * self.h

    # Calculates correct deviation
    def correctPosition(self, x, y):
        return self._centerPosition(*self._adjustedOriginPointPos(x, y))


    def objectBelowMouse(self, relativePos):
        dc = wx.ClientDC(self)
        color = dc.GetPixel(*relativePos)
        for object, color in self.objectColors():
            print(object, color)


    def objectColors(self):
        for o in self.layers:
            print(o)
            yield o, o.getProperty("color").getValue()

