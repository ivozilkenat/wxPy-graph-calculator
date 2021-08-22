import wx


def expanded(widget, padding=0):
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(widget, 1, wx.EXPAND | wx.ALL, padding)
    return sizer
