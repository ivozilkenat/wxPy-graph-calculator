from GraphCalc.Components.Graphical.graphPlanes import GraphicalPanel


# Manages Graphical-Layers, with any GraphPlane as Base-Layer
class DynamicPlaneLayerManager:
    def __init__(self, basePlane):
        self.basePlane = basePlane
        assert isinstance(self.basePlane, GraphicalPanel)

        self.layers = list()  # Exchange with priority queue
        # ideal Design?
        # Assigns important event-receiver-bindings
        self.basePlane.Bind(wx.EVT_SIZE, self.basePlane.resize)
        self.basePlane.Bind(wx.EVT_PAINT, self.basePlane.onPaint)  # Difference EVT_Paint, etc.
        self.basePlane.Bind(wx.EVT_MOTION, self.basePlane.mouseMotion)
        self.basePlane.Bind(wx.EVT_LEFT_UP, self.basePlane.leftMouseUp)
        self.basePlane.Bind(wx.EVT_MOUSEWHEEL, self.basePlane.mousewheel)

    # returns current layers and order
    def layerOrder(self):
        return [(0, self.basePlane)] + [(c + 1, o) for c, o in enumerate(self.layers)]

    # adds gpo at desired position in layer-stack
    def addGraphicalObject(self, graphicalObject, priorityIndex=None):
        graphicalObject.basePlane = self.basePlane
        if priorityIndex is None:
            self.layers.append(graphicalObject)
        else:
            self.layers.insert(priorityIndex, graphicalObject)

# !!!
# !!! Redundant class -> maybe useful later on with more advanced group/layer managing
# !!! 					or for input output management of propertyObjects
# !!!
