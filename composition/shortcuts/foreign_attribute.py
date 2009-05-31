from copy import deepcopy

from django.db import models
from django.db.models.related import RelatedObject

from composition.base import CompositionField

class ForeignAttributeField(CompositionField):
    """
        Composition field that can track changes of related objects attributes.
    """
    def __init__(self, field, native=None):
        """
            field - path to related field, e.g. 'director.country.name'
            native - field instance to store value
        """
        self.field = field
        self.native = native

        self.internal_init()

    def introspect_class(self, cls):
        bits = self.field.split(".")

        if len(bits) < 2:
            raise ValueError("Illegal path to foreign field")

        foreign_field = None

        related_models_chain = [cls]
        related_names_chain = []

        for bit in bits[:-1]:
            meta = related_models_chain[-1]._meta

            try:
                foreign_field = meta.get_field(bit)
            except models.FieldDoesNotExist:
                raise ValueError("Field '%s' does not exist" % bit)

            if isinstance(foreign_field, models.ForeignKey):
                if isinstance(foreign_field.rel.to, basestring):
                    raise ValueError("Model with name '%s' must be class instance not string" % foreign_field.rel.to)

                related_name = foreign_field.rel.related_name
                if not related_name:
                    related_name = RelatedObject(
                        foreign_field.rel.to,
                        related_models_chain[-1],
                        foreign_field
                    ).get_accessor_name()

                related_models_chain.append(foreign_field.rel.to)
                related_names_chain.append(related_name)
            else:
                raise ValueError("Foreign fields in path must be ForeignField"
                                 "instances except last. Got %s" % foreign_field.__name__)

        native = self.native
        if not native:
            field_name = bits[-1]
            try:
                native = deepcopy(related_models_chain[-1]._meta.get_field(field_name))
                native.creation_counter = models.Field.creation_counter
                models.Field.creation_counter += 1
            except models.FieldDoesNotExist:
                raise ValueError("Leaf field '%s' does not exist" % field_name)

        def get_root_instances(instance, chain):
            attr = getattr(instance, chain.pop()).all()

            if chain:
                for obj in attr:
                    for inst in get_root_instances(
                        obj,
                        chain
                    ):
                        yield inst
            else:
                for obj in attr:
                    yield obj

        def get_leaf_instance(instance, chain):
            for bit in chain:
                instance = getattr(instance, bit)

            return instance

        self.internal_init(
            native=native,
            trigger=[
                dict(
                    on=(models.signals.post_save, models.signals.post_delete),
                    sender_model=related_models_chain[-1],
                    do=lambda holder, foreign, signal: getattr(foreign, bits[-1]),
                    field_holder_getter=lambda foreign: get_root_instances(foreign, related_names_chain[:])
                ),
                dict(
                    on=models.signals.pre_save,
                    sender_model=related_models_chain[0],
                    do=lambda holder, _, signal: get_leaf_instance(holder, bits[:]),
                    commit=False, # to prevent recursion `save` method call
                )
            ],
            update_method=dict(
                queryset=lambda holder: get_leaf_instance(holder, bits[:-1])#FIXME: rename queryset
            )
        )
        # TODO: add support for selective object handling to prevent pre_save unneeded work
