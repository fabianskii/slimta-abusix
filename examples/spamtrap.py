#!/usr/bin/env python
from argparse import ArgumentParser
from cStringIO import StringIO
from json import load, dumps
from logging import basicConfig, DEBUG, getLogger
from logging.config import dictConfig
from slimta.edge.smtp import (SmtpEdge, SmtpValidators)
from slimta.queue.proxy import ProxyQueue
from slimta.relay.redis import (RedisPublisherRelay, RedisQueueRelay)

from gevent.event import Event


DEFAULT_LOGGER_CONF = '''{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "default": {
      "format": "%(asctime)s %(name)s - %(levelname)s - %(message)s",
      "datefmt": "%Y-%m-%dT%H:%M:%S"
    }
  },
  "handlers": {
    "console": {
      "class":     "logging.StreamHandler",
      "level":     "DEBUG",
      "formatter": "default",
      "stream":    "ext://sys.stderr"
    }
  },
  "loggers": {
    "system.relay": {
      "level": "IMPORTANT",
      "handler": ["console"]
    }
  },
  "root": {
    "level": 20,
    "handlers": ["console"]
  }
}'''


class JSONEventEncoder(object):
    '''
    an instance of this can extract informations from an envelope and encode
    it to json
    '''

    def __init__(self):
        super(JSONEventEncoder, self).__init__()
        self._log = getLogger('system.encoder')

    def encode(self, envelope):
        client = envelope.client
        result = {
            'event_source': 'sproxy',
            'event_class': 'mail',
            'data': {
                'isipv4': True,
                'src_ip': client.get('ip'),
                'src_port': client.get('port'),
                'dst_ip': None,
                'dst_port': None,
                'helo': client.get('name'),
                'mailfrom': envelope.sender,
                'rcptto': envelope.recipients,
                'data': envelope.raw_data,
            }
        }

        self._log.important('event emitted')
        self._log.info(dumps(result, indent=4, sort_keys=True))
        return dumps(result)


class Validator(SmtpValidators):

    def __init__(self, hostname, session):
        super(Validator, self).__init__(session)
        self._hostname = hostname

    def handle_banner(self, reply, address):
        reply.message = self._hostname

    def handle_have_data(self, reply, data):
        '''
        validate the received message data.
        '''
        self.session.envelope.raw_data = data
        self.session.envelope.client['port'] = self.session.address[1]
#
# class NonparsingEnvelope(Envelope):
#     pass


def instantiatePipeline(portList):
    '''
    instantiate the publishing pipeline
    '''
    # relay = RedisPublisherRelay('redis://localhost', 'mails')
    relay = RedisQueueRelay('redis://localhost', 'mail-queue')
    relay.set_encoder(JSONEventEncoder())
    queue = ProxyQueue(relay)

    # create policies here

#     def mailMethod(self, reply, address, params):
#         self._call_validator('mail', reply, address, params)
#         if reply.code == '250':
#             self.envelope = NonparsingEnvelope(sender=address)

#    SmtpSession.MAIL = mailMethod

    def validator_factory(session):
        hostname = 'betamax ESMTP Postfix (Debian/GNU)'
        return Validator(hostname, session)

    for port in portList:
        edge = SmtpEdge(
            ('', port), queue, validator_class=validator_factory,
            max_size=10 * 1024 * 1024)
        edge.start()


def parseArguments():
    '''
    checks that all required arguments are given and return all arguments found
    '''
    parser = ArgumentParser(
        description='a configurable lightweight MTA'
    )
    parser.add_argument(
        '-f', '--logconf', nargs='?', default=None, type=str,
        help='the place where the system can find the log configuration')
    parser.add_argument(
        '-p', '--port', nargs='+', default=[2525], type=int,
        help='a port to bind to')

    return parser.parse_args()


def configureLogger(conf):
    from logging import _levelNames, Logger
    # create the IMPORTANT log level
    _levelNames['IMPORTANT'] = 25
    _levelNames[25] = 'IMPORTANT'
    # add the important method to Logger

    def important(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'IMPORTANT'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        if self.isEnabledFor(25):
            self._log(25, msg, args, **kwargs)

    Logger.important = important

    try:
        fd = StringIO(DEFAULT_LOGGER_CONF)
        dictConfig(load(fd))
        fd.close()
    except:
        basicConfig(level=DEBUG)
        getLogger('log').error('config', exc_info=True)


def main():
    args = parseArguments()
    configureLogger(args.logconf)
    instantiatePipeline(args.port)

    try:
        Event().wait()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
