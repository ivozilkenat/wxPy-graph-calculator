from MyWx.wx import *


# positions as tuples or individual arguments?
# add more assertions or further type checking
# add interactive selection of displayed objects

# Baseclass for Base-Panels
# -> Foundation of every layer-system
class GraphicalPanel(GenericPanel):
    def __init__(self, parent=None, size=None):
        super().__init__(parent, size)
        # self.bitmap = None
        # self.memoryDc = None

        self.Bind(wx.EVT_SIZE, self.resize)
        self.Bind(wx.EVT_PAINT, self.onPaint)  # Difference EVT_Paint, etc.
        self.Bind(wx.EVT_MOTION, self.mouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.leftMouseUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.leftMouseUp)
        self.Bind(wx.EVT_MOUSEWHEEL, self.mousewheel)

        self.layers = list()  # Exchange with priority queue

        self.SetDoubleBuffered(True)

        self.backgroundColor = (255, 255, 255)

    # self.addProperty(Property("background_color", (255, 255, 255))) # <- metaclass conflict (must be resolved) if derived from Property

    # returns current layers and order
    def getLayerOrder(self):
        return [(0, self)] + [(c + 1, o) for c, o in enumerate(self.layers)]

    # adds gpo at desired position in layer-stack
    def addGraphicalObject(self, graphicalObject, priorityIndex=None):
        graphicalObject.basePlane = self
        if priorityIndex is None:
            self.layers.append(graphicalObject)
        else:
            self.layers.insert(priorityIndex, graphicalObject)

    def onPaint(self, event=None):
        """
        OnPaint-Event-Receiver
        """

        self.updatePlaneData()
        # self.bitmap = wx.Bitmap(*self.GetSize())
        # self.memoryDc = wx.MemoryDC(self.bitmap)
        # self.memoryDc.SetBackground(wx.Brush((255, 255, 255)))
        # self.memoryDc.Clear() # <- why is this necessary
        dc = wx.BufferedPaintDC(self, wx.Bitmap(*self.GetSize()))
        dc.SetBackground(wx.Brush(self.backgroundColor))
        dc.Clear()

        for object in self.layers:
            object.blitUpdate(dc)

    # self.bitmap.ConvertToImage().SaveFile("test.png", wx.BITMAP_TYPE_PNG)
    # dc = wx.BufferedPaintDC(self, self.bitmap)
    # dc.DrawBitmap(self.bitmap, 0, 0)

    # Predefined Event-Receivers (design must be approved of)
    def updatePlaneData(self, event=None):
        """
        Updates values of plane
        """
        pass

    def mouseMotion(self, event=None):
        """
        Mouse motion receiver
        Updates position of origin and refreshes frame
        """
        pass

    def mousewheel(self, event=None):
        """
        Mousewheel movement receiver
        """
        pass

    def leftMouseUp(self, event=None):
        """
        Left mouse button released receiver
        """
        pass

    def resize(self, event=None):
        """
        Plane is resized receiver
        """
        self.Refresh()


# implement zooming / scaling

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

    # Update of all important class members
    def updatePlaneData(self, event=None):
        self.w, self.h = self.GetSize()  # must be of parent (must be changed for more dynamic behaviour)
        self.origin = (self.origin[0] + self.originUpdate[0], self.origin[1] + self.originUpdate[1])
        self.originUpdate = (0, 0)
        oX, oY = self.origin
        self.db = (oX - 1 / 2 * self.w, oX + 1 / 2 * self.w)  # Definition-Classes
        self.wb = (oY - 1 / 2 * self.h, oY + 1 / 2 * self.h)

    # OnPaint event receiver
    # def onPaint(self, event = None):
    # 	# Add logic to eliminate redundant blit-calls
    # 	# Bitmap logic must be implemented to prevent flickering and lower drawing costs
    # 	self.updatePlaneData()
    # 	dc = wx.PaintDC(self)
    # 	for object in self.layers:
    # 		object.blitUpdate(dc)

    # Mousewheel event receiver (zooming)
    def mousewheel(self, event=None):
        pass

    # Resets mouseBefore-Status for dragging
    def leftMouseUp(self, event=None):
        self.mouseBefore = None

    # Adjusts origin shift in proportion to mouse movement
    def mouseMotion(self, event=None):
        self.mouseCounter += 1  # <- current fix to reduce drawCalls when mouseMotion is received
        if self.mouseCounter > 5:  # <- spurious fix / could be adjusted for stepwise scaling

            if event.Dragging():
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
