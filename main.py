import os

import wx

from MyWx.wx import *

from GraphCalc.Components.Graphical.Objects.graphUtilities import CartesianAxies
from GraphCalc.Components.Property.PropertyManager.propertyManager import PropertyManagerPostEvent
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Graphical.graphPlanes import EVT_OBJ_BELOW
from GraphCalc.Components.Property.property import PropertyObjCategory
from GraphCalc.Components.Property.PropertyManager.propertyManager import EVT_ACT_PROP_SET
from GraphCalc.Components.Property.PropertyManager.propertyOverview import EVT_PROP_PAN_REM_CALL


from GraphCalc.Calc.graphObjInterface import PropertyAddPanel
from GraphCalc.Calc.graphCalculator import GraphCalculator2D
from GraphCalc.Calc.graphObjInterface import PropertyObj2DInterface
from GraphCalc.Calc.Tools.graphSelector import PropertySelector
from GraphCalc.Calc.Tools.toolManager import ToolManager
from GraphCalc.Calc.Tools.Collection import intersection

from GraphCalc.Application.outputPrompt import OutputPrompt, BasicOutputTextPanel

from MyWx.Collection.templates import ThreePanelWorkspace

# General Todos: ==================================
# implement type hinting
# overhaul all classes and adjust for new superclass, like genericPanel and its global parent implementation
# add *args, **kwargs
# convert assert's into exceptions
# rework function system -> optimize
# allow prompt interaction
# add context menu
# graph plane threading?
# multi language support
# buttons in ui to change plane background (zooming, scaling, override interval approximation, etc.)
# optimize function drawing, by precalculating values -> use idle handler and intern optimization
# add more expression types
# get coordinates of plane when right clicking => saving to clipboard
# values are not properly updated -> when variable is created, which is used in an other expression there is no update call
# adding a small prompt
# Kurvenscharen, Flächen, Funktionsintervalle
# add object deletion
# add multi selection
# add object tools
# update value constants
# refactor code
# rework code
# position axle scaling based on width of text, to prevent overlapping
# implement better rounding functionalities
# add saving
# structure ApplicationFrame more rigorously
# split classes into more files -> use more structural hierarchy
# proof if mathematical rigorously
# multiselect
# custom events in own classes => observer design pattern could be used more often
# add approximation solver
# disable simplify in solve if performance becomes an issue
# test tools, etc.
# unify names
# structure more strictly into front- and backend
# add arbitrary graphical object during runtime in application (e.g. cartesian coordinate system)
# start work on property controlers
# delete graph objects when they are right clicked (context menu)
# use prompt for tool input (e.g. limited integrals)
# right click to remove
# variable cannot be value at function
# linearFirstValue -> linearLastValue
#todo: -tool add coordinate system, -when dupe, object is getting deleted unintendedly, -more tools, -toolbar, -menubar, -put overview into static box, -dont rebuild categories, just change color
#==================================================


class GraphCalculatorApplicationFrame(wx.Frame):
    version = "0.9.2"
    title = "Ivo's Grafikrechner"
    sourcePath = os.path.join(
        "GraphCalc",
        "source"
    )
    imgSrcPath = os.path.join(sourcePath, "img")
    iconSize = (32, 32)

    def __init__(self, parent=None, id=wx.ID_ANY, title=""):
        super().__init__(parent, id, title)
        self.SetTitle(f"{GraphCalculatorApplicationFrame.title} (Version: {GraphCalculatorApplicationFrame.version})")
        self.SetSize((1280, 720))
        self.buildApp()
        # self.Maximize(True)
        self.Show(True)

    def buildApp(self):
        self._buildBars()
        self._buildUI()
        self._bindHandlers()

        self.output.getPanel().setLines([
            "Application has been instantiated!",
            f"Welcome to {self.title} - v{self.version}",
            None  #<- works like a line break
        ])

    def _buildUI(self):
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.workspace = ThreePanelWorkspace(self)

        self.leftWorkspacePanel = GenericPanel(self.workspace.splitter)
        self.leftWorkspacePanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.rightWorkspacePanel = GenericPanel(self.workspace.splitter)
        self.rightWorkspacePanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.output = OutputPrompt(
            BasicOutputTextPanel(self.rightWorkspacePanel)
        )

        self.graphPropertyManager = Dy2DGraphPropertyManager(
            self.workspace.splitter  # <- move parent into getter method
        )
        self.graphPropertyManager.setPropertyManager(PropertyManagerPostEvent(self))
        self.graphCalculator = GraphCalculator2D()

        self.graphCalcObjInterface = PropertyObj2DInterface(
            graphCalculator=self.graphCalculator,
            graphPropertyManager=self.graphPropertyManager,
            updateFunction=self.Refresh
        )

        self.toolManager = ToolManager(PropertySelector(), self.output)
        #self.Bind(EVT_ACT_PROP_CH, self.toolManager.selectorUpdHandler())
        self.Bind(EVT_ACT_PROP_SET, self.toolManager.selectorUpdHandler())

        #=Setup tools=

        self.intersectionTool = self.toolManager.callable(
            intersection.IntersectionTool(self.graphPropertyManager)
        )

        #=============



        self.graphPanel = self.graphPropertyManager.getGraphPlane()
        self.graphPanel.mirrorY(True)
        # self.graphPropertyManager.propertyManager.createOverviewInspectionPanels(self.workspace.splitter)
        self.graphPropertyManager.propertyManager.createOverviewPanel(self.leftWorkspacePanel)
        self.graphPropertyManager.propertyManager.createInspectionPanel(self.rightWorkspacePanel)
        self.overviewPanel, self.inspectionPanel = self.graphPropertyManager.propertyManager.getOverviewInspectionPanels()

        self.overviewPanel.createCategory(PropertyObjCategory.FUNCTION.getName())
        self.overviewPanel.createCategory(PropertyObjCategory.VARIABLE.getName())
        self.overviewPanel.createCategory(PropertyObjCategory.POINT.getName())
        self.overviewPanel.createCategory(PropertyObjCategory.VECTOR.getName())
        self.overviewPanel.createCategory(PropertyObjCategory.SHAPE.getName())
        self.overviewPanel.createCategory(PropertyObjCategory.NO_CATEGORY.getName())
        # self.overviewPanel.createCategory(PropertyObjCategory.CUSTOM_CATEGORY("Test").getName())

        # Overview-panel and Inspection-panel have been created

        # TESTING---------------
        for i in range(1, 2):
            axis = CartesianAxies()
            p = axis.getProperty("name")
            p._setValue("Cartesian-Plane - " + str(i))
            axis.addProperty(p, override=True)
            self.graphPropertyManager.addPropertyObject(axis, setAsActive=False)

        self.addPropertyPanel = PropertyAddPanel(
            parent=self.leftWorkspacePanel,
            graphObjectInterface=self.graphCalcObjInterface
            # todo: parent should come first | needs to be connected to the interface
        )  # <- define as special control / also other controls that effect manager
        self.addPropertyPanel.setOutput(self.output)

        self.leftWorkspacePanelSizer.Add(self.addPropertyPanel, 0, wx.EXPAND | wx.TOP, 5)
        self.leftWorkspacePanelSizer.Add(self.overviewPanel, 3, wx.EXPAND | wx.TOP, 5)
        self.leftWorkspacePanel.SetSizer(self.leftWorkspacePanelSizer)

        self.rightWorkspacePanelSizer.Add(self.inspectionPanel, 4, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.rightWorkspacePanelSizer.Add(self.output.getPanel(), 1, wx.EXPAND | wx.ALL, 5)
        self.rightWorkspacePanel.SetSizer(self.rightWorkspacePanelSizer)

        self.leftWorkspacePanel.SetBackgroundColour((255, 255, 255))
        self.rightWorkspacePanel.SetBackgroundColour((100, 100, 100))
        # todo: right panel must have a minimum size, else contents can go out of view in the scroll panel
        self.workspace.setWindows(self.leftWorkspacePanel, self.graphPanel, self.rightWorkspacePanel)
        self.workspace.build()
        # self.workspace.splitter.SetMinimumPaneSize(100)

        self.mainSizer.Add(self.toolbar, 0, wx.EXPAND)
        self.mainSizer.Add(self.workspace.getSizer(), 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)

    def _bindHandlers(self):
        self.graphPanel.Bind(wx.EVT_MOTION, self._updateStatusBarPos)
        self.graphPanel.Bind(wx.EVT_PAINT, self._updateStatusBarDrawTime)
        self.Bind(EVT_OBJ_BELOW, self._updateStatusBarBelowCursor)

        self.Bind(wx.EVT_MENU, self._toggleStatusBar, self._showStatusBarItem)
        self.Bind(wx.EVT_MENU, self._toggleToolBar, self._showToolBarItem)
        self.Bind(wx.EVT_MENU, self._clearPrompt, self._clearPromptItem)

        self.Bind(wx.EVT_TOOL, self.intersectionTool, self._toolbarIntersectionButton)
        self.Bind(wx.EVT_MENU, self.intersectionTool, self._menuIntersectionButton)

        self.Bind(EVT_PROP_PAN_REM_CALL, self._removePropertyObject)

        self.Bind(wx.EVT_CLOSE, self._onFrameClose)
        self.graphPanel.Bind(wx.EVT_RIGHT_DOWN, self._onRightDownGraph)

    def _removePropertyObject(self, evt=None):
        self.graphPropertyManager.removeUndefinePropertyObject((o :=evt.propertyObject))
        self.graphPanel.Refresh()
        self.output.send(f"removed '{type(o).strRep()}':  {o.getProperty('name').getValue()}")

    def _buildBars(self):
        self._buildMenuBar()
        self._buildToolBar()
        self._buildStatusBar()

    def _buildMenuBar(self):
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(
            wx.ID_ANY,
            "&Hello...\tCtrl-H",
            "Help string shown in status bar for this menu item"
        )
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        toolMenu = wx.Menu()
        self._menuIntersectionButton = toolMenu.Append(
            wx.ID_ANY,
            "function intersections",
            "Calculates the intersections of 2 functions"
        )

        miscMenu = wx.Menu()
        self._showStatusBarItem = miscMenu.Append(
            wx.ID_ANY,
            "Show statusbar",
            "Shows the Statusbar",
            kind=wx.ITEM_CHECK
        )
        self._showToolBarItem = miscMenu.Append(
            wx.ID_ANY,
            "Show toolbar",
            "Shows the Toolbar",
            kind=wx.ITEM_CHECK
        )
        self._clearPromptItem = miscMenu.Append(
            wx.ID_ANY,
            "Clear prompt",
            "Clears the Prompt"
        )
        miscMenu.Check(self._showStatusBarItem.GetId(), True)
        miscMenu.Check(self._showToolBarItem.GetId(), True)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)



        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(toolMenu, "&Tools")
        menuBar.Append(miscMenu, "&Miscellaneous")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self._onHello, helloItem)
        self.Bind(wx.EVT_MENU, self._onExit, exitItem)
        self.Bind(wx.EVT_MENU, self._onAbout, aboutItem)

    def _buildStatusBar(self):
        """
        Create a Statusbar
        """
        self.CreateStatusBar()
        self.GetStatusBar().SetFieldsCount(3)

    def _buildToolBar(self):
        self.toolbar = wx.ToolBar(self)
        self.toolbar.SetToolBitmapSize(self.iconSize)

        self._toolbarIntersectionButton = self.toolbar.AddTool(
            wx.ID_ANY,
            "intersection",
            wx.Bitmap(os.path.join(self.imgSrcPath, "test.png")),
            "calculate the intersections of 2 Functions",
        )
        self.toolbar.AddSeparator()
        # self.toolbar.AddTool(
        #     wx.ID_ANY,
        #     ""
        # )

        self.toolbar.Realize()

    def _updateStatusBarDrawTime(self, evt=None):
        bar: wx.StatusBar = self.GetStatusBar()
        bar.SetStatusText(f"Last drawtime: {round(self.graphPanel.lastDrawTime * 1000, 3)}ms", 0)
        evt.Skip()

    def _updateStatusBarPos(self, evt: wx.MouseEvent=None):
        if evt.Dragging():
            evt.Skip()
            return
        bar: wx.StatusBar = self.GetStatusBar()
        panel = self.graphPanel

        x, y = panel.pxPointToLogical(*panel.absPosToOrigin(*evt.GetPosition()))
        #todo: implement better rounding or scientific notation
        #      -determine by zooming factor
        bar.SetStatusText(
            f"x = {x} | y = {y}", # f"x = {convertToScientificStr(x)} | y = {convertToScientificStr(y)}"
            1
        )
        evt.Skip()

    def _updateStatusBarBelowCursor(self, evt=None):
        bar: wx.StatusBar = self.GetStatusBar()
        hovered = evt.below
        if hovered is not None:
            bar.SetStatusText(f"Hovering: '{hovered.getProperty('name').getValue()}'", 2)
        else:
            bar.SetStatusText("Hovering: ", 2)

        evt.Skip()

    def _toggleStatusBar(self, evt=None):
        if self._showStatusBarItem.IsChecked():
            self.GetStatusBar().Show()
        else:
            self.GetStatusBar().Hide()
        self.Layout()

    def _toggleToolBar(self, evt=None):
        if self._showToolBarItem.IsChecked():
            self.toolbar.Show()
        else:
            self.toolbar.Hide()
        self.Layout()

    def _clearPrompt(self, evt=None):
        self.output.getPanel().clear()

    def _onExit(self, evt=None):
        """Close the frame, terminating the application."""
        self.Close(True)

    def _onHello(self, evt=None):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")

    def _onAbout(self, evt=None):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)

    def _onRightDownGraph(self, evt: wx.MouseEvent=None):  # todo: doesnt work yet correctly
        self.graphPanel.PopupMenu(ContextMenuGraph(self), evt.GetPosition())
        evt.Skip()

    def _onFrameClose(self, evt: wx.CloseEvent = None):
        if False:
            # if evt.CanVeto():
            if wx.MessageBox("The latest changes have not been saved yet, do you want to save before closing ?",
                             "Please confirm", wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                pass
        self.Destroy()


#todo: out-source
class ContextMenuGraph(wx.Menu):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent

        mmi = wx.MenuItem(self, wx.ID_ANY, 'Minimize')
        self.Append(mmi)
        self.Bind(wx.EVT_MENU, self._onMinimize, mmi)

        cmi = wx.MenuItem(self, wx.ID_ANY, 'Close')
        self.Append(cmi)
        self.Bind(wx.EVT_MENU, self._onClose, cmi)

    def _onMinimize(self, evt=None):
        self._parent.Iconize()

    def _onClose(self, evt=None):
        self._parent._onFrameClose()
        # self._parent.Close()


if __name__ == "__main__":
    app = wx.App(False)
    frame = GraphCalculatorApplicationFrame()
    app.MainLoop()
