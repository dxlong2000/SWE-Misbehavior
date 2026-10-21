"""
Provide django-style hooks for model events.
"""
from peewee import Model as _Model


class Signal(object):
    def __init__(self):
        self._flush()

    def _flush(self):
        self._receivers = set()
        self._receiver_list = []

    def connect(self, receiver, name=None, sender=None):
        name = name or receiver.__name__
        key = (name, sender)
        if key not in self._receivers:
            self._receivers.add(key)
            self._receiver_list.append((name, receiver, sender))
        else:
            raise ValueError('receiver named %s (for sender=%s) already '
                             'connected' % (name, sender or 'any'))

    def disconnect(self, receiver=None, name=None, sender=None):
        """Disconnect a receiver from the Signal instance. It removes the receiver from the list of receivers and updates the receiver list accordingly in which every element format is (name, receiver, sender).
        Input-Output Arguments
        :param self: Signal. An instance of the Signal class.
        :param receiver: Object. The receiver to be disconnected from the Signal instance. Defaults to None.
        :param name: String. The name of the receiver. If not provided, it is inferred from the receiver's name. Defaults to None.
        :param sender: Object. The sender of the signal. If provided, only the receiver with the specified sender will be disconnected. Defaults to None.
        :return: No return values.
        """

    def __call__(self, name=None, sender=None):
        def decorator(fn):
            self.connect(fn, name, sender)
            return fn
        return decorator

    def send(self, instance, *args, **kwargs):
        sender = type(instance)
        responses = []
        for n, r, s in self._receiver_list:
            if s is None or isinstance(instance, s):
                responses.append((r, r(sender, instance, *args, **kwargs)))
        return responses


pre_save = Signal()
post_save = Signal()
pre_delete = Signal()
post_delete = Signal()
pre_init = Signal()


class Model(_Model):
    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        pre_init.send(self)

    def save(self, *args, **kwargs):
        pk_value = self._pk if self._meta.primary_key else True
        created = kwargs.get('force_insert', False) or not bool(pk_value)
        pre_save.send(self, created=created)
        ret = super(Model, self).save(*args, **kwargs)
        post_save.send(self, created=created)
        return ret

    def delete_instance(self, *args, **kwargs):
        pre_delete.send(self)
        ret = super(Model, self).delete_instance(*args, **kwargs)
        post_delete.send(self)
        return ret