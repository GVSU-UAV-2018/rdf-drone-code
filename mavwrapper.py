from collections import namedtuple

from configparser import ConfigParser, DuplicateSectionError

# from MAVLink common message set specification
PARAM_ID_MAX_LENGTH = 16
PARAM_TYPE_REAL32 = 9
PARAM_TYPE_REAL64 = 10 # not supported by a lot of software so we have to use REAL32 :-(
MAV_TYPE_ONBOARD_CONTROLLER = 18
MAV_TYPE_AUTOPILOT_INVALID = 8
MAV_STATE_ACTIVE = 4
MAV_RESULT_IN_PROGRESS = 5

def send_heartbeat(connection, status=MAV_STATE_ACTIVE):
    connection.heartbeat_send(
        MAV_TYPE_ONBOARD_CONTROLLER,
        MAV_TYPE_AUTOPILOT_INVALID,
        0,
        0,
        status)


MavParam = namedtuple('MavParam', ['name', 'value', 'set_param'])

def _set_param(param):
    if param.set_param is not None:
        param.set_param(param)

class MavParamTable(object):
    """
    This class represents parameters stored on this machine (i.e. acting as
    the vehicle end of a MAVLink connection).

    Parameter names are determined when this object is created, by passing
    a list of `MavParam`s to the constructor. They cannot be changed except
    by replacing the entire `MavParamTable` object with a new one.

    Each parameter may have a `set_param` callback that is called with the
    parameter's MavParam object every time the parameter is changed.
    Parameters which don't need a callback can set this to None.

    Parameters appear as regular object members, with a few limitations:

    * the name of a parameter must be no longer than 16 characters,
      so it can be used as a MAVLink param_id.
    * the type of the parameter is always `float`, which is a 64-bit float.
    """

    __slots__ = '_name', '_params', '_lookup', '_handlers'

    def __init__(self, params, name='MAVTable'):
        """
        :param params:
            The list of parameters stored in this object.
        """
        object.__setattr__(self, '_name', name)
        object.__setattr__(self, '_params',
            [MavParam(param.name, float(param.value), param.set_param)
                for param in params])
        object.__setattr__(self, '_lookup',
            {k: i for k, i in zip(
                [param.name for param in params],
                range(len(params)))})
        object.__setattr__(self, '_handlers', {
            'PARAM_REQUEST_READ': self.__class__._handle_PARAM_REQUEST_READ,
            'PARAM_REQUEST_LIST': self.__class__._handle_PARAM_REQUEST_LIST,
            'PARAM_SET': self.__class__._handle_PARAM_SET
            })
        self.load(self._name+'_persistent.ini')


    def __getattr__(self, k):
        if k in self.__slots__:
            return object.__getattr__(self, k)
        try:
            return self._params[self._lookup[k]].value
        except KeyError:
            raise AttributeError(k)

    def __setattr__(self, k, v, save_now=True):
        if k not in self._lookup:
            raise AttributeError('No key "{0}"'.format(k))
        i = self._lookup[k]
        old_value = self._params[i]
        result = MavParam(k, float(v), old_value.set_param)
        if result.set_param is not None:
            result.set_param(result)
        self._params[i] = result
        self.save(self._name+'_persistent.ini')


    def __repr__(self):
        return '{0}({1})'.format(self.__class__, self._params)


    def load(self, filename):
        parser = ConfigParser()
        parser.optionxform = str
        try:
            with open(filename, 'r') as config_file:
                parser.readfp(config_file)
        except:
            print('Failed to read saved settings file "{0}"'.format(filename))

        try:
            for k, v in parser.items('saved'):
                try:
                    self.__setattr__(k, float(v), save_now=False)
                except Exception as e:
                    print('Failed to load "{0}": {1}'.format(k, e))
        except:
            print('Failed to read saved settings file "{0}", section "saved"'.format(filename))


    def save(self, filename):
        parser = ConfigParser()
        parser.optionxform = str
        try:
            with open(filename, 'r') as config_file:
                parser.readfp(config_file)
        except:
            print('Failed to read saved settings file')

        try:
            parser.add_section('saved')
        except DuplicateSectionError:
            pass

        for param in self._params:
            parser.set('saved', param.name, str(param.value))

        try:
            with open(filename, 'w') as config_file:
                parser.write(config_file)
        except:
            print('Failed to write saved settings file')


    def handle(self, connection, message):
        """
        Handle an incoming message and use connection to send any response.
        :param connection:
            The connection the message was received on.
        :param message:
            The received message.
        """
        h = self._handlers.get(message.get_type())
        if h is not None:
            h(self, connection, message)

    def _send_param(self, connection, k, i):
        if i < 0:
            i = self._lookup[k]
        v = self._params[i].value
        print('Sending PARAM_VALUE for {0}:{1}'.format(k, v))
        connection.param_value_send(
            k, v, PARAM_TYPE_REAL32, len(self._params), i)


    def _handle_PARAM_REQUEST_READ(self, connection, message):
        try:
            self._send_param(connection, message.param_id, message.param_index)
        except Exception as ex:
            print('{0} failed: {1}'.format(message.get_type(), ex))

    def _handle_PARAM_REQUEST_LIST(self, connection, message):
        for param in self._params:
            self._send_param(connection, param.name, -1)

    def _handle_PARAM_SET(self, connection, message):
        print('PARAM_SET: {0}: {1}'.format(message.param_id, message.param_value))
        try:
            self.__setattr__(message.param_id, message.param_value)
            self._send_param(connection, message.param_id, -1)
        except Exception as ex:
            print('{0} failed: {1}'.format(message.get_type(), ex))
