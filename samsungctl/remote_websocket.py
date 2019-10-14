# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import base64
import logging
import threading
import ssl
import websocket
import requests
import time
import json
import socket
from . import exceptions
from . import application
from . import websocket_base
from . import wake_on_lan
from .utils import LogIt, LogItWithReturn

logger = logging.getLogger('samsungctl')


URL_FORMAT = "ws://{}:{}/api/v2/channels/samsung.remote.control?name={}"
SSL_URL_FORMAT = "wss://{}:{}/api/v2/channels/samsung.remote.control?name={}"


class RemoteWebsocket(websocket_base.WebSocketBase):
    """Object for remote control connection."""

    @LogIt
    def __init__(self, config):
        self.receive_lock = threading.Lock()
        self.send_event = threading.Event()
        websocket_base.WebSocketBase.__init__(self, config)

    @property
    @LogItWithReturn
    def has_ssl(self):
        try:
            response = requests.get(
                ' http://{0}:8001/api/v2/'.format(self.config.host),
                timeout=3
            )
            return(
                json.loads(response.content.decode('utf-8'))['device']['TokenAuthSupport']
            )
        except (ValueError, KeyError):
            return False
        except (requests.HTTPError, requests.exceptions.ConnectTimeout):
            return None

    @LogIt
    def open(self):
        if self.sock is not None:
            return True

        self._starting = True
        with self.receive_lock:
            power = self.power

            if not self.config.paired and not power:
                self.power = True

                if not self.power:
                    raise RuntimeError(
                        'Unable to pair with TV.. Is the TV off?!?'
                    )

            if self.sock is not None:
                self.close()

            if self.config.port == 8002 or self.has_ssl:
                self.config.port = 8002

                if self.config.token:
                    logger.debug('using saved token: ' + self.config.token)
                    token = "&token=" + self.config.token
                else:
                    token = ''

                sslopt = {"cert_reqs": ssl.CERT_NONE}
                url = SSL_URL_FORMAT.format(
                    self.config.host,
                    self.config.port,
                    self._serialize_string(self.config.name)
                ) + token
            else:
                self.config.port = 8001

                sslopt = {}
                url = URL_FORMAT.format(
                    self.config.host,
                    self.config.port,
                    self._serialize_string(self.config.name)
                )

            try:
                self.sock = websocket.create_connection(
                    url, 
                    self.config.timeout,
                    #ssl_handshake_timeout=self.config.timeout,
                    sslopt=sslopt
                )
            except:
                if not self.config.paired:
                    raise RuntimeError('Unable to connect to the TV')

                if not self._running:
                    logger.info('Is the TV on?!?')
                self._starting = False
                return False

            auth_event = threading.Event()

            def unauthorized_callback(_):
                auth_event.set()

                self.unregister_receive_callback(
                    auth_callback,
                    'event',
                    'ms.channel.connect'
                )

                if self.config.port == 8001:
                    logger.debug(
                        "Websocket connection failed. Trying ssl connection"
                    )
                    self.config.port = 8002
                    self.open()
                else:
                    self.close()
                    raise RuntimeError('Authentication denied')

            def auth_callback(data):
                logger.debug("Access granted.")

                if 'data' in data and 'token' in data["data"]:
                    self.config.token = data['data']["token"]
                    logger.debug('new token: ' + self.config.token)

                auth_event.set()

                self.unregister_receive_callback(
                    unauthorized_callback,
                    'event',
                    'ms.channel.unauthorized'
                )

                if 'data' in data and 'token' in data["data"]:
                    self.config.token = data['data']["token"]
                    logger.debug('new token: ' + self.config.token)

                if not power and not self.config.paired:
                    self.power = False

                self.config.paired = True
                if self.config.path:
                    self.config.save()

                auth_event.set()

            self.register_receive_callback(
                auth_callback,
                'event',
                'ms.channel.connect'
            )

            self.register_receive_callback(
                unauthorized_callback,
                'event',
                'ms.channel.unauthorized'
            )

            if not self._running:
                self._thread = threading.Thread(target=self.loop)
                self._thread.start()

                if self.config.paired:
                    auth_event.wait(5.0)
                else:
                    auth_event.wait(30.0)

                if not auth_event.isSet():
                    if not self.config.paired and self.config.port == 8001:
                        logger.debug(
                            "Websocket connection failed. Trying ssl connection"
                        )
                        self.config.port = 8002
                        return self.open()
                    else:
                        self.close()
                        raise RuntimeError('Auth Failure')

                self._starting = False
                self.send_event.wait(0.5)
                return True
            else:
                self._starting = False
                return True

    @LogIt
    def send(self, method, **params):
        if self.sock is None:
            if method != 'ms.remote.control':
                if self.power:
                    self.open()
                else:
                    logger.info('Is the TV on?!?')

        payload = dict(
            method=method,
            params=params
        )
        self.sock.send(json.dumps(payload))
        self.send_event.wait(0.3)

    @LogIt
    def power(self, value):
        event = threading.Event()

        if value and not self.power:
            if self.mac_address:
                count = 0
                wake_on_lan.send_wol(self.mac_address)
                event.wait(1.0)

                while not self.power and count < 20:
                    if not self._running:
                        try:
                            self.open()
                        except:
                            pass
                    wake_on_lan.send_wol(self.mac_address)
                    event.wait(1.0)

                    count += 1

                if count == 20:
                    logger.error(
                        'Unable to power on the TV, '
                        'check network connectivity'
                    )
            else:
                logging.error('Unable to get TV\'s mac address')

        elif not value and self.power:
            if self.sock is None:
                self.open()

            count = 0
            #max_count = 5
            max_count = self.config.timeout
            
            power_off = dict(
                Cmd='Click',
                DataOfCmd='KEY_POWEROFF',
                Option="false",
                TypeOfRemote="SendRemoteKey"
            )
            power = dict(
                Cmd='Click',
                DataOfCmd='KEY_POWER',
                Option="false",
                TypeOfRemote="SendRemoteKey"
            )

            logger.info("Sending control command: " + str(power))
            self.send("ms.remote.control", **power)
            logger.info("Sending control command: " + str(power_off))
            self.send("ms.remote.control", **power_off)

            while self.power and count < max_count:
                event.wait(1.0)
                count += 1

            if count == max_count:
                logger.info('Unable to power off the TV')

    power = property(fget=websocket_base.WebSocketBase.power, fset=power)

    @LogIt
    def control(self, key, cmd='Click'):
        """
        Send a control command.
        cmd can be one of the following
        'Click'
        'Press'
        'Release'
        """

        if key == 'KEY_POWERON':
            if not self.power:
                self.power = True
            return
        elif key == 'KEY_POWEROFF':
            if self.power:
                self.power = False
            return
        elif key == 'KEY_POWER':
            self.power = not self.power
            return

        elif self.sock is None:
            if not self.power:
                logger.info('Is the TV on?!?')
                return

            self.open()

        with self.receive_lock:
            params = dict(
                Cmd=cmd,
                DataOfCmd=key,
                Option="false",
                TypeOfRemote="SendRemoteKey"
            )

            logger.info("Sending control command: " + str(params))
            self.send("ms.remote.control", **params)

    _key_interval = 0.5

    @LogItWithReturn
    def get_application(self, pattern):
        for app in self.applications:
            if pattern in (app.app_id, app.name):
                return app

    @property
    @LogItWithReturn
    def applications(self):
        eden_event = threading.Event()
        installed_event = threading.Event()

        eden_data = []
        installed_data = []

        @LogIt
        def eden_app_get(data):
            logger.debug('eden apps: ' + str(data))
            if 'data' in data:
                eden_data.extend(data['data']['data'])
            eden_event.set()

        @LogIt
        def installed_app_get(data):
            logger.debug('installed apps: ' + str(data))
            if 'data' in data:
                installed_data.extend(data['data']['data'])
            installed_event.set()

        self.register_receive_callback(
            eden_app_get,
            'event',
            'ed.edenApp.get'
        )
        self.register_receive_callback(
            installed_app_get,
            'event',
            'ed.installedApp.get'
        )

        for event in ['ed.edenApp.get', 'ed.installedApp.get']:
            params = dict(
                data='',
                event=event,
                to='host'
            )

            self.send('ms.channel.emit', **params)

        eden_event.wait(10.0)
        installed_event.wait(10.0)

        self.unregister_receive_callback(
            eden_app_get,
            'event',
            'ed.edenApp.get'
        )

        self.unregister_receive_callback(
            installed_app_get,
            'data',
            None
        )

        if not eden_event.isSet():
            logger.debug('ed.edenApp.get timed out')

        if not installed_event.isSet():
            logger.debug('ed.installedApp.get timed out')

        if eden_data and installed_data:
            updated_apps = []

            for eden_app in eden_data[:]:
                for installed_app in installed_data[:]:
                    if eden_app['appId'] == installed_app['appId']:
                        installed_data.remove(installed_app)
                        eden_data.remove(eden_app)
                        eden_app.update(installed_app)
                        updated_apps += [eden_app]
                        break
        else:
            updated_apps = []

        updated_apps += eden_data + installed_data

        for app in updated_apps[:]:
            updated_apps.remove(app)
            updated_apps += [application.Application(self, **app)]

        logger.debug('applications returned: ' + str(updated_apps))

        return updated_apps

    @LogIt
    def register_receive_callback(self, callback, key, data):
        self._registered_callbacks += [[callback, key, data]]

    @LogIt
    def unregister_receive_callback(self, callback, key, data):
        if [callback, key, data] in self._registered_callbacks:
            self._registered_callbacks.remove([callback, key, data])

    @LogIt
    def on_message(self, message):
        response = json.loads(message)
        logger.debug('incoming message: ' + message)

        for callback, key, data in self._registered_callbacks[:]:
            if key in response and (data is None or response[key] == data):
                callback(response)
                self._registered_callbacks.remove([callback, key, data])
                break

        else:
            if 'params' in response and 'event' in response['params']:
                event = response['params']['event']

                if event == 'd2d_service_message':
                    data = json.loads(response['params']['data'])

                    if 'event' in data:
                        for callback, key, _ in self._registered_callbacks[:]:
                            if key == data['event']:
                                callback(data)
                                self._registered_callbacks.remove(
                                    [callback, key, None]
                                )
                                break

    @property
    def artmode(self):
        """
        {
            "method":"",
            "params":{
                "clientIp":"192.168.1.20",
                "data":"{
                    \"request\":\"get_artmode_status\",
                    \"id\":\"30852acd-1b7d-4496-8bef-53e1178fa839\"
                }",
                "deviceName":"W1Bob25lXWlQaG9uZQ==",
                "event":"art_app_request",
                "to":"host"
            }
        }"
        """

        params = dict(
            clientIp=socket.gethostbyname(socket.gethostname()),
            data=json.dumps(
                dict(
                    request='get_artmode_status',
                    id=self.config.id
                )
            ),
            deviceName=self._serialize_string(self.config.name),
            event='art_app_request',
            to='host'

        )

        response = []
        event = threading.Event()

        def artmode_callback(data):
            """
            {
                "method":"ms.channel.emit",
                "params":{
                    "clientIp":"127.0.0.1",
                    "data":"{
                        \"id\":\"259320d8-f368-48a4-bf03-789f24a22c0f\",
                        \"event\":\"artmode_status\",
                        \"value\":\"off\",
                        \"target_client_id\":\"84b12082-5f28-461e-8e81-b98ad1c1ffa\"
                    }",
                    "deviceName":"Smart Device",
                    "event":"d2d_service_message",
                    "to":"84b12082-5f28-461e-8e81-b98ad1c1ffa"
                }
            }
            """

            if data['value'] == 'on':
                response.append(True)
            else:
                response.append(False)

            event.set()

        self.register_receive_callback(
            artmode_callback,
            'artmode_status',
            None
        )

        self.send('ms.channel.emit', **params)

        event.wait(2.0)

        self.unregister_receive_callback(
            artmode_callback,
            'artmode_status',
            None
        )

        if not event.isSet():
            logging.debug('get_artmode_status: timed out')
        else:
            return response[0]

    @artmode.setter
    def artmode(self, value):
        """
        {
            "method":"ms.channel.emit",
            "params":{
                "clientIp":"192.168.1.20",
                "data":"{
                    \"id\":\"545fc0c1-bd9b-48f5-8444-02f9c519aaec\",
                    \"value\":\"on\",
                    \"request\":\"set_artmode_status\"
                }",
                "deviceName":"W1Bob25lXWlQaG9uZQ==",
                "event":"art_app_request",
                "to":"host"
            }
        }
        """
        if value:
            value = 'on'

        else:
            value = 'off'

        params = dict(
            clientIp=socket.gethostbyname(socket.gethostname()),
            data=json.dumps(
                dict(
                    request='set_artmode_status',
                    value=value,
                    id=self.config.id
                )
            ),
            deviceName=self._serialize_string(self.config.name),
            event='art_app_request',
            to='host'

        )
        self.send('ms.channel.emit', **params)

    @LogIt
    def input_text(self, text):

        params = dict(
            Cmd=self._serialize_string(text),
            TypeOfRemote="SendInputString",
            DataOfCmd="base64"
        )

        self.send('ms.remote.control', **params)

    @LogIt
    def start_voice_recognition(self):
        """Activates voice recognition."""
        with self.receive_lock:
            event = threading.Event()

            def voice_callback(_):
                event.set()

            self.register_receive_callback(
                voice_callback,
                'event',
                'ms.voiceApp.standby'
            )

            params = dict(
                Cmd='Press',
                DataOfCmd='KEY_BT_VOICE',
                Option="false",
                TypeOfRemote="SendRemoteKey"
            )

            logger.info("Sending control command: " + str(params))
            self.send("ms.remote.control", **params)

            event.wait(2.0)
            self.unregister_receive_callback(
                voice_callback,
                'event',
                'ms.voiceApp.standby'
            )

            if not event.isSet():
                logger.debug('ms.voiceApp.standby timed out')

    @LogIt
    def stop_voice_recognition(self):
        """Activates voice recognition."""

        with self.receive_lock:
            event = threading.Event()

            def voice_callback(_):
                event.set()

            self.register_receive_callback(
                voice_callback,
                'event',
                'ms.voiceApp.hide'
            )

            params = dict(
                Cmd='Release',
                DataOfCmd='KEY_BT_VOICE',
                Option="false",
                TypeOfRemote="SendRemoteKey"
            )

            logger.info("Sending control command: " + str(params))
            self.send("ms.remote.control", **params)

            event.wait(2.0)
            self.unregister_receive_callback(
                voice_callback,
                'event',
                'ms.voiceApp.hide'
            )
            if not event.isSet():
                logger.debug('ms.voiceApp.hide timed out')

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")

    @property
    @LogItWithReturn
    def mouse(self):
        return Mouse(self)


class Mouse(object):

    @LogIt
    def __init__(self, remote):
        self._remote = remote
        self._is_running = False
        self._commands = []
        self._ime_start_event = threading.Event()
        self._ime_update_event = threading.Event()
        self._touch_enable_event = threading.Event()
        self._send_event = threading.Event()

    @property
    @LogItWithReturn
    def is_running(self):
        return self._is_running

    @LogIt
    def clear(self):
        if not self.is_running:
            del self._commands[:]

    @LogIt
    def _send(self, cmd, **kwargs):
        """Send a control command."""

        if not self._remote.connection:
            raise exceptions.ConnectionClosed()

        if not self.is_running:
            params = {
                "Cmd": cmd,
                "TypeOfRemote": "ProcessMouseDevice"
            }
            params.update(kwargs)

            payload = json.dumps({
                "method": "ms.remote.control",
                "params": params
            })

            self._commands += [payload]

    @LogIt
    def left_click(self):
        self._send('LeftClick')

    @LogIt
    def right_click(self):
        self._send('RightClick')

    @LogIt
    def move(self, x, y):
        position = dict(
            x=x,
            y=y,
            Time=str(time.time())
        )

        self._send('Move', Position=position)

    @LogIt
    def add_wait(self, wait):
        if self._is_running:
            self._commands += [wait]

    @LogIt
    def stop(self):
        if self.is_running:
            self._send_event.set()
            self._ime_start_event.set()
            self._ime_update_event.set()
            self._touch_enable_event.set()

    @LogIt
    def run(self):
        if self._remote.sock is None:
            logger.error('Is the TV on??')
            return

        if not self.is_running:
            self._send_event.clear()
            self._ime_start_event.clear()
            self._ime_update_event.clear()
            self._touch_enable_event.clear()

            self._is_running = True

            with self._remote.receive_lock:

                @LogIt
                def ime_start(_):
                    self._ime_start_event.set()

                @LogIt
                def ime_update(_):
                    self._ime_update_event.set()

                @LogIt
                def touch_enable(_):
                    self._touch_enable_event.set()

                self._remote.register_receive_callback(
                    ime_start,
                    'event',
                    'ms.remote.imeStart'
                )

                self._remote.register_receive_callback(
                    ime_update,
                    'event',
                    'ms.remote.imeUpdate'
                )

                self._remote.register_receive_callback(
                    touch_enable,
                    'event',
                    'ms.remote.touchEnable'
                )

                for payload in self._commands:
                    if isinstance(payload, (float, int)):
                        self._send_event.wait(payload)
                        if self._send_event.isSet():
                            self._is_running = False
                            return
                    else:
                        logger.info(
                            "Sending mouse control command: " + str(payload)
                        )
                        self._remote.sock.send(payload)

                self._ime_start_event.wait(len(self._commands))
                self._ime_update_event.wait(len(self._commands))
                self._touch_enable_event.wait(len(self._commands))

                self._remote.unregister_receive_callback(
                    ime_start,
                    'event',
                    'ms.remote.imeStart'
                )

                self._remote.unregister_receive_callback(
                    ime_update,
                    'event',
                    'ms.remote.imeUpdate'
                )

                self._remote.unregister_receive_callback(
                    touch_enable,
                    'event',
                    'ms.remote.touchEnable'
                )

                self._is_running = False
