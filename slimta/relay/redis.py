from __future__ import absolute_import

from logging import getLogger
from slimta.relay import Relay, PermanentRelayError
from slimta.smtp.reply import Reply, unhandled_error
from time import sleep
import uuid

from redis import StrictRedis
from redis.exceptions import ConnectionError


class RedisRelay(Relay):
    '''
    post every envelope this relay gets to redis channels!
    '''

    def __init__(self, url):
        super(RedisRelay, self).__init__()
        self._log = getLogger('system.relay.redis')
        self._connection = None
        self._interupted = False
        self._url = url
        self._encoder = None
        # do not use None as a socket timeout or you will never return
        self._socket_timeout = 1
        self._socket_connect_timeout = 1
        self._socket_keepalive = True

    def set_socket_connect_timeout(self, value):
        self._socket_connect_timeout = int(value)

    def set_socket_keepalive(self, value):
        self._socket_keepalive = bool(value)

    def set_timeout(self, value):
        self._socket_timeout = int(value)

    def set_encoder(self, encoder):
        self._encoder = encoder

    def _reconnect_if_necessary(self):
        # this looks like it is terribly wrong since it could never terminate
        while not self._interupted:
            try:
                self._connection = StrictRedis.from_url(
                    self._url,
                    socket_timeout=self._socket_timeout,
                    socket_connect_timeout=self._socket_connect_timeout,
                    socket_keepalive=self._socket_keepalive)
                return
            except ConnectionError:
                self._log.warn('while connecting', exc_info=True)
                sleep(2)

    def attempt(self, envelope, attempts):
        raise NotImplementedError(type(self))

    def kill(self):
        self._connection = None


class RedisQueueRelay(RedisRelay):

    def __init__(self, url, qname):
        super(RedisQueueRelay, self).__init__(url)
        self._qname = qname

    def attempt(self, envelope, attempts):
        try:
            encoded = self._encoder.encode(envelope)
            self._reconnect_if_necessary()
            msgId = uuid.uuid4()

            self._connection.rpush(self._qname, encoded)
            return Reply('250', '2.0.0 Message Delivered; {0!s}'.format(msgId))
        except:
            msg = 'while attempting to deliver envelope'
            self._log.error(msg, exc_info=True)
        return PermanentRelayError('unable to deliver')


class RedisPublisherRelay(RedisRelay):

    def __init__(self, url, channel):
        super(RedisPublisherRelay, self).__init__(url)
        self._channel = str(channel)

    def attempt(self, envelope, attempts):
        try:
            encoded = self._encoder.encode(envelope)
            self._reconnect_if_necessary()
            msgId = uuid.uuid4()

            self._connection.publish(self._channel, encoded)
            return Reply('250', '2.0.0 Message Delivered; {0!s}'.format(msgId))
        except:
            msg = 'while attempting to deliver envelope'
            self._log.error(msg, exc_info=True)
        return unhandled_error
