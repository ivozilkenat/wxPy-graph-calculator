from MyWx.wx import *

from GraphCalc.Components.Property._property import PropertyObject

from typing import List

class PropertyManager():
	def __init__(self):
		self._propertyObjects : List[PropertyObject] = []

	def getPropObjects(self):
		return self._propertyObjects
	def addPropObject(self, propertyObject : PropertyObject):
		assert isinstance(propertyObject, PropertyObject)
		self._propertyObjects.append(propertyObject)
	def removePropObject(self, propertyObject : PropertyObject):
		assert isinstance(propertyObject, PropertyObject)
		self._propertyObjects.remove(propertyObject)

	def getPropertiesByCategory(self):
		categoryDic = PropertyObject.Category.categoryDict()
		for p in self._propertyObjects:
			categoryDic[p.getCategory()].append(p)
		return categoryDic

	def createOverviewPanel(self, parent : wx.Window):
		return PropObjectOverviewPanel(manager = self, parent = parent)
	def createInspectionPanel(self, parent : wx.Window, overviewPanel):
		return PropInspectionPanel(manager = self, overviewPanel = overviewPanel, parent = parent)

class PropObjectOverviewPanel(GenericPanel):
	def __init__(self, manager : PropertyManager, parent=None, size=None):
		super().__init__(parent=parent, size=size)
		self._manager = manager

class PropInspectionPanel(GenericPanel):
	def __init__(self, manager : PropertyManager, overviewPanel : PropObjectOverviewPanel, parent=None, size=None):
		super().__init__(parent=parent, size=size)
		self._manager = manager
		self._overview = overviewPanel