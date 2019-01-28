# -*- coding: utf-8 -*-
"""
The code for the encrypted websocket connection is a modified version of the
SmartCrypto library that was modified by eclair4151.
I want to thank eclair4151 for writing the code that allows the samsungctl
library to support H and J (2014, 2015) model TV's

https://github.com/eclair4151/SmartCrypto
"""

# TODO: Python 2 compatibility

from __future__ import print_function
import sys

if sys.version_info[0] < 3:
    raise ImportError

from . import crypto # NOQA
import re # NOQA
from .command_encryption import AESCipher # NOQA
from ..utils import LogIt, LogItWithReturn # NOQA
from .. import wake_on_lan # NOQA
import requests # NOQA
import time # NOQA
import websocket # NOQA
import threading # NOQA
import logging # NOQA

logger = logging.getLogger('samsungctl')


class RemoteEncrypted(object):

    @LogIt
    def __init__(self, config):

        if config.token:
            self.ctx, self.current_session_id = config.token.rsplit(':', 1)

            try:
                self.current_session_id = int(self.current_session_id)
            except ValueError:
                pass
        else:
            self.ctx = None
            self.current_session_id = None

        self.sk_prime = False
        self.last_request_id = 0
        self.aes_lib = None
        self.sock = None
        self.config = config
        self._running = False
        self._mac_address = None
        self._power_event = threading.Event()
        self._starting = True

    @property
    @LogItWithReturn
    def mac_address(self):
        if self._mac_address is None:
            _mac_address = wake_on_lan.get_mac_address(self.config.host)
            if _mac_address is None:
                _mac_address = ''

            self._mac_address = _mac_address

        return self._mac_address

    @property
    @LogItWithReturn
    def power(self):
        if not self._starting and not self._running and self.config.paired:
            try:
                self.open()
                return True
            except RuntimeError:
                return False

        try:
            requests.get(
                ' http://{0}:8001/api/v2/'.format(self.config.host),
                timeout=2
            )
            return True
        except (requests.HTTPError, requests.exceptions.ConnectTimeout):
            return False

    @power.setter
    @LogIt
    def power(self, value):
        if not self._starting and not self._running and self.config.paired:
            try:
                self.open()
            except RuntimeError:
                pass

        if value and self.sock is None:
            if self.mac_address:
                count = 0
                wake_on_lan.send_wol(self.mac_address)
                self._power_event.wait(10)

                try:
                    self.open()
                except:
                    while not self._power_event.isSet() and count < 6:
                        wake_on_lan.send_wol(self.mac_address)
                        self._power_event.wait(2)
                        try:
                            self.open()
                            break
                        except:
                            count += 1

                    if count == 6:
                        logger.error(
                            'Unable to power on the TV, '
                            'check network connectivity'
                        )

        elif not value and self.sock is not None:
            count = 0
            while (
                not self._power_event.isSet() and
                self.sock is not None and
                count < 6
            ):
                self.control('KEY_POWER')
                self.control('KEY_POWEROFF')
                self._power_event.wait(2.0)
                count += 1

            if count == 6:
                logger.info('Unable to power off the TV')

    @LogIt
    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    @LogIt
    def open(self):
        self._starting = True
        if self.ctx is None:
            self.start_pairing()
            while self.ctx is None:
                tv_pin = input("Please enter pin from tv: ")

                logger.info("Got pin: '" + tv_pin + "'\n")

                self.first_step_of_pairing()
                output = self.hello_exchange(tv_pin)
                if output:
                    self.ctx = output['ctx'].hex()
                    self.sk_prime = output['SKPrime']
                    logger.debug("ctx: " + self.ctx)
                    logger.info("Pin accepted :)\n")
                else:
                    logger.info("Pin incorrect. Please try again...\n")

            self.current_session_id = self.acknowledge_exchange()
            self.config.token = (
                str(self.ctx) + ':' + str(self.current_session_id)
            )

            logger.info('***************************************')
            logger.info('USE THE FOLLOWING NEXT TIME YOU CONNECT')
            logger.info('***************************************')
            logger.info(
                '--host {0} '
                '--method encryption '
                '--token {1}'.format(self.config.host, self.config.token)
            )

            self.close_pin_page()
            logger.info("Authorization successful :)\n")
            self.config.paired = True

        millis = int(round(time.time() * 1000))
        step4_url = (
            'http://' +
            self.config.host +
            ':8000/socket.io/1/?t=' +
            str(millis)
        )

        if not self.power:
            self.power = True

        try:
            websocket_response = requests.get(step4_url, timeout=3)
        except (requests.HTTPError, requests.exceptions.ConnectTimeout):
            raise RuntimeError(
                'Unable to open connection.. Is the TV off?!?'
            )

        print('websocket_response: ' + websocket_response.content.decode("utf-8"))

        websocket_url = (
            'ws://' +
            self.config.host +
            ':8000/socket.io/1/websocket/' +
            websocket_response.text.split(':')[0]
        )

        logger.debug(websocket_url)

        self.aes_lib = AESCipher(self.ctx.upper(), self.current_session_id)
        self.sock = websocket.create_connection(websocket_url)
        time.sleep(0.35)
        self._starting = False

    @LogItWithReturn
    def get_full_url(self, url_path):
        return (
            "http://{0}:{1}{2}".format(
                self.config.host,
                self.config.port,
                url_path
            )
        )

    @LogItWithReturn
    def get_request_url(self, step):
        return self.get_full_url(
            "/ws/pairing?step=" +
            str(step) +
            "&app_id=" +
            self.config.app_id +
            "&device_id=" +
            self.config.device_id
        )

    @LogIt
    def show_pin_page(self):
        response = requests.post(self.get_full_url("/ws/apps/CloudPINPage"), "pin4")
        print('show_pin_page: ' + response.content.decode("utf-8"))

    @LogItWithReturn
    def check_pin_page(self):
        if not self.config.paired:
            if not self.power:
                self.power = True

        full_url = self.get_full_url("/ws/apps/CloudPINPage")

        try:
            page = requests.get(full_url, timeout=3).text
        except (requests.HTTPError, requests.exceptions.ConnectTimeout):
            if not self.config.paired:
                raise RuntimeError('Unable to pair with TV.. Is the TV off?!?')
            else:
                raise RuntimeError(
                    'Unable to connect with TV.. Is the TV off?!?'
                )

        print('page: ' + page)

        output = re.search('state>([^<>]*)</state>', page, flags=re.IGNORECASE)
        if output is not None:
            state = output.group(1)
            logger.debug("Current state: " + state)
            if state == "stopped":
                return True
        return False

    @LogIt
    def first_step_of_pairing(self):
        first_step_url = self.get_request_url(0)
        first_step_url += "&type=1"
        _ = requests.get(first_step_url).text

    @LogIt
    def start_pairing(self):
        self.last_request_id = 0

        if self.check_pin_page():
            logger.debug("Pin NOT on TV")
            self.show_pin_page()
        else:
            logger.debug("Pin ON TV")

    @LogItWithReturn
    def hello_exchange(self, pin):
        hello_output = crypto.generateServerHello(self.config.id, pin)

        if not hello_output:
            return False

        content = (
            "{\"auth_Data\":{\"auth_type\":\"SPC\",\"GeneratorServerHello\":\""
            + hello_output['serverHello'].hex().upper()
            + "\"}}"
        )

        second_step_url = self.get_request_url(1)
        second_step_response = requests.post(second_step_url, content).text
        print('second_step_response: ' + second_step_response)
        logger.debug('second_step_response: ' + second_step_response)

        output = re.search(
            'request_id.*?(\d).*?GeneratorClientHello.*?:.*?(\d[0-9a-zA-Z]*)',
            second_step_response,
            flags=re.IGNORECASE
        )

        if output is None:
            return False

        request_id = output.group(1)
        client_hello = output.group(2)
        self.last_request_id = int(request_id)

        return crypto.parseClientHello(
            client_hello,
            hello_output['hash'],
            hello_output['AES_key'],
            self.config.id
        )

    @LogItWithReturn
    def acknowledge_exchange(self):
        server_ack_message = crypto.generateServerAcknowledge(self.sk_prime)
        content = (
            "{\"auth_Data\":{\"auth_type\":\"SPC\",\"request_id\":\"" +
            str(self.last_request_id) +
            "\",\"ServerAckMsg\":\"" +
            server_ack_message +
            "\"}}"
        )

        third_step_url = self.get_request_url(2)
        third_step_response = requests.post(third_step_url, content).text

        print('third_step_response: ' + third_step_response)

        if "secure-mode" in third_step_response:
            raise RuntimeError(
                "TODO: Implement handling of encryption flag!!!!"
            )

        output = re.search(
            'ClientAckMsg.*?:.*?(\d[0-9a-zA-Z]*).*?session_id.*?(\d)',
            third_step_response,
            flags=re.IGNORECASE
        )

        if output is None:
            raise RuntimeError(
                "Unable to get session_id and/or ClientAckMsg!!!"
            )

        client_ack = output.group(1)
        if not crypto.parseClientAcknowledge(client_ack, self.sk_prime):
            raise RuntimeError("Parse client ack message failed.")

        session_id = output.group(2)
        logger.debug("session_id: " + session_id)

        return session_id

    @LogIt
    def close_pin_page(self):
        full_url = self.get_full_url("/ws/apps/CloudPINPage/run")
        requests.delete(full_url)
        return False

    @LogIt
    def control(self, key):
        if self.sock is None:
            if not self._running:
                self.open()
            else:
                logger.info('Is thee TV on?!?')
                return
        try:

            # need sleeps cuz if you send commands to quick it fails
            self.sock.send('1::/com.samsung.companion')
            # pairs to this app with this command.
            time.sleep(0.35)

            self.sock.send(self.aes_lib.generate_command(key))
            time.sleep(0.35)
            return True
        except:
            self.sock = None
            return False
