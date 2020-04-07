# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Chris Caron <lead2gold@gmail.com>
# All rights reserved.
#
# This code is licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CON

# This Plugin assues you have a OpenPush API set up:
#  - https://gitlab.com/Bubu/pushserver/blob/master/openapi.yml

import six
import requests
from json import dumps

from .NotifyBase import NotifyBase
from ..URLBase import PrivacyMode
from ..common import NotifyType
from ..utils import validate_regex
from ..AppriseLocale import gettext_lazy as _


# Priorities
class OpenPushPriority(object):
    NORMAL = "normal"
    HIGH = "high"


OPENPUSH_PRIORITIES = (
    OpenPushPriority.NORMAL,
    OpenPushPriority.HIGH,
)


class NotifyOpenPush(NotifyBase):
    """
    A wrapper for OpenPush Notifications
    """

    # The default descriptive name associated with the Notification
    service_name = 'OpenPush'

    # The services URL
    service_url = 'https://bubu1.eu/openpush/'

    # Insecure protocol (for those self hosted requests)
    protocol = 'opush'

    # The default protocol (this is secure for notica)
    secure_protocol = 'opushs'

    # A URL that takes you to the setup/help of the specific protocol
    setup_url = 'https://github.com/caronc/apprise/wiki/Notify_openpush'

    # Message time to live (if remote client isn't around to receive it)
    time_to_live = 2419200

    # Define object templates
    templates = (
        '{schema}://{host}/{token}',
        '{schema}://{host}:{port}/{token}',
        '{schema}://{user}@{host}/{token}',
        '{schema}://{user}@{host}:{port}/{token}',
        '{schema}://{user}:{password}@{host}/{token}',
        '{schema}://{user}:{password}@{host}:{port}/{token}',
    )

    # Define our template tokens
    template_tokens = dict(NotifyBase.template_tokens, **{
        'token': {
            'name': _('Token'),
            'type': 'string',
            'private': True,
            'required': True,
            'regex': (r'^([0-9a-z]+)$', 'i')
        },
        'host': {
            'name': _('Hostname'),
            'type': 'string',
            'required': True,
        },
        'port': {
            'name': _('Port'),
            'type': 'int',
            'min': 1,
            'max': 65535,
        },
        'user': {
            'name': _('Username'),
            'type': 'string',
        },
        'password': {
            'name': _('Password'),
            'type': 'string',
            'private': True,
        },
    })

    # Define our template arguments
    template_args = dict(NotifyBase.template_args, **{
        'priority': {
            'name': _('Priority'),
            'type': 'choice:string',
            'values': OPENPUSH_PRIORITIES,
            'default': OpenPushPriority.NORMAL,
        },
    })

    # Define any kwargs we're using
    template_kwargs = {
        'headers': {
            'name': _('HTTP Header'),
            'prefix': '+',
        },
    }

    def __init__(self, token, priority=None, headers=None, **kwargs):
        """
        Initialize OpenPush Object
        """
        super(NotifyOpenPush, self).__init__(**kwargs)

        # Token (associated with project)
        self.token = validate_regex(token)
        if not self.token:
            msg = 'An invalid OpenPush Token ' \
                  '({}) was specified.'.format(token)
            self.logger.warning(msg)
            raise TypeError(msg)

        # The priority of the message
        if priority not in OPENPUSH_PRIORITIES:
            self.priority = self.template_args['priority']['default']

        else:
            self.priority = priority

        # prepare our fullpath
        self.fullpath = kwargs.get('fullpath')
        if not isinstance(self.fullpath, six.string_types):
            self.fullpath = '/'

        self.headers = {}
        if headers:
            # Store our extra headers
            self.headers.update(headers)

        return

    def send(self, body, title='', notify_type=NotifyType.INFO, **kwargs):
        """
        Perform OpenPush Notification
        """

        headers = {
            'User-Agent': self.app_id,
            'Content-Type': 'application/json'
        }

        # Prepare our payload
        payload = {
            "token": self.token,
            "data": {
                "title": title,
                "body": body,
            },
            "priority": self.priority,
            "time_to_live": self.time_to_live,
            "collapse_key": "string"
        }

        # Optionally specify user/pass for self hosted systems
        auth = None

        if self.user:
            auth = (self.user, self.password)

        # Set our schema
        schema = 'https' if self.secure else 'http'

        # Prepare our notify_url
        notify_url = '%s://%s' % (schema, self.host)
        if isinstance(self.port, int):
            notify_url += ':%d' % self.port

        notify_url += '{fullpath}/message'.format(
            fullpath=self.fullpath.rstrip('/'),
            token=self.token)

        self.logger.debug('OpenPush POST URL: %s (cert_verify=%r)' % (
            notify_url, self.verify_certificate,
        ))
        self.logger.debug('OpenPush Payload: %s' % str(payload))

        # Always call throttle before any remote server i/o is made
        self.throttle()

        try:
            r = requests.post(
                notify_url.format(token=self.token),
                data=dumps(payload),
                headers=headers,
                auth=auth,
                verify=self.verify_certificate,
            )
            if r.status_code != requests.codes.ok:
                # We had a problem
                status_str = \
                    NotifyOpenPush.http_response_code_lookup(r.status_code)

                self.logger.warning(
                    'Failed to send OpenPush notification:'
                    '{}{}error={}.'.format(
                        status_str,
                        ', ' if status_str else '',
                        r.status_code))

                self.logger.debug('Response Details:\r\n{}'.format(r.content))

                # Return; we're done
                return False

            else:
                self.logger.info('Sent OpenPush notification.')

        except requests.RequestException as e:
            self.logger.warning(
                'A Connection error occured sending OpenPush notification.',
            )
            self.logger.debug('Socket Exception: %s' % str(e))

            # Return; we're done
            return False

        return True

    def url(self, privacy=False, *args, **kwargs):
        """
        Returns the URL built dynamically based on specified arguments.
        """

        # Define any arguments set
        args = {
            'format': self.notify_format,
            'overflow': self.overflow_mode,
            'verify': 'yes' if self.verify_certificate else 'no',
            'priority': self.priority,
        }

        # Append our headers into our args
        args.update({'+{}'.format(k): v for k, v in self.headers.items()})

        # Authorization can be used for self-hosted sollutions
        auth = ''

        # Determine Authentication
        if self.user and self.password:
            auth = '{user}:{password}@'.format(
                user=NotifyOpenPush.quote(self.user, safe=''),
                password=self.pprint(
                    self.password, privacy, mode=PrivacyMode.Secret, safe=''),
            )
        elif self.user:
            auth = '{user}@'.format(
                user=NotifyOpenPush.quote(self.user, safe=''),
            )

        default_port = 443 if self.secure else 80

        return '{schema}://{auth}{hostname}{port}{fullpath}{token}/?{args}' \
               .format(
                   schema=self.secure_protocol
                   if self.secure else self.protocol,
                   auth=auth,
                   hostname=NotifyOpenPush.quote(self.host, safe=''),
                   port='' if self.port is None or self.port == default_port
                        else ':{}'.format(self.port),
                   fullpath=NotifyOpenPush.quote(
                       self.fullpath, safe='/'),
                   token=self.pprint(self.token, privacy, safe=''),
                   args=NotifyOpenPush.urlencode(args),
               )

    @staticmethod
    def parse_url(url):
        """
        Parses the URL and returns enough arguments that can allow
        us to substantiate this object.

        """
        results = NotifyBase.parse_url(url, verify_host=False)
        if not results:
            # We're done early as we couldn't load the results
            return results

        # Get unquoted entries
        entries = NotifyOpenPush.split_path(results['fullpath'])
        if not entries:
            # We expected a token at the very least
            # We're done
            results['token'] = None
            return results

        # The last element in the list is our token
        results['token'] = entries.pop()

        # Re-assemble our full path
        results['fullpath'] = \
            '/' if not entries else '/{}/'.format('/'.join(entries))

        # Add our headers that the user can potentially over-ride if they
        # wish to to our returned result set
        results['headers'] = results['qsd-']
        results['headers'].update(results['qsd+'])

        # configure our priority
        priority = \
            results['qsd'].get('priority', results['qsd'].get('priority'))
        if priority and len(priority):
            _map = {
                'n': OpenPushPriority.NORMAL,
                '1': OpenPushPriority.NORMAL,
                'h': OpenPushPriority.HIGH,
                '2': OpenPushPriority.HIGH,
            }

            try:
                # Attempt to index/retrieve our priority
                results['priority'] = _map[priority[0].lower()]

            except KeyError:
                # No priority was set
                pass

        return results
