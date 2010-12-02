from django.db import models
from django.utils.itercompat import is_iterable

from composition.trigger import Trigger

class CompositionMeta(object):
    def __init__(self, model, field, name, trigger,\
                  commons, commit, update_method):#TODO: remove commit param
        self.model = model
        self.name = name
        self.trigger = []

        if not commons:
            commons = {}
        self.commons = commons

        if not is_iterable(trigger) or isinstance(trigger, dict):
            trigger = [trigger]

        trigger_defaults = dict(
            sender_model=model,
            sender=None,
            on=[models.signals.post_save],
            field_holder_getter=lambda instance: instance,
            field_name=name,
            commit=True
        )
        trigger_defaults.update(commons)

        if not len(trigger):
            raise ValueError("At least one trigger must be specefied")

        for t in trigger:
            trigger_meta = trigger_defaults.copy()
            trigger_meta.update(t)

            trigger_obj = Trigger(**trigger_meta)
            trigger_obj.connect()

            self.trigger.append(trigger_obj)

        update_method_defaults = dict(
            initial=None,
            name="update_%s" % name,
            do=self.trigger[0],
            queryset=None
        )
        update_method_defaults.update(update_method)

        if isinstance(update_method_defaults["do"], (int, long)):
            n = update_method_defaults["do"]
            if n >= len(self.trigger):
                raise ValueError("Update method trigger must be index of trigger list")
            update_method_defaults["do"] = self.trigger[update_method_defaults["do"]]

        self.update_method = update_method_defaults

        setattr(model, self.update_method["name"], lambda instance: self._update_method(instance))
        setattr(model, "freeze_%s" % name, lambda instance: self._freeze_method(instance))

    def toggle_freeze(self):
        for t in self.trigger:
            t.freeze = not t.freeze

    def _update_method(self, instance):
        """
            Generic `update_FOO` method that is connected to model
        """
        qs_getter = self.update_method["queryset"]
        if qs_getter is None:
            qs_getter = [instance]

        trigger = self.update_method["do"]

        setattr(instance, trigger.field_name, self.update_method["initial"])
        if callable(qs_getter):
            qs = qs_getter(instance)
        else:
            qs = qs_getter

        if not is_iterable(qs):
            qs = [qs]

        for obj in qs:
            setattr(
                instance,
                trigger.field_name,
                trigger.do(instance, obj, trigger.on[0])
            )

        instance.save()

    def _freeze_method(self, instance):
        """
            Generic `freeze_FOO` method that is connected to model
        """
        self.toggle_freeze()
