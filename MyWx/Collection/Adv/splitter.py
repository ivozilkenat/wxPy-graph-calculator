import wx
from wx.lib.splitter import MultiSplitterWindow, MultiSplitterEvent


# TODO: proof if auiManager might be a better solution
#		-Structure class, add documentation, test it fully, rework naming
#		-type hinting and parameter descriptions
#		-*args, **kwargs support ?
# Extends the MultiSplitter-Class by adding convenience methods
# or further functionalities like SashGravity or absolute positioning
# and the negative position of sashes

# -adjust _AdjustSashPosition to work with max size
# -sizing information should be saved in the proportion object
# -allow splitting/unsplitting
# (-resize while splitting) <- can be worked later on, since might be very complex, since sash drawing must be disabled
# -allow for min and max size to work properly (set, get, implement checks)
class DynamicMultiSplitter(MultiSplitterWindow):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        assert not parent is None
        self._proportions = None  # <- proportions must be set
        self.__propInit = False
        self._movable = False  # <- should be renamed, smth. like adjustNeighbours
        self._resizeWhileDragging = False  # <- what does this do
        self._parent = parent

        self.__minPaneSizeLowerBound = 10 #<- if 0, paneSize can be zero and since panes do not unsplit an error will occur
        self._minimumPaneSize = self.__minPaneSizeLowerBound #<- could be removed if unsplitting is possible
        #TODO: what if size of pane is set to 0 and not -1

    # Resizes all windows properly, according to their proportion
    def _onSize(self, event=None):
        self._setSashesProportional()

        self.__refreshAllWindows() #mandatory for multiple windows, else bugs might appear
        event.Skip()

    def _setSashesProportional(self):
        # should work with both orientations (not tested yet)
        totalSpace = self.GetTotalSpaceWithoutSashes()
        for p in self._proportions:
            ratio = p[0]
            if ratio == 0:
                totalSpace -= p[1].GetSize()
        for i, p in enumerate(self._proportions[:-1]):
            ratio = p[0]
            if ratio != 0:
                newWidth = totalSpace * (ratio / self._proportions.sum)
                if newWidth < self._minimumPaneSize: #TODO: maybe rework this fix, to fully rescale everything
                    newWidth = self._minimumPaneSize
                self.SetSashRePosition(i, newWidth)

    # A valid solution for problems which occur when dealing with more windows?? If windows are not refreshed
    # their construction becomes invalid -> leads to overlapping in drawing (could be fixed with auimanager?)
    def __refreshAllWindows(self):
        for p in self._windows:
            p.Refresh()

    # Updates the sizes in the proportion object if a splitter is changed to prevent wrong resizing
    # e.g.: if the proportion factor is 0, the window should not be changed in any way when resizing the app,
    #		but if the splitter changes the new size must be set as the base size
    # Also catches event of parent class and corrects arguments (self._movable)
    def _DoSetSashPosition(self, idx, newPos1, newPos2=-1, adjustNeighbor=False):
        self.__refreshAllWindows()  # <- prevents flickering because of incorrect rendering
        if not self._movable:
            super()._DoSetSashPosition(idx, newPos1, newPos2, adjustNeighbor=True)
        else:
            super()._DoSetSashPosition(idx, newPos1, newPos2, adjustNeighbor)

        self._SizeWindows()
        self._proportions.UpdateSize(self.GetPanelSizes())

    def _AdjustSashPosition(self, idx, newPos1, newPos2=-1, adjustNeighbor=False):
        adjustNeighbor = not self._movable  # <- decouples adjustNeighbour from any shift-event

        total = newPos1 + newPos2
        # these are the windows on either side of the sash
        win1 = self._windows[idx]
        win2 = self._windows[idx + 1]

        # make adjustments for window min sizes #TODO <- Extra logic must be implemented here
        # TODO: fix minSize = 0
        minSize = self._GetWindowMin(win1)
        if minSize == -1 or self._minimumPaneSize > minSize:
            minSize = self._minimumPaneSize
        minSize += self._GetBorderSize()
        if newPos1 < minSize:
            newPos1 = minSize
            newPos2 = total - newPos1

        if adjustNeighbor:
            minSize = self._GetWindowMin(win2)
            if minSize == -1 or self._minimumPaneSize > minSize:
                minSize = self._minimumPaneSize
            minSize += self._GetBorderSize()
            if newPos2 < minSize:
                newPos2 = minSize
                newPos1 = total - newPos2

        return (newPos1, newPos2)

    def _OnSashPositionChanging(self, idx, newPos1, newPos2, adjustNeighbor):
        # TODO: check for possibility of unsplit (pane size becomes zero)

        # make sure that minsizes are honored
        newPos1, newPos2 = self._AdjustSashPosition(idx, newPos1, newPos2, adjustNeighbor)

        # sanity check
        if newPos1 <= 0:
            newPos2 += newPos1
            newPos1 = 0

        # send the events
        evt = MultiSplitterEvent(
            wx.wxEVT_COMMAND_SPLITTER_SASH_POS_CHANGING, self)
        evt.SetSashIdx(idx)
        evt.SetSashPosition(newPos1)
        if not self._DoSendEvent(evt):
            # the event handler vetoed the change
            newPos1 = -1
        else:
            # or it might have changed the value
            newPos1 = evt.GetSashPosition()

        if adjustNeighbor and newPos1 != -1:
            evt.SetSashIdx(idx + 1)
            evt.SetSashPosition(newPos2)
            if not self._DoSendEvent(evt):
                # the event handler vetoed the change
                newPos2 = -1
            else:
                # or it might have changed the value
                newPos2 = evt.GetSashPosition()
            if newPos2 == -1:
                newPos1 = -1

        return (newPos1, newPos2)

    # Extends the AppendWindow-method to automatically adjust the proportions if a new window is added or set
    # the proportions if the window is the first to be added, thereby a Proportions-object is created
    # Note: the proportion argument is standardized to be 1, which would mean equal scaling if proportions aren't set manually
    def AppendWindow(self, window, sashPos=-1, proportion=1):
        super().AppendWindow(window, sashPos)
        if self._proportions is None:
            self.SetProportions([proportion])
        else:
            self._proportions.Add([proportion],
                                  [window.GetSize() if proportion < 1 else self.Proportions.SplitterSize.NoFixedSize])

    # If given a tuple of proportion-factors (must be len of existing windows) proportions are set and if a factor
    # pn = 0, the according size to preserve is selected automatically
    def SetProportions(self, proportions):
        # print(proportions, len(self._windows))
        assert all([i >= 0 for i in proportions]) and len(proportions) == len(self._windows)
        self._proportions = self.Proportions(self._orient, proportions, [
            w.GetSize() if proportions[i] < 1 else self.Proportions.SplitterSize.NoFixedSize for i, w in
            enumerate(self._windows)])
        if not self.__propInit:
            wx.CallAfter(self.__initSashGravity)
            self.__propInit = True

    # After the application is initialized events for dynamic resizing are binded here and proportions are set correctly,
    # which means sizes are obtained correctly
    def __initSashGravity(self):
        self.Bind(wx.EVT_SIZE,
                  self._onSize)  # <- how does CallAfter work exactly / maybe unecessary if self.SizeWindows may solve this
        self.SetProportions(self._proportions.proportions)

    # Returns the Proportion-Object
    def GetProportions(self):
        return self._proportions

    # Returns the amount of splitted windows
    def GetWindowAmount(self):
        return len(self._windows)  # <- should the method be used internally?

    # Returns the amount of Sashes
    def GetSashAmount(self):
        return len(self._windows) - 1  # <- should the method be used internally?

    # Allows to set the absolute position (relative to the splitter itself) of the idx't sash
    def SetSashAbsPosition(self, idx, pos):
        if pos < 0:
            pos += self.GetTotalSpace()  # Doesn't work exact (=not pixel perfect), since sash pos does not account for sash width which could lead to unexpected results
        if idx != 0:
            self.SetSashRePosition(idx, pos - self.GetSashAbsPosition(idx - 1))
        else:
            self.SetSashRePosition(idx, pos)

    # Returns the absolute position (relative to the splitter itself) of the idx't sash
    def GetSashAbsPosition(self, idx):
        return sum([self.GetSashPosition(i) for i in range(self._adjustSashIndex(idx) + 1)])

    # Allows to set the relative position (relative to the sash before) of the idx't sash
    # Note: Same as self.SetSashPosition, but with further argument support
    def SetSashRePosition(self, idx, pos):
        idx = self._adjustSashIndex(idx)
        # TODO: finish implementation for negative positioning
        # if pos < 0: # Has not been tested
        # 	if len(self._windows) > idx + 2:
        #		# Does not deliver expected results, probably of the unfinished min/max sizing
        # 		pos += self.GetSashRePosition(idx + 1) + self.GetSashRePosition(idx) # p(i) + p (i+1) + pos, given i+1 is a valid index
        # 	else:
        # 		# Must respect index
        # 		pos += self.GetTotalSpace() - self.GetSashAbsPosition(idx - 1)

        self.SizeWindows()  # <- maybe move
        self.SetSashPosition(idx, pos)

    # Returns the relative position (relative to the sash before) of the idx't sash
    def GetSashRePosition(self, idx):
        return self.GetSashPosition(self._adjustSashIndex(idx))

    # TODO: prof validity of the 3 functions below.
    # 		Should probably be changed, since they are used to determine the size of the splitter itself
    #		because it is often expanded in the parents's sizer. But if that is not the case
    #		the parent size won't give any information about the splitter size. It is hereby suggested to properly
    #		make these functions work
    #
    # ------------------------------------------------------
    def GetWidth(self):
        return self._parent.GetSize().GetWidth()

    def GetHeight(self):
        return self._parent.GetSize().GetHeight()

    def GetTotalSpace(self):
        if self._orient == wx.HORIZONTAL:
            return self.GetWidth()
        else:
            return self.GetHeight()

    # ------------------------------------------------------

    # Returns the accumulated width of all windows in the splitter
    def GetAccumulatedPanelWidth(self):
        return sum(w.GetSize()[0] for w in self._windows)

    # Calculates the space taken by all sashes
    def GetTotalSashSpace(self):
        return self._GetSashSize() * self.GetSashAmount()

    # Calculates the total space taken by all windows TODO: check if maybe redundant if window sizes can be obtained correctly / or maybe this is better
    def GetTotalSpaceWithoutSashes(self):
        return self.GetTotalSpace() - self.GetTotalSashSpace()

    # Calculates the total size without sashes
    def GetSizeWithoutSashes(self):
        s = self.GetSize()
        if self._orient == wx.HORIZONTAL:
            return (s.GetWidth() - self.GetTotalSashSpace(), s.GetHeight())
        else:
            return (s.GetWidth(), s.GetHeight() - self.GetTotalSashSpace())

    # Returns all panel size-objects
    def GetPanelSizes(self):
        return [w.GetSize() for w in self._windows]

    def SetMovable(self, state):
        self._movable = state

    def SetMinimumPaneSize(self, minSize):
        if minSize >= self.__minPaneSizeLowerBound:
            self._minimumPaneSize = minSize
            return True
        return False

    # Returns the correct index if given index is negative
    def _adjustIndex(self, idx, valueAmount):
        return idx if idx >= 0 else valueAmount + idx

    # Uses the sashe amount implicitly to calculate correct index if given index is negative
    def _adjustSashIndex(self, idx):
        return self._adjustIndex(idx, len(self._windows) - 1)

    def _adjustWindowIndex(self, idx):
        # Uses the window amount implicitly to calculate correct index if given index is negative
        return self._adjustIndex(idx, len(self._windows))

    # A convenient class to work with proportions
    class Proportions():
        def __init__(self, splitterOrientation, proportions=None, sizes=None):
            self._splitterOrientation = splitterOrientation
            self._propSize = list()
            self.proportions = list()
            if proportions is None and sizes is None:
                self.proportions = list()
                self.sum = 0
            else:
                self.Add(proportions, sizes)

        def Add(self, proportions, sizes):
            # A size of None indicates minimal size of (0, 0)
            if not isinstance(proportions, list) and not isinstance(sizes, list):
                proportions, sizes = [proportions], [sizes]
            sizes = self.__normSizes(sizes)
            self._propSize.extend([(entry, sizes[index]) for index, entry in enumerate(proportions)])
            self.proportions.extend(proportions)
            self.sum = sum(self.proportions)

        def UpdateSize(self, sizes):
            if not isinstance(sizes, list):
                sizes = [sizes]
            assert len(sizes) == len(self._propSize)
            sizes = self.__normSizes(sizes)
            self._propSize = [(p[0], sizes[i]) for i, p in enumerate(self._propSize)]

        def GetSizes(self):
            return tuple(i[1] for i in self._propSize)

        def GetSizesValues(self):
            return tuple(i[1]._size for i in self._propSize)

        def __normSizes(self, sizes):
            return [self.SplitterSize(s, self._splitterOrientation) for s in sizes]

        def __iter__(self):
            return self._propSize.__iter__()

        def __getitem__(self, item):
            return self._propSize[item]

        # Internally represents all information needed for proportion calculation <- needed for dynamic sizing
        class SplitterSize():
            NoMinimalSize = (0, 0)  # <- needed?
            NoFixedSize = None

            def __init__(self, size, splitterOrientation):
                self.SetOrientation(splitterOrientation)
                # self._size = None #<- good practice to init even if set afterwards?
                self.SetSize(size)

            def GetSize(self):
                return self._size

            def SetSize(self, size):
                if size == self.NoFixedSize:
                    self._size = size
                elif self._orientation == wx.VERTICAL:
                    self._size = size[1]
                else:
                    self._size = size[0]

            def SetSizeSingeValue(self, size):
                self._size = size

            def GetOrientation(self):
                return self._orientation

            def SetOrientation(self, orientation):
                assert orientation in (wx.VERTICAL, wx.HORIZONTAL)
                self._orientation = orientation
