from composition.base import CompositionField

class ChildsAggregationField(CompositionField):
    def __init__(self, field, do, native=None, signal=None, instance_getter=None):
        self.field = field
        self.do = do
        self.native = native
        self.signal = signal
        self.instance_getter = instance_getter
