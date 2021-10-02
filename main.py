from MyWx.wx import *
from MyWx.Collection.panels import RandomPanel

from GraphCalc.Components.Graphical.Objects.graphFunctions import GraphFunction2D
from GraphCalc.Components.Graphical.Objects.graphUtilities import CartesianAxies
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager
from GraphCalc.Components.Property.property import PropertyObjCategory

from GraphCalc.Calc.GraphObjInterface import PropertyAddPanel
from GraphCalc.Calc.GraphCalculator import GraphCalculator2D, Function2DExpr
from GraphCalc.Calc.GraphObjInterface import PropertyObj2DInterface

from GraphCalc.Application.outputPrompt import OutputPrompt, BasicOutputTextPanel

from MyWx.Collection.templates import ThreePanelWorkspace

# everything is displayed upside down -> mirror on x-axis
# implement type hinting
# overhaul all classes and adjust for new superclass, like genericPanel and its global parent implementation
# add *args, **kwargs
# convert assert's into exceptions
# rework function system -> optimize
# allow prompt interaction
# add graph information below
# add context menu
# graph plane threading?
# multi language support
# buttons in ui to change plane background (zooming, scaling, override interval approximation, etc.)
# optimize function drawing, by precalculating values -> use idle handler and intern optimization
# when selected object is deleted, change focus
# add more expression types
# get coordinates of plane when right clicking => saving to clipboard
# creating an object twice causes errors
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

class GraphCalculatorApplicationFrame(wx.Frame):
    version = "0.8.0"
    title = "Ivo's Grafikrechner"

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
            "Welcome to Ivo's GraphCalculator",
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
        self.graphCalculator = GraphCalculator2D()

        self.graphCalcObjInterface = PropertyObj2DInterface(
            graphCalculator=self.graphCalculator,
            graphPropertyManager=self.graphPropertyManager,
            updateFunction=self.Refresh
        )

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

        graphToolPlaceholder = RandomPanel(self.rightWorkspacePanel, (0, 120))
        inputPromptPlaceholder = RandomPanel(self.rightWorkspacePanel, (0, 120))

        self.rightWorkspacePanelSizer.Add(self.inspectionPanel, 4, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        #self.rightWorkspacePanelSizer.Add(graphToolPlaceholder, 12, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.rightWorkspacePanelSizer.Add(self.output.getPanel(), 1, wx.EXPAND | wx.ALL, 5)
        self.rightWorkspacePanel.SetSizer(self.rightWorkspacePanelSizer)

        self.leftWorkspacePanel.SetBackgroundColour((255, 255, 255))
        self.rightWorkspacePanel.SetBackgroundColour((100, 100, 100))
        # todo: right panel must have a minimum size, else contents can go out of view in the scroll panel
        self.workspace.setWindows(self.leftWorkspacePanel, self.graphPanel, self.rightWorkspacePanel)
        self.workspace.build()
        # self.workspace.splitter.SetMinimumPaneSize(100)

        toolbarPlaceholder = RandomPanel(self, size=(0, 50))  # todo: implement

        self.mainSizer.Add(toolbarPlaceholder, 0, wx.EXPAND)
        self.mainSizer.Add(self.workspace.getSizer(), 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)

    def _bindHandlers(self):
        self.Bind(wx.EVT_CLOSE, self._onFrameClose)
        self.graphPanel.Bind(wx.EVT_RIGHT_DOWN, self._onRightDownGraph)

    def _buildBars(self):
        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                                    "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self._onHello, helloItem)
        self.Bind(wx.EVT_MENU, self._onExit, exitItem)
        self.Bind(wx.EVT_MENU, self._onAbout, aboutItem)
        """
		Create a Statusbar
		"""
        self.CreateStatusBar()
        self.SetStatusText("Wer das ließt kann lesen")

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

    def _onRightDownGraph(self, evt=None):  # todo: doesnt work yet correctly
        self.PopupMenu(ContextMenu(self), evt.GetPosition())
        evt.Skip()

    def _onFrameClose(self, evt: wx.CloseEvent = None):
        if False:
            # if evt.CanVeto():
            if wx.MessageBox("The latest changes have not been saved yet, do you want to save before closing ?",
                             "Please confirm", wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                pass
        self.Destroy()


class ContextMenu(wx.Menu):
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
