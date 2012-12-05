from django.db import models

from composition.meta import CompositionMeta

class CompositionField(object):
    def __init__(self, native, trigger=None, commons={},\
                     commit=True, update_method={}):
        self.internal_init(native, trigger, commons, commit, update_method)

    def internal_init(self, native=None, trigger=None, commons={},\
                     commit=True, update_method={}):
        """
            CompositionField class that patches native field
            with custom `contribute_to_class` method

            Params:
                 * native - Django field instance for current compostion field
                 * trigger - one or some numberr of triggers that handle composition.
                    Trigger is a dict with allowed keys:
                      * on - signal or list of signals that this field handles
                      * do - signals handler, with 3 params:
                               * related instance
                               * instance (that comes with signal send)
                               * concrete signal (one from `on` value)
                      * field_holder_getter - function that gets instance(that comes with signal send)\
                                              as parameter and returns field holder
                                              object (related instance)
                      * sender - signal sender
                      * sender_model - model instance or model name that send signal
                      * commit - flag that indicates save instance after trigger appliance or not
                 * commons - a trigger like field with common settings
                             for all given triggers
                 * update_method - dict for customization of update_method. Allowed params:
                        * initial - initial value to field before applince of method
                        * do - index of update trigger or trigger itself
                        * queryset - query set or callable(with one param - `instance` of an holder model)
                                that have to retun something iterable
                        * name - custom method name instead of `update_FOO`
        """
        if native is not None:
            import new
            self.__class__ = new.classobj(
                self.__class__.__name__,
                tuple([self.__class__, native.__class__] + list(self.__class__.__mro__[1:])),
                {}
            )

            self.__dict__.update(native.__dict__)

        self._c_native = native

        self._c_trigger = trigger
        self._c_commons = commons
        self._c_commit = commit
        self._c_update_method = update_method

    def contribute_to_class(self, cls, name):
        self._c_name = name

        if not self._c_native:
            models.signals.class_prepared.connect(
                self.deferred_contribute_to_class,
                sender=cls
            )
        else:
            self._composition_meta = self.create_meta(cls)
            return self._c_native.__class__.contribute_to_class(self, cls, name)

    def create_meta(self, cls):
        return CompositionMeta(
            cls, self._c_native, self._c_name, self._c_trigger,\
            self._c_commons, self._c_commit, self._c_update_method
        )

    def deferred_contribute_to_class(self, sender, **kwargs):
        cls = sender

        self.introspect_class(cls)
        self._composition_meta = self.create_meta(cls)
        return self._c_native.__class__.contribute_to_class(self, cls, self._c_name)

    def introspect_class(self, cls):
        pass

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = self._c_native.__class__.__module__ + "." + self._c_native.__class__.__name__
        args, kwargs = introspector(self._c_native)
        # That's our definition!
        return (field_class, args, kwargs)
