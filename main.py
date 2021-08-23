from MyWx.wx import *
from MyWx.Collection.panels import RandomPanel

# from GraphCalc.Components.Graphical.GraphFunctions import Function2D
from GraphCalc.Components.Graphical.graphPlanes import Dynamic2DGraphicalPlane
from GraphCalc.Components.Graphical.graphUtilities import CartesianAxies
from GraphCalc.Components.Graphical.graphManagers import Dy2DGraphPropertyManager

from MyWx.Collection.templates import ThreePanelWorkspace


# add string file
# everything is displayed upside down -> mirror on x-axis
# implement type hinting
# overhaul all classes and adjust for new superclass, like genericPanel and its global parent implementation

class GraphCalculatorApplicationFrame(wx.Frame):
    version = "0.1.0"
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

    def _buildUI(self):
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.workspace = ThreePanelWorkspace(self)

        self.graphPropertyManager = Dy2DGraphPropertyManager(self)
        self.overviewPanel, self.inspectionPanel = self.graphPropertyManager.getPropertyManager().createOverviewInspectionPanels(self)

        axis = CartesianAxies()
        self.graphPropertyManager.addPropertyObject(axis)

        self.workspace.setContent(self.overviewPanel, self.graphPropertyManager.getGraphPlane(), self.inspectionPanel)
        self.workspace.build()
        #self.workspace.splitter.SetMinimumPaneSize(100)

        # from GraphCalc.Components.Graphical.graphUtilities import CartesianAxes
        # self.workspace._graphicalPlane.addGraphicalObject(CartesianAxes())

        self.mainSizer.Add(self.workspace.getSizer(), 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)

    def _bindHandlers(self):
        self.Bind(wx.EVT_CLOSE, self._onFrameClose)

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

    def _onExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def _onHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")

    def _onAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)

    def _onFrameClose(self, evt: wx.CloseEvent = None):
        if False:
            # if evt.CanVeto():
            if wx.MessageBox("The latest changes have not been saved yet, do you want to save before closing ?",
                             "Please confirm", wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                pass
        self.Destroy()


if __name__ == "__main__":
    app = wx.App(False)
    frame = GraphCalculatorApplicationFrame()
    app.MainLoop()
