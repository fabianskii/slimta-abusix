
# Change Log

## [Unreleased]

_There are currently no unreleased changes._

## \[[3.0.0][1]\] - 2015-12-19

### Added

- Compatibility with Python 3.3+.
- [Proxy protocol][2] version 1 support on edge services.
- Dependence on [pycares][3] for DNS resolution.
- Support for the `socket_creator` option to control how sockets are created
  during SMTP relaying.
- Support for `ehlo_as` functions to allow custom EHLO logic on each delivery
  attempt.
- Support for a new `handle_queued` callback on SMTP edges, to control the reply
  code and message based on queue results.

### Removed

- Compatibility with Python 2.6.x.
- Dependence on [dnspython][4] for DNS resolution.

### Fixed

- During SMTP relaying, timeouts and other errors will more consistently return
  the current SMTP command where the error happened.
- Setting a reply code to `221` or `421` in an SMTP edge session will now result
  in the connection closing.

[1]: https://github.com/slimta/python-slimta/issues?q=milestone%3A3.0.0
[2]: http://www.haproxy.org/download/1.5/doc/proxy-protocol.txt
[3]: https://github.com/saghul/pycares
[4]: http://www.dnspython.org/