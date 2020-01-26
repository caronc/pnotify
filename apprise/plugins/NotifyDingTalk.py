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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import requests
from json import dumps

from .NotifyBase import NotifyBase
from ..common import NotifyFormat
from ..common import NotifyType
from ..utils import parse_list
from ..utils import validate_regex
from ..AppriseLocale import gettext_lazy as _

# Register at https://dingtalk.com
#   - Download their PC based software as it is the only way you can create
#     a custom robot.  You can create a custom robot per group.  You will
#     be provided an access_token that Apprise will need.

# Syntax:
#  dingtalk://{access_token}/
#  dingtalk://{access_token}/{optional_phone_no}
#  dingtalk://{access_token}/{phone_no_1}/{phone_no_2}/{phone_no_N/

# Some Phone Number Detection
IS_PHONE_NO = re.compile(r'^\+?(?P<phone>[0-9\s)(+-]+)\s*$')


class NotifyDingTalk(NotifyBase):
    """
    A wrapper for DingTalk Notifications
    """

    # The default descriptive name associated with the Notification
    service_name = 'DingTalk'

    # The services URL
    service_url = 'https://www.dingtalk.com/'

    # All notification requests are secure
    secure_protocol = 'dingtalk'

    # A URL that takes you to the setup/help of the specific protocol
    setup_url = 'https://github.com/caronc/apprise/wiki/Notify_dingtalk'

    # DingTalk API
    notify_url = 'https://oapi.dingtalk.com/robot/send?access_token={token}'

    # Do not set title_maxlen as it is set in a property value below
    # since the length varies depending if we are doing a markdown
    # based message or a text based one.
    # title_maxlen = see below @propery defined

    # Define object templates
    templates = (
        '{schema}://{token}/',
        '{schema}://{token}/{targets}/',
    )

    # Define our template tokens
    template_tokens = dict(NotifyBase.template_tokens, **{
        'token': {
            'name': _('Token'),
            'type': 'string',
            'private': True,
            'required': True,
            'regex': (r'^[a-z0-9]+$', 'i'),
        },
        'targets': {
            'name': _('Target Phone No'),
            'type': 'list:string',
        },
    })

    # Define our template arguments
    template_args = dict(NotifyBase.template_args, **{
        'to': {
            'alias_of': 'targets',
        },
    })

    def __init__(self, token, targets=None, **kwargs):
        """
        Initialize DingTalk Object
        """
        super(NotifyDingTalk, self).__init__(**kwargs)

        # Secret Key (associated with project)
        self.token = validate_regex(
            token, *self.template_tokens['token']['regex'])
        if not self.token:
            msg = 'An invalid DingTalk API Token ' \
                  '({}) was specified.'.format(token)
            self.logger.warning(msg)
            raise TypeError(msg)

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

        return

    def send(self, body, title='', notify_type=NotifyType.INFO, **kwargs):
        """
        Perform DingTalk Notification
        """

        payload = {
            'msgtype': 'text',
            'at': {
                'atMobiles': self.targets,
                'isAtAll': False,
            }
        }

        if self.notify_format == NotifyFormat.MARKDOWN:
            payload['markdown'] = {
                'title': title,
                'text': body,
            }

        else:
            payload['text'] = {
                'content': body,
            }

        # Our Notification URL
        notify_url = self.notify_url.format(token=self.token)

        # Prepare our headers
        headers = {
            'User-Agent': self.app_id,
            'Content-Type': 'application/json'
        }

        # Some Debug Logging
        self.logger.debug('DingTalk URL: {} (cert_verify={})'.format(
            notify_url, self.verify_certificate))
        self.logger.debug('DingTalk Payload: {}' .format(payload))

        # Always call throttle before any remote server i/o is made
        self.throttle()

        try:
            r = requests.post(
                notify_url,
                data=dumps(payload),
                headers=headers,
                verify=self.verify_certificate,
            )

            if r.status_code != requests.codes.ok:
                # We had a problem
                status_str = \
                    NotifyDingTalk.http_response_code_lookup(
                        r.status_code)

                self.logger.warning(
                    'Failed to send DingTalk notification: '
                    '{}{}error={}.'.format(
                        status_str,
                        ', ' if status_str else '',
                        r.status_code))

                self.logger.debug(
                    'Response Details:\r\n{}'.format(r.content))
                return False

            else:
                self.logger.info('Sent DingTalk notification.')

        except requests.RequestException as e:
            self.logger.warning(
                'A Connection error occured sending DingTalk '
                'notification.'
            )
            self.logger.debug('Socket Exception: %s' % str(e))
            return False

        return True

    @property
    def title_maxlen(self):
        """
        The title isn't used when not in markdown mode.
        """
        return NotifyBase.title_maxlen \
            if self.notify_format == NotifyFormat.MARKDOWN else 0

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

        return '{schema}://{token}/{targets}/?{args}'.format(
            schema=self.secure_protocol,
            token=self.pprint(self.token, privacy, safe=''),
            targets='/'.join(
                [NotifyDingTalk.quote(x, safe='') for x in self.targets]),
            args=NotifyDingTalk.urlencode(args))

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

        results['token'] = NotifyDingTalk.unquote(results['host'])

        # Get our entries; split_path() looks after unquoting content for us
        # by default
        results['targets'] = NotifyDingTalk.split_path(results['fullpath'])

        # Support the 'to' variable so that we can support targets this way too
        # The 'to' makes it easier to use yaml configuration
        if 'to' in results['qsd'] and len(results['qsd']['to']):
            results['targets'] += \
                NotifyDingTalk.parse_list(results['qsd']['to'])

        return results
