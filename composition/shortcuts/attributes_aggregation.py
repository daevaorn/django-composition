from composition.base import CompositionField

class AttributesAggregationField(CompositionField):
    def __init__(self, field, do, native=None):
        self.field = field
        self.do = do
        self.native = native
