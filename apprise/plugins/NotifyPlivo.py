# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Chris Caron <lead2gold@gmail.com>
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Create an account https://messagebird.com if you don't already have one
#
# Get your auth_id and auth token from the dashboard here:
#   - https://console.plivo.com/dashboard/
#

import re
import requests

from .NotifyBase import NotifyBase
from ..common import NotifyType
from ..utils import parse_list
from ..utils import validate_regex
from ..AppriseLocale import gettext_lazy as _

# Some Phone Number Detection
IS_PHONE_NO = re.compile(r'^\+?(?P<phone>[0-9\s)(+-]+)\s*$')


class NotifyPlivo(NotifyBase):
    """
    A wrapper for Plivo Notifications
    """

    # The default descriptive name associated with the Notification
    service_name = 'Plivo'

    # The services URL
    service_url = 'https://plivo.com'

    # The default protocol
    secure_protocol = 'plivo'

    # A URL that takes you to the setup/help of the specific protocol
    setup_url = 'https://github.com/caronc/apprise/wiki/Notify_plivo'

    # Plivo uses the http protocol with JSON requests
    notify_url = 'https://api.plivo.com/v1/Account/{auth_id}/Message/'

    # The maximum length of the body
    body_maxlen = 140

    # A title can not be used for SMS Messages.  Setting this to zero will
    # cause any title (if defined) to get placed into the message body.
    title_maxlen = 0

    # Define object templates
    templates = (
        '{schema}://{auth_id}@{token}/{source}',
        '{schema}://{auth_id}@{token}/{source}/{targets}',
    )

    # Define our template tokens
    template_tokens = dict(NotifyBase.template_tokens, **{
        'auth_id': {
            'name': _('Auth ID'),
            'type': 'string',
            'required': True,
            'regex': (r'^[a-z0-9]{25}$', 'i'),
        },
        'token': {
            'name': _('Auth Token'),
            'type': 'string',
            'required': True,
            'regex': (r'^[a-z0-9]{25}$', 'i'),
        },
        'source': {
            'name': _('Source Phone No'),
            'type': 'string',
            'prefix': '+',
            'required': True,
            'regex': (r'^[0-9\s)(+-]+$', 'i'),
        },
        'target_phone': {
            'name': _('Target Phone No'),
            'type': 'string',
            'prefix': '+',
            'regex': (r'^[0-9\s)(+-]+$', 'i'),
            'map_to': 'targets',
        },
        'targets': {
            'name': _('Targets'),
            'type': 'list:string',
        }
    })

    # Define our template arguments
    template_args = dict(NotifyBase.template_args, **{
        'to': {
            'alias_of': 'targets',
        },
        'from': {
            'alias_of': 'source',
        },
    })

    def __init__(self, auth_id, token, source, targets=None, **kwargs):
        """
        Initialize Plivo Object
        """
        super(NotifyPlivo, self).__init__(**kwargs)

        self.auth_id = validate_regex(
            auth_id, *self.template_tokens['auth_id']['regex'])
        if not self.auth_id:
            msg = 'The Plivo authentication ID specified ({}) is ' \
                'invalid.'.format(auth_id)
            self.logger.warning(msg)
            raise TypeError(msg)

        self.token = validate_regex(
            token, *self.template_tokens['token']['regex'])
        if not self.token:
            msg = 'The Plivo authentication token specified ({}) is ' \
                'invalid.'.format(token)
            self.logger.warning(msg)
            raise TypeError(msg)

        result = IS_PHONE_NO.match(source)
        if not result:
            msg = 'The Plivo source specified ({}) is invalid.'\
                .format(source)
            self.logger.warning(msg)
            raise TypeError(msg)

        # Further check our phone # for it's digit count
        result = ''.join(re.findall(r'\d+', result.group('phone')))
        if len(result) < 11 or len(result) > 14:
            msg = 'The Plivo source # specified ({}) is invalid.'\
                .format(source)
            self.logger.warning(msg)
            raise TypeError(msg)

        # Store our source
        self.source = result

        # Parse our targets
        self.targets = list()

        for target in parse_list(targets):
            # Validate targets and drop bad ones:
            result = IS_PHONE_NO.match(target)
            if result:
                # Further check our phone # for it's digit count
                result = ''.join(re.findall(r'\d+', result.group('phone')))
                if len(result) < 11 or len(result) > 14:
                    self.logger.warning(
                        'Dropped invalid phone # '
                        '({}) specified.'.format(target),
                    )
                    continue

                # store valid phone number
                self.targets.append(result)
                continue

            self.logger.warning(
                'Dropped invalid phone # '
                '({}) specified.'.format(target),
            )

    def send(self, body, title='', notify_type=NotifyType.INFO, **kwargs):
        """
        Perform Plivo Notification
        """

        # Prepare our headers
        headers = {
            'User-Agent': self.app_id,
            'Content-Type': 'application/json',
        }

        # Prepare our authentication
        auth = (self.auth_id, self.token)

        # Prepare our payload
        payload = {
            'src': self.source,
            'dst': None,
            'text': body,

        }
        # Create a copy of the targets list
        targets = list(self.targets)

        if len(targets) == 0:
            # No sources specified, use our own phone no
            targets.append(self.source)

        # Prepare our phone no (< delimits more then one)
        payload['recipients'] = '<'.join(self.targets)

        # Some Debug Logging
        self.logger.debug(
            'Plivo POST URL: {} (cert_verify={})'.format(
                self.notify_url, self.verify_certificate))
        self.logger.debug('Plivo Payload: {}' .format(payload))

        # Always call throttle before any remote server i/o is made
        self.throttle()
        try:
            r = requests.post(
                self.notify_url,
                data=payload,
                headers=headers,
                auth=auth,
                verify=self.verify_certificate,
            )

            if r.status_code not in (
                    requests.codes.ok, requests.codes.accepted):
                # We had a problem
                status_str = \
                    NotifyPlivo.http_response_code_lookup(
                        r.status_code)

                self.logger.warning(
                    'Failed to send Plivo notification to {}: '
                    '{}{}error={}.'.format(
                        ','.join(self.targets),
                        status_str,
                        ', ' if status_str else '',
                        r.status_code))

                self.logger.debug(
                    'Response Details:\r\n{}'.format(r.content))

                return False

            else:
                self.logger.info(
                    'Sent Plivo notification to {}.'.format(self.targets))

        except requests.RequestException as e:
            self.logger.warning(
                'A Connection error occured sending Plivo:%s ' % (
                    self.targets) + 'notification.'
            )
            self.logger.debug('Socket Exception: %s' % str(e))

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
        }

        return '{schema}://{auth_id}@{token}/{source}/' \
            '{targets}/?{args}'.format(
                schema=self.secure_protocol,
                auth_id=self.pprint(self.auth_id, privacy, safe=''),
                token=self.pprint(self.token, privacy, safe=''),
                source=self.source,
                targets='/'.join(
                    [NotifyPlivo.quote(x, safe='') for x in self.targets]),
                args=NotifyPlivo.urlencode(args))

    @staticmethod
    def parse_url(url):
        """
        Parses the URL and returns enough arguments that can allow
        us to substantiate this object.

        """

        results = NotifyBase.parse_url(url)

        if not results:
            # We're done early as we couldn't load the results
            return results

        # The Auth ID is in the username field
        results['auth_id'] = NotifyPlivo.unquote(results['user'])

        # The hostname is our authentication key
        results['token'] = NotifyPlivo.unquote(results['host'])

        # Get our entries; split_path() looks after unquoting content for us
        # by default
        results['targets'] = NotifyPlivo.split_path(results['fullpath'])

        try:
            # The first path entry is the source/originator
            results['source'] = results['targets'].pop(0)
        except IndexError:
            # No path specified... this URL is potentially un-parseable; we can
            # hope for a from= entry
            pass

        # Support the 'to' variable so that we can support targets this way too
        # The 'to' makes it easier to use yaml configuration
        if 'to' in results['qsd'] and len(results['qsd']['to']):
            results['targets'] += \
                NotifyPlivo.parse_list(results['qsd']['to'])

        if 'from' in results['qsd'] and len(results['qsd']['from']):
            results['source'] = \
                NotifyPlivo.unquote(results['qsd']['from'])

        return results
