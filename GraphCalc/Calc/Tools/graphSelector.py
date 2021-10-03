from GraphCalc.Components.Property.PropertyManager.propertyManager import ActiveChangedEvent, EVT_ACT_PROP_CH
from GraphCalc.Components.Property.property import ManagerPropertyObject

from GraphCalc.Application.outputPrompt import IOutputExtension

from abc import ABC, abstractmethod
from enum import Enum, auto


# rework this whole file
# -use concept with more extensibility
# -more logical class structure
# -potentially use interruption to use selector
# -use Exceptions instead of assertions
# -expand into more files
# -highlight all selections

# -use issubclass() function

# Stores selected objects inorder or not in order
#todo: remove in order?
class SelectionSequence:
    def __init__(self, inOrder: bool = False):
        self._selection = list()
        self._inOrder = inOrder


    def getSelection(self):
        return self._selection

    def getSelectedTypes(self):
        return list(map(lambda x: type(x), self._selection))

    def isOrdered(self):
        return self._inOrder

    def reset(self):
        self._selection = list()

    def setOrdered(self, state: bool):
        self._inOrder = state

    def add(self, item, allowDupes=False):
        if item not in self._selection or allowDupes:
            self._selection.append(item)

    def remove(self, item):
        self._selection.remove(item)

    def matches(self, selectionPattern, onlyBool=False):
        assert isinstance(selectionPattern, SelectionPattern)

        desired = selectionPattern.desiredTypes
        if desired is DesiredType.ANY:
            return True
        selected = self.getSelectedTypes()
        selectedCopy = selected.copy()


        if self._inOrder:
            for i in range(len(selected)):
                if not desired[i] == selected[i]:
                    return False
            missing = desired[len(selected):]

        else:

            #todo: redundant?
            # if len(selected) > len(desired):
            #     return False
            missing = list()
            for desiredType in desired:
                if desiredType in selectedCopy:
                    selectedCopy.remove(desiredType)
                else:
                    missing.append(desiredType)

            for selectedType in selected:
                if selectedType not in desired:
                    return False

            # if the desired selection cant be possible anymore
            if len(desired) - len(selected) != len(missing):
                return False

        if len(missing) > 0:
            if onlyBool:
                return False
            return list(map(lambda x: x.strRep(), missing))
        else:
            return True


# A selection pattern can be compared with a SelectionSequence and returns True, False or the missing types
#todo: -implement further type checking and limitations => fully implement desiredType-enumeration to replace type of desired types
class SelectionPattern:
    def __init__(self, desiredTypes):
        self.desiredTypes = desiredTypes
        if not self.isNone():
            self.validObjSelection(self.desiredTypes)

    def isNone(self):
        return True if self.desiredTypes is None else False

    @classmethod
    def validObjSelection(cls, objSelection):
        if objSelection is DesiredType.ANY:
            return
        assert not any([not isinstance(i, type) for i in objSelection]), "Expected list of classes"
        assert not any([not issubclass(i, ManagerPropertyObject) for i in objSelection]), "All types must derive from ManagerPropertyObject"

# extend to use a desiredType-dataclass
class DesiredType(Enum):
    ANY = auto()


class PropertySelector(IOutputExtension):
    def __init__(self):
        super().__init__()
        self._selection = None
        self._matching = None

    def setSelector(self, selector: SelectionSequence):
        self._selection = selector

    def selected(self):
        return self._selection

    def matchSelectionObjCall(self, selectionObj):
        assert issubclass(type(selectionObj), SelectionInterface), "Selected Object must include SelectionInterface"
        self._matching = selectionObj
        assert not self._matching.getSelectionPattern().isNone(), "Selection Pattern must be defined"
        self.setSelector(
            SelectionSequence(self._matching.selectInOrder())
        )

        self.sendlTry(f"Selected tool: '{selectionObj.getName()}'")
        self.sendlTry(f"Select: {list(map(lambda x: x.strRep(), self._matching.getSelectionPattern().desiredTypes))}")

    def update(self, evt: ActiveChangedEvent=None):
        if self._matching is None:
            return
        newObj = evt.selected
        if newObj in self._selection.getSelection():
            return
        self._selection.add(newObj)
        if (missing := self._validSelection()) is True:
            self.sendlTry("Selection successful")
            self._matching.run(self._selection)
            self._matched()
        elif missing is False:
            self.sendlTry("Selection failed")
            self._matched()
        else:
            self.sendlTry(f"Select: {missing}")

        evt.Skip()

    def _validSelection(self):
        return self._selection.matches(self._matching.getSelectionPattern())

    def _matched(self):
        self._selection = None
        self._matching = None


class SelectionInterface(ABC):
    _selectionInOrder = True
    _selectionPattern = SelectionPattern(None)

    def __init__(self):
        if self._selectionPattern is None:
            self.__class__._selectionPattern = SelectionPattern(None)
        assert isinstance(self._selectionPattern, SelectionPattern)

    @classmethod
    def getSelectionPattern(cls):
        return cls._selectionPattern

    @classmethod
    def selectInOrder(cls):
        return cls._selectionInOrder