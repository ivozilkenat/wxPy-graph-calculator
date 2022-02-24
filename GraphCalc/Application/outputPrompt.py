import wx

from MyWx.wx import *
from abc import abstractmethod

# Provides basic methods that must be defined. Otherwise panel doesnt suite needs and becomes invalid
class IValidTextPanel:
    def __init__(self, output=None):
        self._output = output

    # usually set by prompt itself
    def _setOutput(self, output):
        assert isinstance(output, OutputPrompt)
        self._output = output

    def getOutput(self):
        return self._output

    @abstractmethod
    def setTxt(self, txt: str):
        pass

    @abstractmethod
    def setLines(self, lines: List[str]):
        pass

    @abstractmethod
    def appendTxt(self, txt: str):
        pass

    @abstractmethod
    def appendLines(self, lines: List[str]):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def getTxt(self):
        pass

    @abstractmethod
    def getTxtCtrl(self):
        pass


# Main class to handle everything related to output information
class OutputPrompt:
    def __init__(self, txtOutputPanel=None):
        self._panel = None
        self.setPanel(txtOutputPanel)

    def getPanel(self) -> IValidTextPanel:
        return self._panel

    def setPanel(self, panel):
        assert isinstance(panel, IValidTextPanel) or panel is None
        if self._panel is not None:
            self._panel.Destroy()
        self._panel = panel
        if self._panel is not None:
            self._panel._setOutput(self)

    # convenience method
    def send(self, txt):
        if self._panel is not None:
            self._panel.appendTxt(txt)


# General Interface to extend classes to give them basic methods to output to custom prompt
class IOutputExtension:
    def __init__(self, output: OutputPrompt=None):
        self._output = output

    def getOutput(self):
        return self._output

    def setOutput(self, output):
        assert isinstance(output, OutputPrompt)
        self._output = output

    # convenience method
    def output(self):
        return self._output

    def hasOutput(self):
        return True if self._output is not None else False

    def _send(self, line: str):
        self._output.send(line)

    def sendl(self, line: str):
        if self.hasOutput():
            self._send(line)
        else:
            raise OutputNotProvided

    # convenience method
    def sendlTry(self, line: str):
        if self.hasOutput():
            self._send(line)
            return True
        return False


class OutputNotProvided(Exception):
    def __init__(self, message="Missing Output-object"):
        super().__init__(message)


# Basic class to allow displaying of output information
class BasicOutputTextPanel(GenericPanel, IValidTextPanel):
    def __init__(self, parent=None, size=None):
        GenericPanel.__init__(self, parent=parent, size=size)
        IValidTextPanel.__init__(self)
        self._outCtrl: wx.TextCtrl = None
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.build()

    def build(self):
        self._sizer.Clear()
        self._outCtrl = wx.TextCtrl(
            parent=self,
            style=wx.TE_READONLY | wx.TE_MULTILINE
        )
        self._sizer.Add(self._outCtrl, 1, wx.EXPAND)
        self.SetSizer(self._sizer)

    def _outputBuild(method):
        def _inner(obj, *args, **kwargs):
            if obj._outCtrl is not None:
                return method(obj, *args, **kwargs)
            return False
        return _inner

    def _wrapTxt(method):
        def _inner(obj, txt, *args, useWrapper=True, **kwargs):
            if useWrapper:
                return method(obj, obj._txtWrapper(txt), *args, **kwargs)
            else:
                return method(obj, txt, *args, **kwargs)
        return _inner


    def _txtWrapper(self, txt: str):
        if txt is None:
            return "\n"
        return f">>> {txt}"

    @_wrapTxt
    @_outputBuild
    def setTxt(self, txt: str):
        self._outCtrl.SetValue(txt)

    @_outputBuild
    def setLines(self, lines: List[str]):
        self.setTxt("\n".join(map(self._txtWrapper, lines)), useWrapper=False)

    @_wrapTxt
    @_outputBuild
    def appendTxt(self, txt: str):
        self._outCtrl.AppendText(txt + "\n")

    @_outputBuild
    def appendLines(self, lines: List[str]):
        for l in lines:
            self.appendTxt(l)

    @_outputBuild
    def clear(self):
        self._outCtrl.Clear()

    @_outputBuild
    def getTxt(self):
        return self._outCtrl.GetValue()

    @_outputBuild
    def getTxtCtrl(self):
        return self._outCtrl
