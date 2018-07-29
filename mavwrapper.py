# Pymavlink is... mostly not documented, so most of our knowledge of it comes
# from reading the (mostly auto-generated) code. This works, but we might be
# doing some things that aren't intended, because we don't always know _what_
# was intended.
#
# We are using pymavlink.mavutil because it's convenient.
# However, it is _not_ the proper abstraction.
# mavutil assumes that it's on the end of the connection which sends commands
# and receives telemetry, but we're on the end which receives commands and
# sends telemetry, which is exactly the opposite.
#
# We are _not_ using pymavlink.mavparm because, again, it assumes we are on
# the commanding end of the connection, which we aren't.
#
# If we had more time, we might either modify mavutil so that it can work on
# the 'vehicle' end of a connection without surprises, or add a separate module
# to do so.

from collections import namedtuple

PARAM_ID_MAX_LENGTH = 16 # from MAVLink common message set specification
PARAM_TYPE_REAL64 = 10 # from MAVLink common message set specification

MavParam = namedtuple('MavParam', ['name', 'value'])

class MavParamTable(object):
    """
    This class represents parameters stored on this machine (i.e. acting as
    the vehicle end of a MAVLink connection).
    Parameters are determined when this object is created, by passing
    a list of `MavParam`s to the constructor. They cannot be changed except
    by replacing the entire `MavParamTable` object with a new one.

    Parameters appear as regular object members, with a few limitations:

    * the name of a parameter must be no longer than 16 characters,
      so it can be used as a MAVLink param_id.
    * the type of the parameter is always `float` (MAV_PARAM_TYPE_REAL64),
      which is a 64-bit float.
    """

    __slots__ = '_params', '_lookup', '_handlers', '_on_param_changed'

    def __init__(self, *params, on_param_changed = None):
        """
        :param params:
            The list of parameters stored in this object.
        :param on_param_changed:
            An (optional) function to call when a parameter is set on this
            object. on_param_changed receives this object and the name of
            the changed parameter.
        """
        object.__setattr__(self, '_params',
            [MavParam(param.name, float(param.value)) for param in params])
        object.__setattr__(self, '_lookup',
            {k: i for k, i in zip(
                [param.name for param in params],
                range(len(params)))})
        object.__setattr__(self, '_handlers', {
            'PARAM_REQUEST_READ': self.__class__._handle_PARAM_REQUEST_READ,
            'PARAM_REQUEST_LIST': self.__class__._handle_PARAM_REQUEST_LIST,
            'PARAM_SET': self.__class__._handle_PARAM_SET
            })
        object.__setattr__(self, '_on_param_changed', on_param_changed)


    def __getattr__(self, k):
        if k in self.__slots__:
            return object.__getattr__(k)
        try:
            return self._params[self._lookup[k]].value
        except KeyError:
            raise AttributeError(k)

    def __setattr__(self, k, v):
        if k not in self._lookup:
            raise AttributeError(k)
        self._values[self.lookup[k]] = MavParam(k, float(v))
        if self._on_param_changed:
            self._on_param_changed(self, param.name)


    def __repr__(self):
        return '{0}({1})'.format(self.__class__, self._params)


    def handle(self, connection, message):
        """
        Handle an incoming message and use connection to send any response.
        """
        h = self._handlers.get(message.get_type())
        if h is not None:
            h(self, connection, message)

    def _send_param(self, connection, k):
        i = self._lookup[k]
        v = self._params[i].value
        connection.param_value_send(
            k, v, PARAM_TYPE_REAL64, len(self._params), i)
        

    def _handle_PARAM_REQUEST_READ(self, connection, message):
        if message.param_id not in self._lookup:
            return
        self._send_param(connection, message.param_id)

    def _handle_PARAM_REQUEST_LIST(self, connection, message):
        for param in self._params:
            self._send_param(param.name)

    def _handle_PARAM_SET(self, connection, message):
        if message.param_id not in self._lookup:
            return
        self._values[self.lookup[message.param_id]] = MavParam(k, float(v))
        if self._on_param_changed:
            self._on_param_changed(self, param.name)
        self._send_param(param.name)
