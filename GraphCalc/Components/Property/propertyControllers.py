from GraphCalc.Components.Property._property import Property, ToggleProperty, NumProperty


# A class that allows for any Object to bind a Property to it, which can be manipulated due to that
class PropertyController:
    def __init__(self, assignProperty=None):
        self.bindTo(assignProperty)

    def bindTo(self, targetProperty):
        self.assignedProperty = targetProperty


class TogglePropertyController(PropertyController):
    def __init__(self, assignProperty=None):
        assert isinstance(assignProperty, ToggleProperty)
        super().__init__(assignProperty)


class SliderPropertyController(PropertyController):
    def __init__(self, assignProperty=None):
        assert isinstance(assignProperty, NumProperty)
        super().__init__(assignProperty)


class InputPropertyController(PropertyController):
    def __init__(self, assignProperty=None):
        assert isinstance(assignProperty, Property)
        super().__init__(assignProperty)
