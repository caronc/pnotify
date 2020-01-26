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

import os
import six
import pytest
import requests
import mock
from json import dumps
from random import choice
from string import ascii_uppercase as str_alpha
from string import digits as str_num

from apprise import plugins
from apprise import NotifyType
from apprise import NotifyBase
from apprise import Apprise
from apprise import AppriseAsset
from apprise import AppriseAttachment
from apprise.common import NotifyFormat
from apprise.common import OverflowMode

# Disable logging for a cleaner testing output
import logging
logging.disable(logging.CRITICAL)

# a test UUID we can use
UUID4 = '8b799edf-6f98-4d3a-9be7-2862fb4e5752'

# Some exception handling we'll use
REQUEST_EXCEPTIONS = (
    requests.ConnectionError(
        0, 'requests.ConnectionError() not handled'),
    requests.RequestException(
        0, 'requests.RequestException() not handled'),
    requests.HTTPError(
        0, 'requests.HTTPError() not handled'),
    requests.ReadTimeout(
        0, 'requests.ReadTimeout() not handled'),
    requests.TooManyRedirects(
        0, 'requests.TooManyRedirects() not handled'),
)

# Attachment Directory
TEST_VAR_DIR = os.path.join(os.path.dirname(__file__), 'var')

TEST_URLS = (
    ##################################
    # NotifyBoxcar
    ##################################
    ('boxcar://', {
        # invalid secret key
        'instance': TypeError,
    }),
    # A a bad url
    ('boxcar://:@/', {
        'instance': TypeError,
    }),
    # No secret specified
    ('boxcar://%s' % ('a' * 64), {
        'instance': TypeError,
    }),
    # No access specified (whitespace is trimmed)
    ('boxcar://%%20/%s' % ('a' * 64), {
        'instance': TypeError,
    }),
    # No secret specified (whitespace is trimmed)
    ('boxcar://%s/%%20' % ('a' * 64), {
        'instance': TypeError,
    }),
    # Provide both an access and a secret
    ('boxcar://%s/%s' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'boxcar://a...a/****/',
    }),
    # Test without image set
    ('boxcar://%s/%s?image=True' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
        # don't include an image in Asset by default
        'include_image': False,
    }),
    ('boxcar://%s/%s?image=False' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
    }),
    # our access, secret and device are all 64 characters
    # which is what we're doing here
    ('boxcar://%s/%s/@tag1/tag2///%s/?to=tag3' % (
        'a' * 64, 'b' * 64, 'd' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
    }),
    # An invalid tag
    ('boxcar://%s/%s/@%s' % ('a' * 64, 'b' * 64, 't' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
    }),
    ('boxcar://%s/%s/' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('boxcar://%s/%s/' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('boxcar://%s/%s/' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyClickSend
    ##################################
    ('clicksend://', {
        # We failed to identify any valid authentication
        'instance': TypeError,
    }),
    ('clicksend://:@/', {
        # We failed to identify any valid authentication
        'instance': TypeError,
    }),
    ('clicksend://user:pass@{}/{}/{}'.format('1' * 10, '2' * 15, 'a' * 13), {
        # invalid target numbers; we'll fail to notify anyone
        'instance': plugins.NotifyClickSend,
        'notify_response': False,
    }),
    ('clicksend://user:pass@{}?batch=yes'.format('3' * 14), {
        # valid number
        'instance': plugins.NotifyClickSend,
    }),
    ('clicksend://user:pass@{}?batch=yes&to={}'.format('3' * 14, '6' * 14), {
        # valid number but using the to= variable
        'instance': plugins.NotifyClickSend,
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'clicksend://user:****',
    }),
    ('clicksend://user:pass@{}?batch=no'.format('3' * 14), {
        # valid number - no batch
        'instance': plugins.NotifyClickSend,
    }),
    ('clicksend://user:pass@{}'.format('3' * 14), {
        'instance': plugins.NotifyClickSend,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('clicksend://user:pass@{}'.format('3' * 14), {
        'instance': plugins.NotifyClickSend,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyD7Networks
    ##################################
    ('d7sms://', {
        # We failed to identify any valid authentication
        'instance': TypeError,
    }),
    ('d7sms://:@/', {
        # We failed to identify any valid authentication
        'instance': TypeError,
    }),
    ('d7sms://user:pass@{}/{}/{}'.format('1' * 10, '2' * 15, 'a' * 13), {
        # No valid targets to notify
        'instance': TypeError,
    }),
    ('d7sms://user:pass@{}?batch=yes'.format('3' * 14), {
        # valid number
        'instance': plugins.NotifyD7Networks,
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'd7sms://user:****@',
    }),
    ('d7sms://user:pass@{}?batch=yes'.format('7' * 14), {
        # valid number
        'instance': plugins.NotifyD7Networks,
        # Test what happens if a batch send fails to return a messageCount
        'requests_response_text': {
            'data': {
                'messageCount': 0,
            },
        },
        # Expected notify() response
        'notify_response': False,
    }),
    ('d7sms://user:pass@{}?batch=yes&to={}'.format('3' * 14, '6' * 14), {
        # valid number
        'instance': plugins.NotifyD7Networks,
    }),
    ('d7sms://user:pass@{}?batch=yes&from=apprise'.format('3' * 14), {
        # valid number, utilizing the optional from= variable
        'instance': plugins.NotifyD7Networks,
    }),
    ('d7sms://user:pass@{}?batch=yes&source=apprise'.format('3' * 14), {
        # valid number, utilizing the optional source= variable (same as from)
        'instance': plugins.NotifyD7Networks,
    }),
    ('d7sms://user:pass@{}?priority=invalid'.format('3' * 14), {
        # valid number; invalid priority
        'instance': plugins.NotifyD7Networks,
    }),
    ('d7sms://user:pass@{}?priority=3'.format('3' * 14), {
        # valid number; adjusted priority
        'instance': plugins.NotifyD7Networks,
    }),
    ('d7sms://user:pass@{}?priority=high'.format('3' * 14), {
        # valid number; adjusted priority (string supported)
        'instance': plugins.NotifyD7Networks,
    }),
    ('d7sms://user:pass@{}?batch=no'.format('3' * 14), {
        # valid number - no batch
        'instance': plugins.NotifyD7Networks,
    }),
    ('d7sms://user:pass@{}'.format('3' * 14), {
        'instance': plugins.NotifyD7Networks,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('d7sms://user:pass@{}'.format('3' * 14), {
        'instance': plugins.NotifyD7Networks,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyDingTalk
    ##################################
    ('dingtalk://', {
        # No Access Token specified
        'instance': None,
    }),
    ('dingtalk://a_bd_/', {
        # invalid Access Token
        'instance': TypeError,
    }),
    ('dingtalk://12345678'.format('a' * 8), {
        # access token
        'instance': plugins.NotifyDingTalk,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'dingtalk://1...8',
    }),
    ('dingtalk://{}/{}'.format('a' * 8, '1' * 14), {
        # access token + phone number
        'instance': plugins.NotifyDingTalk,
    }),
    ('dingtalk://{}/{}/invalid'.format('a' * 8, '1' * 3), {
        # access token + 2 invalid phone numbers
        'instance': plugins.NotifyDingTalk,
    }),
    ('dingtalk://{}/?to={}'.format('a' * 8, '1' * 14), {
        # access token + phone number using 'to'
        'instance': plugins.NotifyDingTalk,
    }),
    ('dingtalk://{}?format=markdown'.format('a' * 8), {
        # access token
        'instance': plugins.NotifyDingTalk,
    }),
    ('dingtalk://{}'.format('a' * 8), {
        'instance': plugins.NotifyDingTalk,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('dingtalk://{}'.format('a' * 8), {
        'instance': plugins.NotifyDingTalk,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyDiscord
    ##################################
    ('discord://', {
        'instance': None,
    }),
    # No webhook_token specified
    ('discord://%s' % ('i' * 24), {
        'instance': TypeError,
    }),
    # Provide both an webhook id and a webhook token
    ('discord://%s/%s' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),
    # Provide a temporary username
    ('discord://l2g@%s/%s' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),

    # Enable other options

    # DEPRICATED reference to Thumbnail
    ('discord://%s/%s?format=markdown&footer=Yes&thumbnail=Yes' % (
        'i' * 24, 't' * 64), {
            'instance': plugins.NotifyDiscord,
            'requests_response_code': requests.codes.no_content,

            # Our expected url(privacy=True) startswith() response:
            'privacy_url': 'discord://i...i/t...t/',
    }),
    ('discord://%s/%s?format=markdown&footer=Yes&thumbnail=No' % (
        'i' * 24, 't' * 64), {
            'instance': plugins.NotifyDiscord,
            'requests_response_code': requests.codes.no_content,
    }),

    # thumbnail= is depricated and image= is the proper entry
    ('discord://%s/%s?format=markdown&footer=Yes&image=Yes' % (
        'i' * 24, 't' * 64), {
            'instance': plugins.NotifyDiscord,
            'requests_response_code': requests.codes.no_content,
            # don't include an image by default
            'include_image': False,
    }),
    ('discord://%s/%s?format=markdown&footer=Yes&image=No' % (
        'i' * 24, 't' * 64), {
            'instance': plugins.NotifyDiscord,
            'requests_response_code': requests.codes.no_content,
            # don't include an image by default
            'include_image': True,
    }),
    ('https://discordapp.com/api/webhooks/{}/{}'.format(
        '0' * 10, 'B' * 40), {
            # Native URL Support, take the discord URL and still build from it
            'instance': plugins.NotifyDiscord,
            'requests_response_code': requests.codes.no_content,
    }),
    ('https://discordapp.com/api/webhooks/{}/{}?footer=yes'.format(
        '0' * 10, 'B' * 40), {
            # Native URL Support with arguments
            'instance': plugins.NotifyDiscord,
            'requests_response_code': requests.codes.no_content,
    }),
    ('discord://%s/%s?format=markdown&avatar=No&footer=No' % (
        'i' * 24, 't' * 64), {
            'instance': plugins.NotifyDiscord,
            'requests_response_code': requests.codes.no_content,
    }),
    # different format support
    ('discord://%s/%s?format=markdown' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),
    ('discord://%s/%s?format=text' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),
    # Test without image set
    ('discord://%s/%s' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
        # don't include an image by default
        'include_image': False,
    }),
    # An invalid url
    ('discord://:@/', {
        'instance': None,
    }),
    ('discord://%s/%s/' % ('a' * 24, 'b' * 64), {
        'instance': plugins.NotifyDiscord,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('discord://%s/%s/' % ('a' * 24, 'b' * 64), {
        'instance': plugins.NotifyDiscord,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('discord://%s/%s/' % ('a' * 24, 'b' * 64), {
        'instance': plugins.NotifyDiscord,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyEmby
    ##################################
    # Insecure Request; no hostname specified
    ('emby://', {
        'instance': None,
    }),
    # Secure Emby Request; no hostname specified
    ('embys://', {
        'instance': None,
    }),
    # No user specified
    ('emby://localhost', {
        # Missing a username
        'instance': TypeError,
    }),
    ('emby://:@/', {
        'instance': None,
    }),
    # Valid Authentication
    ('emby://l2g@localhost', {
        'instance': plugins.NotifyEmby,
        # our response will be False because our authentication can't be
        # tested very well using this matrix.  It will resume in
        # in test_notify_emby_plugin()
        'response': False,
    }),
    ('embys://l2g:password@localhost', {
        'instance': plugins.NotifyEmby,
        # our response will be False because our authentication can't be
        # tested very well using this matrix.  It will resume in
        # in test_notify_emby_plugin()
        'response': False,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'embys://l2g:****@localhost',
    }),
    # The rest of the emby tests are in test_notify_emby_plugin()

    ##################################
    # NotifyEnigma2
    ##################################
    ('enigma2://:@/', {
        'instance': None,
    }),
    ('enigma2://', {
        'instance': None,
    }),
    ('enigma2s://', {
        'instance': None,
    }),
    ('enigma2://localhost', {
        'instance': plugins.NotifyEnigma2,
        # This will fail because we're also expecting a server acknowledgement
        'notify_response': False,
    }),
    ('enigma2://localhost', {
        'instance': plugins.NotifyEnigma2,
        # invalid JSON response
        'requests_response_text': '{',
        'notify_response': False,
    }),
    ('enigma2://localhost', {
        'instance': plugins.NotifyEnigma2,
        # False is returned
        'requests_response_text': {
            'result': False
        },
        'notify_response': False,
    }),
    ('enigma2://localhost', {
        'instance': plugins.NotifyEnigma2,
        # With the right content, this will succeed
        'requests_response_text': {
            'result': True
        }
    }),
    ('enigma2://user@localhost', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        }
    }),
    # Set timeout
    ('enigma2://user@localhost?timeout=-1', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        }
    }),
    # Set timeout
    ('enigma2://user@localhost?timeout=-1000', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        }
    }),
    # Set invalid timeout (defaults to a set value)
    ('enigma2://user@localhost?timeout=invalid', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        }
    }),
    ('enigma2://user:pass@localhost', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'enigma2://user:****@localhost',
    }),
    ('enigma2://localhost:8080', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
    }),
    ('enigma2://user:pass@localhost:8080', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
    }),
    ('enigma2s://localhost', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
    }),
    ('enigma2s://user:pass@localhost', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'enigma2s://user:****@localhost',
    }),
    ('enigma2s://localhost:8080/path/', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'enigma2s://localhost:8080/path/',
    }),
    ('enigma2s://user:pass@localhost:8080', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
    }),
    ('enigma2://localhost:8080/path?-HeaderKey=HeaderValue', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
    }),
    ('enigma2://user:pass@localhost:8081', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('enigma2://user:pass@localhost:8082', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('enigma2://user:pass@localhost:8083', {
        'instance': plugins.NotifyEnigma2,
        'requests_response_text': {
            'result': True
        },
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyFaast
    ##################################
    ('faast://', {
        'instance': None,
    }),
    # Auth Token specified
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'faast://a...a',
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # don't include an image by default
        'include_image': False,
    }),
    ('faast://:@/', {
        'instance': None,
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyFlock
    ##################################
    # No token specified
    ('flock://', {
        'instance': None,
    }),
    # Provide a token
    ('flock://%s' % ('t' * 24), {
        'instance': plugins.NotifyFlock,
    }),
    # Image handling
    ('flock://%s?image=True' % ('t' * 24), {
        'instance': plugins.NotifyFlock,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'flock://t...t',
    }),
    ('flock://%s?image=False' % ('t' * 24), {
        'instance': plugins.NotifyFlock,
    }),
    ('flock://%s?image=True' % ('t' * 24), {
        'instance': plugins.NotifyFlock,
        # Run test when image is set to True, but one couldn't actually be
        # loaded from the Asset Object.
        'include_image': False,
    }),
    # Test to=
    ('flock://%s?to=u:%s&format=markdown' % ('i' * 24, 'u' * 12), {
        'instance': plugins.NotifyFlock,
    }),
    # Provide markdown format
    ('flock://%s?format=markdown' % ('i' * 24), {
        'instance': plugins.NotifyFlock,
    }),
    # Provide text format
    ('flock://%s?format=text' % ('i' * 24), {
        'instance': plugins.NotifyFlock,
    }),
    # Native URL Support, take the slack URL and still build from it
    ('https://api.flock.com/hooks/sendMessage/{}/'.format('i' * 24), {
        'instance': plugins.NotifyFlock,
    }),
    # Native URL Support with arguments
    ('https://api.flock.com/hooks/sendMessage/{}/?format=markdown'.format(
        'i' * 24), {
        'instance': plugins.NotifyFlock,
    }),
    # Bot API presumed if one or more targets are specified
    # Provide markdown format
    ('flock://%s/u:%s?format=markdown' % ('i' * 24, 'u' * 12), {
        'instance': plugins.NotifyFlock,
    }),
    # Bot API presumed if one or more targets are specified
    # Provide text format
    ('flock://%s/u:%s?format=html' % ('i' * 24, 'u' * 12), {
        'instance': plugins.NotifyFlock,
    }),
    # Bot API presumed if one or more targets are specified
    # u: is optional
    ('flock://%s/%s?format=text' % ('i' * 24, 'u' * 12), {
        'instance': plugins.NotifyFlock,
    }),
    # Bot API presumed if one or more targets are specified
    # Multi-entries
    ('flock://%s/g:%s/u:%s?format=text' % ('i' * 24, 'g' * 12, 'u' * 12), {
        'instance': plugins.NotifyFlock,
    }),
    # Bot API presumed if one or more targets are specified
    # Multi-entries using @ for user and # for channel
    ('flock://%s/#%s/@%s?format=text' % ('i' * 24, 'g' * 12, 'u' * 12), {
        'instance': plugins.NotifyFlock,
    }),
    # Bot API presumed if one or more targets are specified
    # has bad entry
    ('flock://%s/g:%s/u:%s?format=text' % ('i' * 24, 'g' * 12, 'u' * 10), {
        'instance': plugins.NotifyFlock,
    }),
    # Invalid user/group defined
    ('flock://%s/g:/u:?format=text' % ('i' * 24), {
        'instance': TypeError,
    }),
    # we don't focus on the invalid length of the user/group fields.
    # As a result, the following will load and pass the data upstream
    ('flock://%s/g:%s/u:%s?format=text' % ('i' * 24, 'g' * 14, 'u' * 10), {
        # We will still instantiate the object
        'instance': plugins.NotifyFlock,
    }),
    # An invalid url
    ('flock://:@/', {
        'instance': None,
    }),
    # Error Testing
    ('flock://%s/g:%s/u:%s?format=text' % ('i' * 24, 'g' * 12, 'u' * 10), {
        'instance': plugins.NotifyFlock,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('flock://%s/' % ('t' * 24), {
        'instance': plugins.NotifyFlock,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('flock://%s/' % ('t' * 24), {
        'instance': plugins.NotifyFlock,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('flock://%s/' % ('t' * 24), {
        'instance': plugins.NotifyFlock,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyGitter
    ##################################
    ('gitter://', {
        'instance': None,
    }),
    ('gitter://:@/', {
        'instance': None,
    }),
    # Invalid Token Length
    ('gitter://%s' % ('a' * 12), {
        'instance': TypeError,
    }),
    # Token specified but no channel
    ('gitter://%s' % ('a' * 40), {
        'instance': TypeError,
    }),
    # Token + channel
    ('gitter://%s/apprise' % ('b' * 40), {
        'instance': plugins.NotifyGitter,
        'response': False,
    }),
    # include image in post
    ('gitter://%s/apprise?image=Yes' % ('c' * 40), {
        'instance': plugins.NotifyGitter,
        'response': False,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'gitter://c...c/apprise',
    }),
    # Don't include image in post (this is the default anyway)
    ('gitter://%s/apprise?image=Yes' % ('d' * 40), {
        'instance': plugins.NotifyGitter,
        'response': False,
        # don't include an image by default
        'include_image': False,
    }),
    # Don't include image in post (this is the default anyway)
    ('gitter://%s/apprise?image=No' % ('e' * 40), {
        'instance': plugins.NotifyGitter,
        'response': False,
    }),
    ('gitter://%s/apprise' % ('f' * 40), {
        'instance': plugins.NotifyGitter,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('gitter://%s/apprise' % ('g' * 40), {
        'instance': plugins.NotifyGitter,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('gitter://%s/apprise' % ('h' * 40), {
        'instance': plugins.NotifyGitter,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyGotify
    ##################################
    ('gotify://', {
        'instance': None,
    }),
    # No token specified
    ('gotify://hostname', {
        'instance': TypeError,
    }),
    # Provide a hostname and token
    ('gotify://hostname/%s' % ('t' * 16), {
        'instance': plugins.NotifyGotify,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'gotify://hostname/t...t',
    }),
    # Provide a priority
    ('gotify://hostname/%s?priority=high' % ('i' * 16), {
        'instance': plugins.NotifyGotify,
    }),
    # Provide an invalid priority
    ('gotify://hostname:8008/%s?priority=invalid' % ('i' * 16), {
        'instance': plugins.NotifyGotify,
    }),
    # An invalid url
    ('gotify://:@/', {
        'instance': None,
    }),
    ('gotify://hostname/%s/' % ('t' * 16), {
        'instance': plugins.NotifyGotify,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('gotifys://localhost/%s/' % ('t' * 16), {
        'instance': plugins.NotifyGotify,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('gotify://localhost/%s/' % ('t' * 16), {
        'instance': plugins.NotifyGotify,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyIFTTT - If This Than That
    ##################################
    ('ifttt://', {
        'instance': None,
    }),
    # No User
    ('ifttt://EventID/', {
        'instance': TypeError,
    }),
    ('ifttt://:@/', {
        'instance': None,
    }),
    # A nicely formed ifttt url with 1 event and a new key/value store
    ('ifttt://WebHookID@EventID/?+TemplateKey=TemplateVal', {
        'instance': plugins.NotifyIFTTT,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'ifttt://W...D',
    }),
    # Test to= in which case we set the host to the webhook id
    ('ifttt://WebHookID?to=EventID,EventID2', {
        'instance': plugins.NotifyIFTTT,
    }),
    # Removing certain keys:
    ('ifttt://WebHookID@EventID/?-Value1=&-Value2', {
        'instance': plugins.NotifyIFTTT,
    }),
    # A nicely formed ifttt url with 2 events defined:
    ('ifttt://WebHookID@EventID/EventID2/', {
        'instance': plugins.NotifyIFTTT,
    }),
    # Support Native URL references
    ('https://maker.ifttt.com/use/WebHookID/', {
        # No EventID specified
        'instance': TypeError,
    }),
    ('https://maker.ifttt.com/use/WebHookID/EventID/', {
        'instance': plugins.NotifyIFTTT,
    }),
    #  Native URL with arguments
    ('https://maker.ifttt.com/use/WebHookID/EventID/?-Value1=', {
        'instance': plugins.NotifyIFTTT,
    }),
    # Test website connection failures
    ('ifttt://WebHookID@EventID', {
        'instance': plugins.NotifyIFTTT,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('ifttt://WebHookID@EventID', {
        'instance': plugins.NotifyIFTTT,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('ifttt://WebHookID@EventID', {
        'instance': plugins.NotifyIFTTT,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyJoin
    ##################################
    ('join://', {
        'instance': None,
    }),
    # APIkey; no device
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
    }),
    # API Key + device (using to=)
    ('join://%s?to=%s' % ('a' * 32, 'd' * 32), {
        'instance': plugins.NotifyJoin,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'join://a...a/',
    }),
    # API Key + priority setting
    ('join://%s?priority=high' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
    }),
    # API Key + invalid priority setting
    ('join://%s?priority=invalid' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
    }),
    # API Key + priority setting (empty)
    ('join://%s?priority=' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
    }),
    # API Key + device
    ('join://%s@%s?image=True' % ('a' * 32, 'd' * 32), {
        'instance': plugins.NotifyJoin,
    }),
    # No image
    ('join://%s@%s?image=False' % ('a' * 32, 'd' * 32), {
        'instance': plugins.NotifyJoin,
    }),
    # API Key + invalid device
    ('join://%s/%s' % ('a' * 32, 'k' * 12), {
        'instance': TypeError,
    }),
    # API Key + device
    ('join://%s/%s' % ('a' * 32, 'd' * 32), {
        'instance': plugins.NotifyJoin,
        # don't include an image by default
        'include_image': False,
    }),
    # API Key + 2 devices
    ('join://%s/%s/%s' % ('a' * 32, 'd' * 32, 'e' * 32), {
        'instance': plugins.NotifyJoin,
        # don't include an image by default
        'include_image': False,
    }),
    # API Key + 1 device and 1 group
    ('join://%s/%s/%s' % ('a' * 32, 'd' * 32, 'group.chrome'), {
        'instance': plugins.NotifyJoin,
    }),
    # API Key + bad url
    ('join://:@/', {
        'instance': None,
    }),
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyJSON
    ##################################
    ('json://:@/', {
        'instance': None,
    }),
    ('json://', {
        'instance': None,
    }),
    ('jsons://', {
        'instance': None,
    }),
    ('json://localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://user:pass@localhost', {
        'instance': plugins.NotifyJSON,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'json://user:****@localhost',
    }),
    ('json://user@localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://localhost:8080', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://user:pass@localhost:8080', {
        'instance': plugins.NotifyJSON,
    }),
    ('jsons://localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('jsons://user:pass@localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('jsons://localhost:8080/path/', {
        'instance': plugins.NotifyJSON,
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'jsons://localhost:8080/path/',
    }),
    ('jsons://user:password@localhost:8080', {
        'instance': plugins.NotifyJSON,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'jsons://user:****@localhost:8080',
    }),
    ('json://localhost:8080/path?-HeaderKey=HeaderValue', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://user:pass@localhost:8081', {
        'instance': plugins.NotifyJSON,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('json://user:pass@localhost:8082', {
        'instance': plugins.NotifyJSON,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('json://user:pass@localhost:8083', {
        'instance': plugins.NotifyJSON,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyKODI
    ##################################
    ('kodi://', {
        'instance': None,
    }),
    ('kodis://', {
        'instance': None,
    }),
    ('kodi://localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodi://user:pass@localhost', {
        'instance': plugins.NotifyXBMC,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'kodi://user:****@localhost',
    }),
    ('kodi://localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodi://user:pass@localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://user:pass@localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://localhost:8080/path/', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://user:password@localhost:8080', {
        'instance': plugins.NotifyXBMC,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'kodis://user:****@localhost:8080',
    }),
    ('kodi://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.WARNING,
    }),
    ('kodi://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.FAILURE,
    }),
    ('kodis://localhost:443', {
        'instance': plugins.NotifyXBMC,
        # don't include an image by default
        'include_image': False,
    }),
    ('kodi://:@/', {
        'instance': None,
    }),
    ('kodi://user:pass@localhost:8081', {
        'instance': plugins.NotifyXBMC,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('kodi://user:pass@localhost:8082', {
        'instance': plugins.NotifyXBMC,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('kodi://user:pass@localhost:8083', {
        'instance': plugins.NotifyXBMC,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyKumulos
    ##################################
    ('kumulos://', {
        # No API or Server Key specified
        'instance': None,
    }),
    ('kumulos://:@/', {
        # No API or Server Key specified
        # We don't have strict host checking on for kumulos, so this URL
        # actually becomes parseable and :@ becomes a hostname.
        # The below errors because a second token wasn't found
        'instance': None,
    }),
    ('kumulos://{}/'.format(UUID4), {
        # No server key was specified
        'instance': TypeError,
    }),
    ('kumulos://{}/{}/'.format(UUID4, 'w' * 36), {
        # Everything is okay
        'instance': plugins.NotifyKumulos,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'kumulos://8...2/w...w/',
    }),
    ('kumulos://{}/{}/'.format(UUID4, 'x' * 36), {
        'instance': plugins.NotifyKumulos,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'kumulos://8...2/x...x/',
    }),
    ('kumulos://{}/{}/'.format(UUID4, 'y' * 36), {
        'instance': plugins.NotifyKumulos,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'kumulos://8...2/y...y/',
    }),
    ('kumulos://{}/{}/'.format(UUID4, 'z' * 36), {
        'instance': plugins.NotifyKumulos,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMailgun
    ##################################
    ('mailgun://', {
        'instance': None,
    }),
    ('mailgun://:@/', {
        'instance': None,
    }),
    # No Token specified
    ('mailgun://user@host', {
        'instance': TypeError,
    }),
    # Token is valid, but no user name specified
    ('mailgun://host/{}-{}-{}'.format('a' * 32, 'b' * 8, 'c' * 8), {
        'instance': TypeError,
    }),
    # Invalid from email address
    ('mailgun://!@host/{}-{}-{}'.format('a' * 32, 'b' * 8, 'c' * 8), {
        'instance': TypeError,
    }),
    # No To email address, but everything else is valid
    ('mailgun://user@host/{}-{}-{}'.format('a' * 32, 'b' * 8, 'c' * 8), {
        'instance': plugins.NotifyMailgun,
    }),
    # valid url with region specified (case insensitve)
    ('mailgun://user@host/{}-{}-{}?region=uS'.format(
        'a' * 32, 'b' * 8, 'c' * 8), {
            'instance': plugins.NotifyMailgun,
    }),
    # valid url with region specified (case insensitve)
    ('mailgun://user@host/{}-{}-{}?region=EU'.format(
        'a' * 32, 'b' * 8, 'c' * 8), {
            'instance': plugins.NotifyMailgun,
    }),
    # invalid url with region specified (case insensitve)
    ('mailgun://user@host/{}-{}-{}?region=invalid'.format(
        'a' * 32, 'b' * 8, 'c' * 8), {
            'instance': TypeError,
    }),
    # One To Email address
    ('mailgun://user@host/{}-{}-{}/test@example.com'.format(
        'a' * 32, 'b' * 8, 'c' * 8), {
            'instance': plugins.NotifyMailgun,
    }),
    ('mailgun://user@host/{}-{}-{}?to=test@example.com'.format(
        'a' * 32, 'b' * 8, 'c' * 8), {
            'instance': plugins.NotifyMailgun,
    }),
    # One To Email address, a from name specified too
    ('mailgun://user@host/{}-{}-{}/test@example.com?name="Frodo"'.format(
        'a' * 32, 'b' * 8, 'c' * 8), {
            'instance': plugins.NotifyMailgun,
    }),
    ('mailgun://user@host/{}-{}-{}'.format('a' * 32, 'b' * 8, 'c' * 8), {
        'instance': plugins.NotifyMailgun,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('mailgun://user@host/{}-{}-{}'.format('a' * 32, 'b' * 8, 'c' * 8), {
        'instance': plugins.NotifyMailgun,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('mailgun://user@host/{}-{}-{}'.format('a' * 32, 'b' * 8, 'c' * 8), {
        'instance': plugins.NotifyMailgun,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMatrix
    ##################################
    ('matrix://', {
        'instance': None,
    }),
    ('matrixs://', {
        'instance': None,
    }),
    ('matrix://localhost?mode=off', {
        # treats it as a anonymous user to register
        'instance': plugins.NotifyMatrix,
        # response is false because we have nothing to notify
        'response': False,
    }),
    ('matrix://localhost', {
        # response is TypeError because we'll try to initialize as
        # a t2bot and fail (localhost is too short of a api key)
        'instance': TypeError
    }),
    ('matrix://user:pass@localhost/#room1/#room2/#room3', {
        'instance': plugins.NotifyMatrix,
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('matrix://user:pass@localhost/#room1/#room2/!room1', {
        'instance': plugins.NotifyMatrix,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('matrix://user:pass@localhost:1234/#room', {
        'instance': plugins.NotifyMatrix,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'matrix://user:****@localhost:1234/',
    }),

    # Matrix supports webhooks too; the following tests this now:
    ('matrix://user:token@localhost?mode=matrix&format=text', {
        # user and token correctly specified with webhook
        'instance': plugins.NotifyMatrix,
        'response': False,
    }),
    ('matrix://user:token@localhost?mode=matrix&format=html', {
        # user and token correctly specified with webhook
        'instance': plugins.NotifyMatrix,
    }),
    ('matrix://user:token@localhost?mode=slack&format=text', {
        # user and token correctly specified with webhook
        'instance': plugins.NotifyMatrix,
    }),
    # Legacy (depricated) webhook reference
    ('matrix://user:token@localhost?webhook=matrix&format=text', {
        # user and token correctly specified with webhook
        'instance': plugins.NotifyMatrix,
        'response': False,
    }),
    ('matrix://user:token@localhost?webhook=matrix&format=html', {
        # user and token correctly specified with webhook
        'instance': plugins.NotifyMatrix,
    }),
    ('matrix://user:token@localhost?webhook=slack&format=text', {
        # user and token correctly specified with webhook
        'instance': plugins.NotifyMatrix,
    }),
    ('matrixs://user:token@localhost?mode=SLACK&format=markdown', {
        # user and token specified; slack webhook still detected
        # despite uppercase characters
        'instance': plugins.NotifyMatrix,
    }),
    # Image Reference
    ('matrixs://user:token@localhost?mode=slack&format=markdown&image=True', {
        # user and token specified; image set to True
        'instance': plugins.NotifyMatrix,
    }),
    ('matrixs://user:token@localhost?mode=slack&format=markdown&image=False', {
        # user and token specified; image set to True
        'instance': plugins.NotifyMatrix,
    }),
    ('matrixs://user@{}?mode=t2bot&format=markdown&image=True'
     .format('a' * 64), {
         # user and token specified; image set to True
         'instance': plugins.NotifyMatrix}),
    ('matrix://user@{}?mode=t2bot&format=markdown&image=False'
     .format('z' * 64), {
         # user and token specified; image set to True
         'instance': plugins.NotifyMatrix}),
    # This will default to t2bot because no targets were specified and no
    # password
    ('matrixs://{}'.format('c' * 64), {
        'instance': plugins.NotifyMatrix,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
    # Test Native URL
    ('https://webhooks.t2bot.io/api/v1/matrix/hook/{}/'.format('d' * 64), {
        # user and token specified; image set to True
        'instance': plugins.NotifyMatrix,
    }),
    # Legacy (Depricated) image reference
    ('matrixs://user:token@localhost?mode=slack&thumbnail=False', {
        # user and token specified; image set to True
        'instance': plugins.NotifyMatrix,
    }),
    ('matrixs://user:token@localhost?mode=slack&thumbnail=True', {
        # user and token specified; image set to True
        'instance': plugins.NotifyMatrix,
    }),
    ('matrix://user:token@localhost?mode=On', {
        # invalid webhook specified (unexpected boolean)
        'instance': TypeError,
    }),
    ('matrix://token@localhost/?mode=Matrix', {
        'instance': plugins.NotifyMatrix,
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('matrix://user:token@localhost/mode=matrix', {
        'instance': plugins.NotifyMatrix,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('matrix://token@localhost:8080/?mode=slack', {
        'instance': plugins.NotifyMatrix,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
    ('matrix://{}/?mode=t2bot'.format('b' * 64), {
        'instance': plugins.NotifyMatrix,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMatterMost
    ##################################
    ('mmost://', {
        'instance': None,
    }),
    ('mmosts://', {
        'instance': None,
    }),
    ('mmost://:@/', {
        'instance': None,
    }),
    ('mmosts://localhost', {
        # Thrown because there was no webhook id specified
        'instance': TypeError,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://user@localhost/3ccdd113474722377935511fc85d3dd4?channel=test', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://user@localhost/3ccdd113474722377935511fc85d3dd4?to=test', {
        'instance': plugins.NotifyMatterMost,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'mmost://user@localhost/3...4/',
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4'
     '?to=test&image=True', {
         'instance': plugins.NotifyMatterMost}),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4' \
     '?to=test&image=False', {
         'instance': plugins.NotifyMatterMost}),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4' \
     '?to=test&image=True', {
         'instance': plugins.NotifyMatterMost,
         # don't include an image by default
         'include_image': False}),
    ('mmost://localhost:8080/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'mmost://localhost:8080/3...4/',
    }),
    ('mmost://localhost:0/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://localhost:invalid-port/3ccdd113474722377935511fc85d3dd4', {
        'instance': None,
    }),
    ('mmosts://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    # Test our paths
    ('mmosts://localhost/a/path/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmosts://localhost/////3ccdd113474722377935511fc85d3dd4///', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMSTeams
    ##################################
    ('msteams://', {
        # First API Token not specified
        'instance': TypeError,
    }),
    ('msteams://:@/', {
        # We don't have strict host checking on for msteams, so this URL
        # actually becomes parseable and :@ becomes a hostname.
        # The below errors because a second token wasn't found
        'instance': TypeError,
    }),
    ('msteams://{}'.format(UUID4), {
        # Just half of one token 1 provided
        'instance': TypeError,
    }),
    ('msteams://{}@{}/'.format(UUID4, UUID4), {
        # Just 1 tokens provided
        'instance': TypeError,
    }),
    ('msteams://{}@{}/{}'.format(UUID4, UUID4, 'a' * 32), {
        # Just 2 tokens provided
        'instance': TypeError,
    }),
    ('msteams://{}@{}/{}/{}?t1'.format(UUID4, UUID4, 'a' * 32, UUID4), {
        # All tokens provided - we're good
        'instance': plugins.NotifyMSTeams,
    }),
    # Support native URLs
    ('https://outlook.office.com/webhook/{}@{}/IncomingWebhook/{}/{}'
     .format(UUID4, UUID4, 'a' * 32, UUID4), {
         # All tokens provided - we're good
         'instance': plugins.NotifyMSTeams}),

    ('msteams://{}@{}/{}/{}?t2'.format(UUID4, UUID4, 'a' * 32, UUID4), {
        # All tokens provided - we're good
        'instance': plugins.NotifyMSTeams,
        # don't include an image by default
        'include_image': False,
    }),
    ('msteams://{}@{}/{}/{}?image=No'.format(UUID4, UUID4, 'a' * 32, UUID4), {
        # All tokens provided - we're good  no image
        'instance': plugins.NotifyMSTeams,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'msteams://8...2/a...a/8...2/',
    }),
    ('msteams://{}@{}/{}/{}?tx'.format(UUID4, UUID4, 'a' * 32, UUID4), {
        'instance': plugins.NotifyMSTeams,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('msteams://{}@{}/{}/{}?ty'.format(UUID4, UUID4, 'a' * 32, UUID4), {
        'instance': plugins.NotifyMSTeams,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('msteams://{}@{}/{}/{}?tz'.format(UUID4, UUID4, 'a' * 32, UUID4), {
        'instance': plugins.NotifyMSTeams,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyNexmo
    ##################################
    ('nexmo://', {
        # No API Key specified
        'instance': TypeError,
    }),
    ('nexmo://:@/', {
        # invalid Auth key
        'instance': TypeError,
    }),
    ('nexmo://AC{}@12345678'.format('a' * 8), {
        # Just a key provided
        'instance': TypeError,
    }),
    ('nexmo://AC{}:{}@{}'.format('a' * 8, 'b' * 16, '3' * 9), {
        # key and secret provided and from but invalid from no
        'instance': TypeError,
    }),
    ('nexmo://AC{}:{}@{}/?ttl=0'.format('b' * 8, 'c' * 16, '3' * 11), {
        # Invalid ttl defined
        'instance': TypeError,
    }),
    ('nexmo://AC{}:{}@{}'.format('d' * 8, 'e' * 16, 'a' * 11), {
        # Invalid source number
        'instance': TypeError,
    }),
    ('nexmo://AC{}:{}@{}/123/{}/abcd/'.format(
        'f' * 8, 'g' * 16, '3' * 11, '9' * 15), {
        # valid everything but target numbers
        'instance': plugins.NotifyNexmo,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'nexmo://A...f:****@',
    }),
    ('nexmo://AC{}:{}@{}'.format('h' * 8, 'i' * 16, '5' * 11), {
        # using phone no with no target - we text ourselves in
        # this case
        'instance': plugins.NotifyNexmo,
    }),
    ('nexmo://_?key=AC{}&secret={}&from={}'.format(
        'a' * 8, 'b' * 16, '5' * 11), {
        # use get args to acomplish the same thing
        'instance': plugins.NotifyNexmo,
    }),
    ('nexmo://_?key=AC{}&secret={}&source={}'.format(
        'a' * 8, 'b' * 16, '5' * 11), {
        # use get args to acomplish the same thing (use source instead of from)
        'instance': plugins.NotifyNexmo,
    }),
    ('nexmo://_?key=AC{}&secret={}&from={}&to={}'.format(
        'a' * 8, 'b' * 16, '5' * 11, '7' * 13), {
        # use to=
        'instance': plugins.NotifyNexmo,
    }),
    ('nexmo://AC{}:{}@{}'.format('a' * 8, 'b' * 16, '6' * 11), {
        'instance': plugins.NotifyNexmo,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('nexmo://AC{}:{}@{}'.format('a' * 8, 'b' * 16, '6' * 11), {
        'instance': plugins.NotifyNexmo,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyNotica
    ##################################
    ('notica://', {
        'instance': TypeError,
    }),
    ('notica://:@/', {
        'instance': TypeError,
    }),
    # Native URL
    ('https://notica.us/?%s' % ('z' * 6), {
        'instance': plugins.NotifyNotica,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'notica://z...z/',
    }),
    # Native URL with additional arguments
    ('https://notica.us/?%s&overflow=upstream' % ('z' * 6), {
        'instance': plugins.NotifyNotica,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'notica://z...z/',
    }),
    # Token specified
    ('notica://%s' % ('a' * 6), {
        'instance': plugins.NotifyNotica,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'notica://a...a/',
    }),
    # Self-Hosted configuration
    ('notica://localhost/%s' % ('b' * 6), {
        'instance': plugins.NotifyNotica,
    }),
    ('notica://user@localhost/%s' % ('c' * 6), {
        'instance': plugins.NotifyNotica,
    }),
    ('notica://user:pass@localhost/%s/' % ('d' * 6), {
        'instance': plugins.NotifyNotica,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'notica://user:****@localhost/d...d',
    }),
    ('notica://user:pass@localhost/a/path/%s/' % ('r' * 6), {
        'instance': plugins.NotifyNotica,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'notica://user:****@localhost/a/path/r...r',
    }),
    ('notica://localhost:8080/%s' % ('a' * 6), {
        'instance': plugins.NotifyNotica,
    }),
    ('notica://user:pass@localhost:8080/%s' % ('b' * 6), {
        'instance': plugins.NotifyNotica,
    }),
    ('noticas://localhost/%s' % ('j' * 6), {
        'instance': plugins.NotifyNotica,
        'privacy_url': 'noticas://localhost/j...j',
    }),
    ('noticas://user:pass@localhost/%s' % ('e' * 6), {
        'instance': plugins.NotifyNotica,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'noticas://user:****@localhost/e...e',
    }),
    ('noticas://localhost:8080/path/%s' % ('5' * 6), {
        'instance': plugins.NotifyNotica,
        'privacy_url': 'noticas://localhost:8080/path/5...5',
    }),
    ('noticas://user:pass@localhost:8080/%s' % ('6' * 6), {
        'instance': plugins.NotifyNotica,
    }),
    ('notica://%s' % ('b' * 6), {
        'instance': plugins.NotifyNotica,
        # don't include an image by default
        'include_image': False,
    }),
    # Test Header overrides
    ('notica://localhost:8080//%s/?+HeaderKey=HeaderValue' % ('7' * 6), {
        'instance': plugins.NotifyNotica,
    }),
    ('notica://%s' % ('c' * 6), {
        'instance': plugins.NotifyNotica,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('notica://%s' % ('d' * 7), {
        'instance': plugins.NotifyNotica,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('notica://%s' % ('e' * 8), {
        'instance': plugins.NotifyNotica,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyNotifico
    ##################################
    ('notifico://', {
        'instance': None,
    }),
    ('notifico://:@/', {
        'instance': None,
    }),
    ('notifico://1234', {
        # Just a project id provided (no message token)
        'instance': TypeError,
    }),
    ('notifico://abcd/ckhrjW8w672m6HG', {
        # an invalid project id provided
        'instance': TypeError,
    }),
    ('notifico://1234/ckhrjW8w672m6HG', {
        # A project id and message hook provided
        'instance': plugins.NotifyNotifico,
    }),
    ('notifico://1234/ckhrjW8w672m6HG?prefix=no', {
        # Disable our prefix
        'instance': plugins.NotifyNotifico,
    }),
    ('notifico://1234/ckhrjW8w672m6HG?color=yes', {
        'instance': plugins.NotifyNotifico,
        'notify_type': 'info',
    }),
    ('notifico://1234/ckhrjW8w672m6HG?color=yes', {
        'instance': plugins.NotifyNotifico,
        'notify_type': 'success',
    }),
    ('notifico://1234/ckhrjW8w672m6HG?color=yes', {
        'instance': plugins.NotifyNotifico,
        'notify_type': 'warning',
    }),
    ('notifico://1234/ckhrjW8w672m6HG?color=yes', {
        'instance': plugins.NotifyNotifico,
        'notify_type': 'failure',
    }),
    ('notifico://1234/ckhrjW8w672m6HG?color=yes', {
        'instance': plugins.NotifyNotifico,
        'notify_type': 'invalid',
    }),
    ('notifico://1234/ckhrjW8w672m6HG?color=no', {
        # Test our color flag by having it set to off
        'instance': plugins.NotifyNotifico,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'notifico://1...4/c...G',
    }),
    # Support Native URLs
    ('https://n.tkte.ch/h/2144/uJmKaBW9WFk42miB146ci3Kj', {
        'instance': plugins.NotifyNotifico,
    }),
    ('notifico://1234/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyNotifico,
        # don't include an image by default
        'include_image': False,
    }),
    ('notifico://1234/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyNotifico,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('notifico://1234/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyNotifico,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('notifico://1234/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyNotifico,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyNextcloud
    ##################################
    ('ncloud://:@/', {
        'instance': None,
    }),
    ('ncloud://', {
        'instance': None,
    }),
    ('nclouds://', {
        # No hostname
        'instance': None,
    }),
    ('ncloud://localhost', {
        # No user specified
        'instance': TypeError,
    }),
    ('ncloud://localhost/admin', {
        'instance': plugins.NotifyNextcloud,
    }),
    ('ncloud://user@localhost/admin', {
        'instance': plugins.NotifyNextcloud,
    }),
    ('ncloud://user@localhost?to=user1,user2', {
        'instance': plugins.NotifyNextcloud,
    }),
    ('ncloud://user:pass@localhost/user1/user2', {
        'instance': plugins.NotifyNextcloud,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'ncloud://user:****@localhost/user1/user2',
    }),
    ('ncloud://user:pass@localhost:8080/admin', {
        'instance': plugins.NotifyNextcloud,
    }),
    ('nclouds://user:pass@localhost/admin', {
        'instance': plugins.NotifyNextcloud,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'nclouds://user:****@localhost/admin',
    }),
    ('nclouds://user:pass@localhost:8080/admin/', {
        'instance': plugins.NotifyNextcloud,
    }),
    ('ncloud://localhost:8080/admin?-HeaderKey=HeaderValue', {
        'instance': plugins.NotifyNextcloud,
    }),
    ('ncloud://user:pass@localhost:8081/admin', {
        'instance': plugins.NotifyNextcloud,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('ncloud://user:pass@localhost:8082/admin', {
        'instance': plugins.NotifyNextcloud,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('ncloud://user:pass@localhost:8083/user1/user2/user3', {
        'instance': plugins.NotifyNextcloud,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyProwl
    ##################################
    ('prowl://', {
        'instance': None,
    }),
    # Invalid API Key
    ('prowl://%s' % ('a' * 20), {
        'instance': TypeError,
    }),
    # Provider Key
    ('prowl://%s/%s' % ('a' * 40, 'b' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # Invalid Provider Key
    ('prowl://%s/%s' % ('a' * 40, 'b' * 20), {
        'instance': TypeError,
    }),
    # APIkey; no device
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # API Key
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # don't include an image by default
        'include_image': False,
    }),
    # API Key + priority setting
    ('prowl://%s?priority=high' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # API Key + invalid priority setting
    ('prowl://%s?priority=invalid' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # API Key + priority setting (empty)
    ('prowl://%s?priority=' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # API Key + No Provider Key (empty)
    ('prowl://%s///' % ('w' * 40), {
        'instance': plugins.NotifyProwl,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'prowl://w...w/',
    }),
    # API Key + Provider Key
    ('prowl://%s/%s' % ('a' * 40, 'b' * 40), {
        'instance': plugins.NotifyProwl,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'prowl://a...a/b...b',
    }),
    # API Key + with image
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # bad url
    ('prowl://:@/', {
        'instance': None,
    }),
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyPushBullet
    ##################################
    ('pbul://', {
        'instance': None,
    }),
    ('pbul://:@/', {
        'instance': None,
    }),
    # APIkey
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # APIkey; but support attachment response
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,

        # Test what happens if a batch send fails to return a messageCount
        'requests_response_text': {
            'file_name': 'cat.jpeg',
            'file_type': 'image/jpeg',
            'file_url': 'http://file_url',
            'upload_url': 'http://upload_url',
        },
    }),
    # APIkey; attachment testing that isn't an image type
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,

        # Test what happens if a batch send fails to return a messageCount
        'requests_response_text': {
            'file_name': 'test.pdf',
            'file_type': 'application/pdf',
            'file_url': 'http://file_url',
            'upload_url': 'http://upload_url',
        },
    }),
    # APIkey; attachment testing were expected entry in payload is missing
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,

        # Test what happens if a batch send fails to return a messageCount
        'requests_response_text': {
            'file_name': 'test.pdf',
            'file_type': 'application/pdf',
            'file_url': 'http://file_url',
            # upload_url missing
        },
        # Our Notification calls associated with attachments will fail:
        'attach_response': False,
    }),
    # API Key + channel
    ('pbul://%s/#channel/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # API Key + channel (via to=
    ('pbul://%s/?to=#channel' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # API Key + 2 channels
    ('pbul://%s/#channel1/#channel2' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'pbul://a...a/',
        'check_attachments': False,
    }),
    # API Key + device
    ('pbul://%s/device/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # API Key + 2 devices
    ('pbul://%s/device1/device2/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # API Key + email
    ('pbul://%s/user@example.com/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # API Key + 2 emails
    ('pbul://%s/user@example.com/abc@def.com/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # API Key + Combo
    ('pbul://%s/device/#channel/user@example.com/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        'check_attachments': False,
    }),
    # ,
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
        'check_attachments': False,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
        'check_attachments': False,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
        'check_attachments': False,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
        'check_attachments': False,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
        'check_attachments': False,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
        'check_attachments': False,
    }),

    ##################################
    # NotifyPushSafer
    ##################################
    ('psafer://:@/', {
        'instance': None,
    }),
    ('psafer://', {
        'instance': None,
    }),
    ('psafers://', {
        'instance': None,
    }),
    ('psafer://{}'.format('a' * 20), {
        'instance': plugins.NotifyPushSafer,
        # This will fail because we're also expecting a server acknowledgement
        'notify_response': False,
    }),
    ('psafer://{}'.format('b' * 20), {
        'instance': plugins.NotifyPushSafer,
        # invalid JSON response
        'requests_response_text': '{',
        'notify_response': False,
    }),
    ('psafer://{}'.format('c' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A failure has status set to zero
        # We also expect an 'error' flag to be set
        'requests_response_text': {
            'status': 0,
            'error': 'we failed'
        },
        'notify_response': False,
    }),
    ('psafers://{}'.format('d' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A failure has status set to zero
        # Test without an 'error' flag
        'requests_response_text': {
            'status': 0,
        },
        'notify_response': False,
    }),
    # This will notify all users ('a')
    ('psafer://{}'.format('e' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A status of 1 is a success
        'requests_response_text': {
            'status': 1,
        }
    }),
    # This will notify a selected set of devices
    ('psafer://{}/12/24/53'.format('e' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A status of 1 is a success
        'requests_response_text': {
            'status': 1,
        }
    }),
    # Same as above, but exercises the to= argument
    ('psafer://{}?to=12,24,53'.format('e' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A status of 1 is a success
        'requests_response_text': {
            'status': 1,
        }
    }),
    # Set priority
    ('psafer://{}?priority=emergency'.format('f' * 20), {
        'instance': plugins.NotifyPushSafer,
        'requests_response_text': {
            'status': 1,
        }
    }),
    # Support integer value too
    ('psafer://{}?priority=-1'.format('f' * 20), {
        'instance': plugins.NotifyPushSafer,
        'requests_response_text': {
            'status': 1,
        }
    }),
    # Invalid priority
    ('psafer://{}?priority=invalid'.format('f' * 20), {
        # Invalid Priority
        'instance': TypeError,
    }),
    # Invalid priority
    ('psafer://{}?priority=25'.format('f' * 20), {
        # Invalid Priority
        'instance': TypeError,
    }),
    # Set sound
    ('psafer://{}?sound=ok'.format('g' * 20), {
        'instance': plugins.NotifyPushSafer,
        'requests_response_text': {
            'status': 1,
        }
    }),
    # Support integer value too
    ('psafers://{}?sound=14'.format('g' * 20), {
        'instance': plugins.NotifyPushSafer,
        'requests_response_text': {
            'status': 1,
        },
        'privacy_url': 'psafers://g...g',
    }),
    # Invalid sound
    ('psafer://{}?sound=invalid'.format('h' * 20), {
        # Invalid Sound
        'instance': TypeError,
    }),
    ('psafer://{}?sound=94000'.format('h' * 20), {
        # Invalid Sound
        'instance': TypeError,
    }),
    # Set vibration (integer only)
    ('psafers://{}?vibration=1'.format('h' * 20), {
        'instance': plugins.NotifyPushSafer,
        'requests_response_text': {
            'status': 1,
        },
        'privacy_url': 'psafers://h...h',
    }),
    # Invalid sound
    ('psafer://{}?vibration=invalid'.format('h' * 20), {
        # Invalid Vibration
        'instance': TypeError,
    }),
    # Invalid vibration
    ('psafer://{}?vibration=25000'.format('h' * 20), {
        # Invalid Vibration
        'instance': TypeError,
    }),
    ('psafers://{}'.format('d' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A failure has status set to zero
        # Test without an 'error' flag
        'requests_response_text': {
            'status': 0,
        },

        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('psafer://{}'.format('d' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A failure has status set to zero
        # Test without an 'error' flag
        'requests_response_text': {
            'status': 0,
        },

        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('psafers://{}'.format('d' * 20), {
        'instance': plugins.NotifyPushSafer,
        # A failure has status set to zero
        # Test without an 'error' flag
        'requests_response_text': {
            'status': 0,
        },
        # Throws a series of connection and transfer exceptions when this
        # flag is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyTechulusPush
    ##################################
    ('push://', {
        # Missing API Key
        'instance': TypeError,
    }),
    # Invalid API Key
    ('push://%s' % ('+' * 24), {
        'instance': TypeError,
    }),
    # APIkey
    ('push://%s' % UUID4, {
        'instance': plugins.NotifyTechulusPush,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'push://8...2/',
    }),
    # API Key + bad url
    ('push://:@/', {
        'instance': TypeError,
    }),
    ('push://%s' % UUID4, {
        'instance': plugins.NotifyTechulusPush,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('push://%s' % UUID4, {
        'instance': plugins.NotifyTechulusPush,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('push://%s' % UUID4, {
        'instance': plugins.NotifyTechulusPush,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyPushed
    ##################################
    ('pushed://', {
        'instance': None,
    }),
    # Application Key Only
    ('pushed://%s' % ('a' * 32), {
        'instance': TypeError,
    }),
    # Application Key+Secret
    ('pushed://%s/%s' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
    }),
    # Application Key+Secret + channel
    ('pushed://%s/%s/#channel/' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
    }),
    # Application Key+Secret + channel (via to=)
    ('pushed://%s/%s?to=channel' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'pushed://a...a/****/',
    }),
    # Application Key+Secret + dropped entry
    ('pushed://%s/%s/dropped_value/' % ('a' * 32, 'a' * 64), {
        # No entries validated is a fail
        'instance': TypeError,
    }),
    # Application Key+Secret + 2 channels
    ('pushed://%s/%s/#channel1/#channel2' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
    }),
    # Application Key+Secret + User Pushed ID
    ('pushed://%s/%s/@ABCD/' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
    }),
    # Application Key+Secret + 2 devices
    ('pushed://%s/%s/@ABCD/@DEFG/' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
    }),
    # Application Key+Secret + Combo
    ('pushed://%s/%s/@ABCD/#channel' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
    }),
    # ,
    ('pushed://%s/%s' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('pushed://%s/%s' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pushed://%s/%s' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
    ('pushed://:@/', {
        'instance': None,
    }),
    ('pushed://%s/%s' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('pushed://%s/%s' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pushed://%s/%s/#channel' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pushed://%s/%s/@user' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pushed://%s/%s' % ('a' * 32, 'a' * 64), {
        'instance': plugins.NotifyPushed,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyPushjet
    ##################################
    ('pjet://', {
        'instance': None,
    }),
    ('pjets://', {
        'instance': None,
    }),
    ('pjet://:@/', {
        'instance': None,
    }),
    #  You must specify a secret key
    ('pjet://%s' % ('a' * 32), {
        'instance': TypeError,
    }),
    # Legacy method of logging in (soon to be depricated)
    ('pjet://%s@localhost' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,
    }),
    # The proper way to log in
    ('pjet://user:pass@localhost/%s' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,
    }),
    # The proper way to log in
    ('pjets://localhost/%s' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,
    }),
    # Specify your own server with login (secret= MUST be provided)
    ('pjet://user:pass@localhost?secret=%s' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'pjet://user:****@localhost',
    }),
    # Specify your own server with login (no secret = fail normally)
    # however this will work since we're providing depricated support
    # at this time so the 'user' get's picked up as being the secret_key
    ('pjet://user:pass@localhost', {
        'instance': plugins.NotifyPushjet,
    }),
    # Specify your own server with port
    ('pjets://localhost:8080/%s' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,
    }),
    ('pjets://localhost:8080/%s' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('pjets://localhost:4343/%s' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pjet://localhost:8081/%s' % ('a' * 32), {
        'instance': plugins.NotifyPushjet,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyPushover
    ##################################
    ('pover://', {
        'instance': None,
    }),
    # APIkey; no user
    ('pover://%s' % ('a' * 30), {
        'instance': TypeError,
    }),
    # API Key + invalid sound setting
    ('pover://%s@%s?sound=invalid' % ('u' * 30, 'a' * 30), {
        'instance': TypeError,
    }),
    # API Key + valid alternate sound picked
    ('pover://%s@%s?sound=spacealarm' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + Valid User
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # don't include an image by default
        'include_image': False,
    }),
    # API Key + Valid User + 1 Device
    ('pover://%s@%s/DEVICE' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + Valid User + 1 Device (via to=)
    ('pover://%s@%s?to=DEVICE' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + Valid User + 2 Devices
    ('pover://%s@%s/DEVICE1/DEVICE2/' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'pover://u...u@a...a',
    }),
    # API Key + Valid User + invalid device
    ('pover://%s@%s/%s/' % ('u' * 30, 'a' * 30, 'd' * 30), {
        'instance': plugins.NotifyPushover,
        # Notify will return False since there is a bad device in our list
        'response': False,
    }),
    # API Key + Valid User + device + invalid device
    ('pover://%s@%s/DEVICE1/%s/' % ('u' * 30, 'a' * 30, 'd' * 30), {
        'instance': plugins.NotifyPushover,
        # Notify will return False since there is a bad device in our list
        'response': False,
    }),
    # API Key + priority setting
    ('pover://%s@%s?priority=high' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + invalid priority setting
    ('pover://%s@%s?priority=invalid' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + emergency(2) priority setting
    ('pover://%s@%s?priority=emergency' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + emergency priority setting with retry and expire
    ('pover://%s@%s?priority=emergency&%s&%s' % ('u' * 30,
                                                 'a' * 30,
                                                 'retry=30',
                                                 'expire=300'), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + emergency priority setting with text retry
    ('pover://%s@%s?priority=emergency&%s&%s' % ('u' * 30,
                                                 'a' * 30,
                                                 'retry=invalid',
                                                 'expire=300'), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + emergency priority setting with text expire
    ('pover://%s@%s?priority=emergency&%s&%s' % ('u' * 30,
                                                 'a' * 30,
                                                 'retry=30',
                                                 'expire=invalid'), {
        'instance': plugins.NotifyPushover,
    }),
    # API Key + emergency priority setting with invalid expire
    ('pover://%s@%s?priority=emergency&%s' % ('u' * 30,
                                              'a' * 30,
                                              'expire=100000'), {
        'instance': TypeError,
    }),
    # API Key + emergency priority setting with invalid retry
    ('pover://%s@%s?priority=emergency&%s' % ('u' * 30,
                                              'a' * 30,
                                              'retry=15'), {
        'instance': TypeError,
    }),
    # API Key + priority setting (empty)
    ('pover://%s@%s?priority=' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # bad url
    ('pover://:@/', {
        'instance': None,
    }),
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyRocketChat
    ##################################
    ('rocket://', {
        'instance': None,
    }),
    ('rockets://', {
        'instance': None,
    }),
    ('rocket://:@/', {
        'instance': None,
    }),
    # No username or pass
    ('rocket://localhost', {
        'instance': TypeError,
    }),
    # No room or channel
    ('rocket://user:pass@localhost', {
        'instance': TypeError,
    }),
    # No valid rooms or channels
    ('rocket://user:pass@localhost/#/!/@', {
        'instance': TypeError,
    }),
    # No user/pass combo
    ('rocket://user@localhost/room/', {
        'instance': TypeError,
    }),
    # No user/pass combo
    ('rocket://localhost/room/', {
        'instance': TypeError,
    }),
    # A room and port identifier
    ('rocket://user:pass@localhost:8080/room/', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # A channel (using the to=)
    ('rockets://user:pass@localhost?to=#channel', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # A channel
    ('rockets://user:pass@localhost/#channel', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # Several channels
    ('rocket://user:pass@localhost/#channel1/#channel2/?avatar=No', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # Several Rooms
    ('rocket://user:pass@localhost/room1/room2', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # A room and channel
    ('rocket://user:pass@localhost/room/#channel?mode=basic', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'rocket://user:****@localhost',
    }),
    # A user/pass where the pass matches a webtoken
    # to ensure we get the right mode, we enforce basic mode
    # so that web/token gets interpreted as a password
    ('rockets://user:pass%2Fwithslash@localhost/#channel/?mode=basic', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # A room and channel
    ('rockets://user:pass@localhost/rooma/#channela', {
        # The response text is expected to be the following on a success
        'requests_response_code': requests.codes.ok,
        'requests_response_text': {
            # return something other then a success message type
            'status': 'failure',
        },
        # Exception is thrown in this case
        'instance': plugins.NotifyRocketChat,
        # Notifications will fail in this event
        'response': False,
    }),
    # A web token
    ('rockets://web/token@localhost/@user/#channel/roomid', {
        'instance': plugins.NotifyRocketChat,
    }),
    ('rockets://user:web/token@localhost/@user/?mode=webhook', {
        'instance': plugins.NotifyRocketChat,
    }),
    ('rockets://user:web/token@localhost?to=@user2,#channel2', {
        'instance': plugins.NotifyRocketChat,
    }),
    ('rockets://web/token@localhost/?avatar=No', {
        # a simple webhook token with default values
        'instance': plugins.NotifyRocketChat,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'rockets://w...n@localhost',
    }),
    ('rockets://localhost/@user/?mode=webhook&webhook=web/token', {
        'instance': plugins.NotifyRocketChat,
    }),
    ('rockets://user:web/token@localhost/@user/?mode=invalid', {
        # invalid mode
        'instance': TypeError,
    }),
    ('rocket://user:pass@localhost:8081/room1/room2', {
        'instance': plugins.NotifyRocketChat,
        # force a failure using basic mode
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('rockets://user:web/token@localhost?to=@user3,#channel3', {
        'instance': plugins.NotifyRocketChat,
        # force a failure using webhook mode
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('rocket://user:pass@localhost:8082/#channel', {
        'instance': plugins.NotifyRocketChat,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('rocket://user:pass@localhost:8083/#chan1/#chan2/room', {
        'instance': plugins.NotifyRocketChat,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyRyver
    ##################################
    ('ryver://', {
        'instance': None,
    }),
    ('ryver://:@/', {
        'instance': None,
    }),
    ('ryver://apprise', {
        # Just org provided (no token)
        'instance': TypeError,
    }),
    ('ryver://apprise/ckhrjW8w672m6HG?webhook=invalid', {
        # Invalid webhook provided
        'instance': TypeError,
    }),
    ('ryver://x/ckhrjW8w672m6HG?mode=slack', {
        # Invalid org
        'instance': TypeError,
    }),
    ('ryver://apprise/ckhrjW8w672m6HG?mode=slack', {
        # No username specified; this is still okay as we use whatever
        # the user told the webhook to use; set our slack mode
        'instance': plugins.NotifyRyver,
    }),
    ('ryver://apprise/ckhrjW8w672m6HG?mode=ryver', {
        # No username specified; this is still okay as we use whatever
        # the user told the webhook to use; set our ryver mode
        'instance': plugins.NotifyRyver,
    }),
    # Legacy webhook mode setting:
    # Legacy webhook mode setting:
    ('ryver://apprise/ckhrjW8w672m6HG?webhook=slack', {
        # No username specified; this is still okay as we use whatever
        # the user told the webhook to use; set our slack mode
        'instance': plugins.NotifyRyver,
    }),
    ('ryver://apprise/ckhrjW8w672m6HG?webhook=ryver', {
        # No username specified; this is still okay as we use whatever
        # the user told the webhook to use; set our ryver mode
        'instance': plugins.NotifyRyver,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'ryver://apprise/c...G',
    }),
    # Support Native URLs
    ('https://apprise.ryver.com/application/webhook/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyRyver,
    }),
    # Support Native URLs with arguments
    ('https://apprise.ryver.com/application/webhook/ckhrjW8w672m6HG'
     '?webhook=ryver',
        {
            'instance': plugins.NotifyRyver,
        }),
    ('ryver://caronc@apprise/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyRyver,
        # don't include an image by default
        'include_image': False,
    }),
    ('ryver://apprise/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyRyver,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('ryver://apprise/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyRyver,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('ryver://apprise/ckhrjW8w672m6HG', {
        'instance': plugins.NotifyRyver,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifySendGrid
    ##################################
    ('sendgrid://', {
        'instance': None,
    }),
    ('sendgrid://:@/', {
        'instance': None,
    }),
    ('sendgrid://abcd', {
        # Just an broken email (no api key or email)
        'instance': None,
    }),
    ('sendgrid://abcd@host', {
        # Just an Email specified, no API Key
        'instance': None,
    }),
    ('sendgrid://invalid-api-key+*-d:user@example.com', {
        # An invalid API Key
        'instance': TypeError,
    }),
    ('sendgrid://abcd:user@example.com', {
        # No To/Target Address(es) specified; so we sub in the same From
        # address
        'instance': plugins.NotifySendGrid,
    }),
    ('sendgrid://abcd:user@example.com/newuser@example.com', {
        # A good email
        'instance': plugins.NotifySendGrid,
    }),
    ('sendgrid://abcd:user@example.com/newuser@example.com'
     '?bcc=l2g@nuxref.com', {
         # A good email with Blind Carbon Copy
         'instance': plugins.NotifySendGrid,
     }),
    ('sendgrid://abcd:user@example.com/newuser@example.com'
     '?cc=l2g@nuxref.com', {
         # A good email with Carbon Copy
         'instance': plugins.NotifySendGrid,
     }),
    ('sendgrid://abcd:user@example.com/newuser@example.com'
     '?to=l2g@nuxref.com', {
         # A good email with Carbon Copy
         'instance': plugins.NotifySendGrid,
     }),
    ('sendgrid://abcd:user@example.com/newuser@example.com'
     '?template={}'.format(UUID4), {
         # A good email with a template + no substitutions
         'instance': plugins.NotifySendGrid,
     }),
    ('sendgrid://abcd:user@example.com/newuser@example.com'
     '?template={}&+sub=value&+sub2=value2'.format(UUID4), {
         # A good email with a template + substitutions
         'instance': plugins.NotifySendGrid,

         # Our expected url(privacy=True) startswith() response:
         'privacy_url': 'sendgrid://a...d:user@example.com/',
     }),
    ('sendgrid://abcd:user@example.ca/newuser@example.ca', {
        'instance': plugins.NotifySendGrid,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('sendgrid://abcd:user@example.uk/newuser@example.uk', {
        'instance': plugins.NotifySendGrid,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('sendgrid://abcd:user@example.au/newuser@example.au', {
        'instance': plugins.NotifySendGrid,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifySinch
    ##################################
    ('sinch://', {
        # No Account SID specified
        'instance': TypeError,
    }),
    ('sinch://:@/', {
        # invalid Auth token
        'instance': TypeError,
    }),
    ('sinch://{}@12345678'.format('a' * 32), {
        # Just spi provided
        'instance': TypeError,
    }),
    ('sinch://{}:{}@_'.format('a' * 32, 'b' * 32), {
        # spi and token provided but invalid from
        'instance': TypeError,
    }),
    ('sinch://{}:{}@{}'.format('a' * 32, 'b' * 32, '3' * 5), {
        # using short-code (5 characters) without a target
        # We can still instantiate ourselves with a valid short code
        'instance': TypeError,
    }),
    ('sinch://{}:{}@{}'.format('a' * 32, 'b' * 32, '3' * 9), {
        # spi and token provided and from but invalid from no
        'instance': TypeError,
    }),
    ('sinch://{}:{}@{}/123/{}/abcd/'.format(
        'a' * 32, 'b' * 32, '3' * 11, '9' * 15), {
        # valid everything but target numbers
        'instance': plugins.NotifySinch,
    }),
    ('sinch://{}:{}@12345/{}'.format('a' * 32, 'b' * 32, '4' * 11), {
        # using short-code (5 characters)
        'instance': plugins.NotifySinch,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'sinch://...aaaa:b...b@12345',
    }),
    ('sinch://{}:{}@123456/{}'.format('a' * 32, 'b' * 32, '4' * 11), {
        # using short-code (6 characters)
        'instance': plugins.NotifySinch,
    }),
    ('sinch://{}:{}@{}'.format('a' * 32, 'b' * 32, '5' * 11), {
        # using phone no with no target - we text ourselves in
        # this case
        'instance': plugins.NotifySinch,
    }),
    ('sinch://{}:{}@{}?region=eu'.format('a' * 32, 'b' * 32, '5' * 11), {
        # Specify a region
        'instance': plugins.NotifySinch,
    }),
    ('sinch://{}:{}@{}?region=invalid'.format('a' * 32, 'b' * 32, '5' * 11), {
        # Invalid region
        'instance': TypeError,
    }),
    ('sinch://_?spi={}&token={}&from={}'.format(
        'a' * 32, 'b' * 32, '5' * 11), {
        # use get args to acomplish the same thing
        'instance': plugins.NotifySinch,
    }),
    ('sinch://_?spi={}&token={}&source={}'.format(
        'a' * 32, 'b' * 32, '5' * 11), {
        # use get args to acomplish the same thing (use source instead of from)
        'instance': plugins.NotifySinch,
    }),
    ('sinch://_?spi={}&token={}&from={}&to={}'.format(
        'a' * 32, 'b' * 32, '5' * 11, '7' * 13), {
        # use to=
        'instance': plugins.NotifySinch,
    }),
    ('sinch://{}:{}@{}'.format('a' * 32, 'b' * 32, '6' * 11), {
        'instance': plugins.NotifySinch,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('sinch://{}:{}@{}'.format('a' * 32, 'b' * 32, '6' * 11), {
        'instance': plugins.NotifySinch,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifySimplePush
    ##################################
    ('spush://', {
        # No api key
        'instance': None,
    }),
    ('spush://{}'.format('A' * 14), {
        # API Key specified however expected server response
        # didn't have 'OK' in JSON response
        'instance': plugins.NotifySimplePush,
        # Expected notify() response
        'notify_response': False,
    }),
    ('spush://{}'.format('Y' * 14), {
        # API Key valid and expected response was valid
        'instance': plugins.NotifySimplePush,
        # Set our response to OK
        'requests_response_text': {
            'status': 'OK',
        },

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'spush://Y...Y/',
    }),
    ('spush://{}?event=Not%20So%20Good'.format('X' * 14), {
        # API Key valid and expected response was valid
        'instance': plugins.NotifySimplePush,
        # Set our response to something that is not okay
        'requests_response_text': {
            'status': 'NOT-OK',
        },
        # Expected notify() response
        'notify_response': False,
    }),
    ('spush://salt:pass@{}'.format('X' * 14, 'A' * 16), {
        # Now we'll test encrypted messages with new salt
        'instance': plugins.NotifySimplePush,
        # Set our response to OK
        'requests_response_text': {
            'status': 'OK',
        },

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'spush://****:****@X...X/',
    }),
    ('spush://{}'.format('Y' * 14), {
        'instance': plugins.NotifySimplePush,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
        # Set a failing message too
        'requests_response_text': {
            'status': 'BadRequest',
            'message': 'Title or message too long',
        },
    }),
    ('spush://{}'.format('Z' * 14), {
        'instance': plugins.NotifySimplePush,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifySlack
    ##################################
    ('slack://', {
        'instance': TypeError,
    }),
    ('slack://:@/', {
        'instance': TypeError,
    }),
    ('slack://T1JJ3T3L2', {
        # Just Token 1 provided
        'instance': TypeError,
    }),
    ('slack://T1JJ3T3L2/A1BRTD4JD/', {
        # Just 2 tokens provided
        'instance': TypeError,
    }),
    ('slack://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#hmm/#-invalid-', {
        # No username specified; this is still okay as we sub in
        # default; The one invalid channel is skipped when sending a message
        'instance': plugins.NotifySlack,
        # There is an invalid channel that we will fail to deliver to
        # as a result the response type will be false
        'response': False,
        'requests_response_text': {
            'ok': False,
            'message': 'Bad Channel',
        },
    }),
    ('slack://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#channel', {
        # No username specified; this is still okay as we sub in
        # default; The one invalid channel is skipped when sending a message
        'instance': plugins.NotifySlack,
        # don't include an image by default
        'include_image': False,
        'requests_response_text': {
            'ok': True,
            'message': '',
        },
    }),
    ('slack://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/+id/@id/', {
        # + encoded id,
        # @ userid
        'instance': plugins.NotifySlack,
        'requests_response_text': {
            'ok': True,
            'message': '',
        },
    }),
    ('slack://username@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/' \
        '?to=#nuxref', {
            'instance': plugins.NotifySlack,

            # Our expected url(privacy=True) startswith() response:
            'privacy_url': 'slack://username@T...2/A...D/T...Q/',
            'requests_response_text': {
                'ok': True,
                'message': '',
            },
        }),
    ('slack://username@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#nuxref', {
        'instance': plugins.NotifySlack,
        'requests_response_text': {
            'ok': True,
            'message': '',
        },
    }),
    # Test using a bot-token (also test footer set to no flag)
    ('slack://username@xoxb-1234-1234-abc124/#nuxref?footer=no', {
        'instance': plugins.NotifySlack,
        'requests_response_text': {
            'ok': True,
            'message': '',
            # support attachments
            'file': {
                'url_private': 'http://localhost/',
            },
        },
    }),

    ('slack://username@xoxb-1234-1234-abc124/#nuxref', {
        'instance': plugins.NotifySlack,
        'requests_response_text': {
            'ok': True,
            'message': '',
        },
        # we'll fail to send attachments because we had no 'file' response in
        # our object
        'response': False,
    }),

    ('slack://username@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ', {
        # Missing a channel, falls back to webhook channel bindings
        'instance': plugins.NotifySlack,
        'requests_response_text': {
            'ok': True,
            'message': '',
        },
    }),
    # Native URL Support, take the slack URL and still build from it
    ('https://hooks.slack.com/services/{}/{}/{}'.format(
        'A' * 9, 'B' * 9, 'c' * 24), {
        'instance': plugins.NotifySlack,
        'requests_response_text': {
            'ok': True,
            'message': '',
        },
    }),
    # Native URL Support with arguments
    ('https://hooks.slack.com/services/{}/{}/{}?format=text'.format(
        'A' * 9, 'B' * 9, 'c' * 24), {
        'instance': plugins.NotifySlack,
        'requests_response_text': {
            'ok': True,
            'message': '',
        },
    }),
    ('slack://username@INVALID/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#cool', {
        # invalid 1st Token
        'instance': TypeError,
    }),
    ('slack://username@T1JJ3T3L2/INVALID/TIiajkdnlazkcOXrIdevi7FQ/#great', {
        # invalid 2rd Token
        'instance': TypeError,
    }),
    ('slack://username@T1JJ3T3L2/A1BRTD4JD/INVALID/#channel', {
        # invalid 3rd Token
        'instance': TypeError,
    }),
    ('slack://l2g@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#usenet', {
        'instance': plugins.NotifySlack,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
        'requests_response_text': {
            'ok': False,
            'message': '',
        },
    }),
    ('slack://respect@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#a', {
        'instance': plugins.NotifySlack,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
        'requests_response_text': {
            'ok': False,
            'message': '',
        },
    }),
    ('slack://notify@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#b', {
        'instance': plugins.NotifySlack,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
        'requests_response_text': {
            'ok': False,
            'message': '',
        },
    }),

    ##################################
    # NotifySNS (AWS)
    ##################################
    ('sns://', {
        'instance': None,
    }),
    ('sns://:@/', {
        'instance': None,
    }),
    ('sns://T1JJ3T3L2', {
        # Just Token 1 provided
        'instance': TypeError,
    }),
    ('sns://T1JJ3TD4JD/TIiajkdnlazk7FQ/', {
        # Missing a region
        'instance': TypeError,
    }),
    ('sns://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcevi7FQ/us-west-2/12223334444', {
        # we have a valid URL and one number to text
        'instance': plugins.NotifySNS,
    }),
    ('sns://T1JJ3TD4JD/TIiajkdnlazk7FQ/us-west-2/12223334444/12223334445', {
        # Multi SNS Suppport
        'instance': plugins.NotifySNS,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'sns://T...D/****/us-west-2',
    }),
    ('sns://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/us-east-1' \
        '?to=12223334444', {
            # Missing a topic and/or phone No
            'instance': plugins.NotifySNS,
        }),
    ('sns://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcevi7FQ/us-west-2/12223334444', {
        'instance': plugins.NotifySNS,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('sns://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcevi7FQ/us-west-2/15556667777', {
        'instance': plugins.NotifySNS,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyTelegram
    ##################################
    ('tgram://', {
        'instance': None,
    }),
    # Simple Message
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message (no images)
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # don't include an image by default
        'include_image': False,
    }),
    # Simple Message with multiple chat names
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message with multiple chat names
    ('tgram://123456789:abcdefg_hijklmnop/?to=id1,id2', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message with an invalid chat ID
    ('tgram://123456789:abcdefg_hijklmnop/%$/', {
        'instance': plugins.NotifyTelegram,
        # Notify will fail
        'response': False,
    }),
    # Simple Message with multiple chat ids
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/23423/-30/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message with multiple chat ids (no images)
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/23423/-30/', {
        'instance': plugins.NotifyTelegram,
        # don't include an image by default
        'include_image': False,
    }),
    # Support bot keyword prefix
    ('tgram://bottest@123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Testing image
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
    }),
    # Testing invalid format (fall's back to html)
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?format=invalid', {
        'instance': plugins.NotifyTelegram,
    }),
    # Testing empty format (falls back to html)
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?format=', {
        'instance': plugins.NotifyTelegram,
    }),
    # Testing valid formats
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?format=markdown', {
        'instance': plugins.NotifyTelegram,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?format=html', {
        'instance': plugins.NotifyTelegram,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?format=text', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message without image
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # don't include an image by default
        'include_image': False,
    }),
    # Invalid Bot Token
    ('tgram://alpha:abcdefg_hijklmnop/lead2gold/', {
        'instance': None,
    }),
    # AuthToken + bad url
    ('tgram://:@/', {
        'instance': None,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
        # force a failure without an image specified
        'include_image': False,
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/', {
        'instance': plugins.NotifyTelegram,
        # force a failure with multiple chat_ids
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/', {
        'instance': plugins.NotifyTelegram,
        # force a failure without an image specified
        'include_image': False,
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # throw a bizzare code forcing us to fail to look it up without
        # having an image included
        'include_image': False,
        'response': False,
        'requests_response_code': 999,
    }),
    # Test with image set
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
        # throw a bizzare code forcing us to fail to look it up without
        # having an image included
        'include_image': True,
        'response': False,
        'requests_response_code': 999,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them without images set
        'include_image': True,
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyTwilio
    ##################################
    ('twilio://', {
        # No Account SID specified
        'instance': TypeError,
    }),
    ('twilio://:@/', {
        # invalid Auth token
        'instance': TypeError,
    }),
    ('twilio://AC{}@12345678'.format('a' * 32), {
        # Just sid provided
        'instance': TypeError,
    }),
    ('twilio://AC{}:{}@_'.format('a' * 32, 'b' * 32), {
        # sid and token provided but invalid from
        'instance': TypeError,
    }),
    ('twilio://AC{}:{}@{}'.format('a' * 32, 'b' * 32, '3' * 5), {
        # using short-code (5 characters) without a target
        # We can still instantiate ourselves with a valid short code
        'instance': TypeError,
    }),
    ('twilio://AC{}:{}@{}'.format('a' * 32, 'b' * 32, '3' * 9), {
        # sid and token provided and from but invalid from no
        'instance': TypeError,
    }),
    ('twilio://AC{}:{}@{}/123/{}/abcd/'.format(
        'a' * 32, 'b' * 32, '3' * 11, '9' * 15), {
        # valid everything but target numbers
        'instance': plugins.NotifyTwilio,
    }),
    ('twilio://AC{}:{}@12345/{}'.format('a' * 32, 'b' * 32, '4' * 11), {
        # using short-code (5 characters)
        'instance': plugins.NotifyTwilio,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'twilio://...aaaa:b...b@12345',
    }),
    ('twilio://AC{}:{}@123456/{}'.format('a' * 32, 'b' * 32, '4' * 11), {
        # using short-code (6 characters)
        'instance': plugins.NotifyTwilio,
    }),
    ('twilio://AC{}:{}@{}'.format('a' * 32, 'b' * 32, '5' * 11), {
        # using phone no with no target - we text ourselves in
        # this case
        'instance': plugins.NotifyTwilio,
    }),
    ('twilio://_?sid=AC{}&token={}&from={}'.format(
        'a' * 32, 'b' * 32, '5' * 11), {
        # use get args to acomplish the same thing
        'instance': plugins.NotifyTwilio,
    }),
    ('twilio://_?sid=AC{}&token={}&source={}'.format(
        'a' * 32, 'b' * 32, '5' * 11), {
        # use get args to acomplish the same thing (use source instead of from)
        'instance': plugins.NotifyTwilio,
    }),
    ('twilio://_?sid=AC{}&token={}&from={}&to={}'.format(
        'a' * 32, 'b' * 32, '5' * 11, '7' * 13), {
        # use to=
        'instance': plugins.NotifyTwilio,
    }),
    ('twilio://AC{}:{}@{}'.format('a' * 32, 'b' * 32, '6' * 11), {
        'instance': plugins.NotifyTwilio,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('twilio://AC{}:{}@{}'.format('a' * 32, 'b' * 32, '6' * 11), {
        'instance': plugins.NotifyTwilio,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyTwist
    ##################################
    ('twist://', {
        # Missing Email and Login
        'instance': None,
    }),
    ('twist://:@/', {
        'instance': None,
    }),
    ('twist://user@example.com/', {
        # No password
        'instance': None,
    }),
    ('twist://user@example.com/password', {
        # Password acceptable as first entry in path
        'instance': plugins.NotifyTwist,
        # Expected notify() response is False because internally we would
        # have failed to login
        'notify_response': False,
    }),
    ('twist://password:user1@example.com', {
        # password:login acceptable
        'instance': plugins.NotifyTwist,
        # Expected notify() response is False because internally we would
        # have failed to login
        'notify_response': False,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'twist://****:user1@example.com',
    }),
    ('twist://password:user2@example.com', {
        # password:login acceptable
        'instance': plugins.NotifyTwist,
        # Expected notify() response is False because internally we would
        # have logged in, but we would have failed to look up the #General
        # channel and workspace.
        'requests_response_text': {
            # Login expected response
            'id': 1234,
            'default_workspace': 9876,
        },
        'notify_response': False,
    }),
    ('twist://password:user2@example.com', {
        'instance': plugins.NotifyTwist,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('twist://password:user2@example.com', {
        'instance': plugins.NotifyTwist,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
    ##################################
    # NotifyTwitter
    ##################################
    ('twitter://', {
        # Missing Consumer API Key
        'instance': TypeError,
    }),
    ('twitter://:@/', {
        'instance': TypeError,
    }),
    ('twitter://consumer_key', {
        # Missing Keys
        'instance': TypeError,
    }),
    ('twitter://consumer_key/consumer_secret/', {
        # Missing Keys
        'instance': TypeError,
    }),
    ('twitter://consumer_key/consumer_secret/access_token/', {
        # Missing Access Secret
        'instance': TypeError,
    }),
    ('twitter://consumer_key/consumer_secret/access_token/access_secret', {
        # No user mean's we message ourselves
        'instance': plugins.NotifyTwitter,
        # Expected notify() response False (because we won't be able
        # to detect our user)
        'notify_response': False,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'twitter://c...y/****/a...n/****',
    }),
    ('twitter://consumer_key/consumer_secret/access_token/access_secret'
        '?cache=no', {
            # No user mean's we message ourselves
            'instance': plugins.NotifyTwitter,
            # However we'll be okay if we return a proper response
            'requests_response_text': {
                'id': 12345,
                'screen_name': 'test'
            },
        }),
    ('twitter://consumer_key/consumer_secret/access_token/access_secret', {
        # No user mean's we message ourselves
        'instance': plugins.NotifyTwitter,
        # However we'll be okay if we return a proper response
        'requests_response_text': {
            'id': 12345,
            'screen_name': 'test'
        },
    }),
    # A duplicate of the entry above, this will cause cache to be referenced
    ('twitter://consumer_key/consumer_secret/access_token/access_secret', {
        # No user mean's we message ourselves
        'instance': plugins.NotifyTwitter,
        # However we'll be okay if we return a proper response
        'requests_response_text': {
            'id': 12345,
            'screen_name': 'test'
        },
    }),
    # handle cases where the screen_name is missing from the response causing
    # an exception during parsing
    ('twitter://consumer_key/consumer_secret2/access_token/access_secret', {
        # No user mean's we message ourselves
        'instance': plugins.NotifyTwitter,
        # However we'll be okay if we return a proper response
        'requests_response_text': {
            'id': 12345,
        },
        # due to a mangled response_text we'll fail
        'notify_response': False,
    }),
    ('twitter://user@consumer_key/csecret2/access_token/access_secret/-/%/', {
        # One Invalid User
        'instance': plugins.NotifyTwitter,
        # Expected notify() response False (because we won't be able
        # to detect our user)
        'notify_response': False,
    }),
    ('twitter://user@consumer_key/csecret/access_token/access_secret'
        '?cache=No', {
            # No Cache
            'instance': plugins.NotifyTwitter,
            'requests_response_text': [{
                'id': 12345,
                'screen_name': 'user'
            }],
        }),
    ('twitter://user@consumer_key/csecret/access_token/access_secret', {
        # We're good!
        'instance': plugins.NotifyTwitter,
        'requests_response_text': [{
            'id': 12345,
            'screen_name': 'user'
        }],
    }),
    # A duplicate of the entry above, this will cause cache to be referenced
    # for this reason, we don't even need to return a valid response
    ('twitter://user@consumer_key/csecret/access_token/access_secret', {
        # We're identifying the same user we already sent to
        'instance': plugins.NotifyTwitter,
    }),
    ('twitter://ckey/csecret/access_token/access_secret?mode=tweet', {
        # A Public Tweet
        'instance': plugins.NotifyTwitter,
    }),
    ('tweet://consumer_key/consumer_secret/access_token/access_secret', {
        # tweet:// is to be depricated; but we will support for purposes of
        # generating a warning to the user; the above matches an above
        # twitter:// reference so that it can use what was cached
        'instance': plugins.NotifyTwitter,
    }),
    ('twitter://user@ckey/csecret/access_token/access_secret?mode=invalid', {
        # An invalid mode
        'instance': TypeError,
    }),
    ('twitter://usera@consumer_key/consumer_secret/access_token/'
        'access_secret/user/?to=userb', {
            # We're good!
            'instance': plugins.NotifyTwitter,
            'requests_response_text': [{
                'id': 12345,
                'screen_name': 'usera'
            }, {
                'id': 12346,
                'screen_name': 'userb'
            }, {
                # A garbage entry we can test exception handling on
                'id': 123,
            }],
        }),
    ('twitter://ckey/csecret/access_token/access_secret', {
        'instance': plugins.NotifyTwitter,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('twitter://ckey/csecret/access_token/access_secret', {
        'instance': plugins.NotifyTwitter,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
    ('twitter://ckey/csecret/access_token/access_secret?mode=tweet', {
        'instance': plugins.NotifyTwitter,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMSG91
    ##################################
    ('msg91://', {
        # No hostname/authkey specified
        'instance': None,
    }),
    ('msg91://-', {
        # Invalid AuthKey
        'instance': None,
    }),
    ('msg91://{}'.format('a' * 23), {
        # No number specified
        'instance': TypeError,
    }),
    ('msg91://{}/123'.format('a' * 23), {
        # invalid phone number
        'instance': TypeError,
    }),
    ('msg91://{}/abcd'.format('a' * 23), {
        # No number to notify
        'instance': TypeError,
    }),
    ('msg91://{}/15551232000/?country=invalid'.format('a' * 23), {
        # invalid country
        'instance': TypeError,
    }),
    ('msg91://{}/15551232000/?country=99'.format('a' * 23), {
        # invalid country
        'instance': TypeError,
    }),
    ('msg91://{}/15551232000/?route=invalid'.format('a' * 23), {
        # invalid route
        'instance': TypeError,
    }),
    ('msg91://{}/15551232000/?route=99'.format('a' * 23), {
        # invalid route
        'instance': TypeError,
    }),
    ('msg91://{}/15551232000'.format('a' * 23), {
        # a valid message
        'instance': plugins.NotifyMSG91,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'msg91://a...a/15551232000',
    }),
    ('msg91://{}/?to=15551232000'.format('a' * 23), {
        # a valid message
        'instance': plugins.NotifyMSG91,
    }),
    ('msg91://{}/15551232000?country=91&route=1'.format('a' * 23), {
        # using phone no with no target - we text ourselves in
        # this case
        'instance': plugins.NotifyMSG91,
    }),
    ('msg91://{}/15551232000'.format('a' * 23), {
        # use get args to acomplish the same thing
        'instance': plugins.NotifyMSG91,
    }),
    ('msg91://{}/15551232000'.format('a' * 23), {
        'instance': plugins.NotifyMSG91,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('msg91://{}/15551232000'.format('a' * 23), {
        'instance': plugins.NotifyMSG91,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMessageBird
    ##################################
    ('msgbird://', {
        # No hostname/apikey specified
        'instance': None,
    }),
    ('msgbird://{}/abcd'.format('a' * 25), {
        # invalid characters in source phone number
        'instance': TypeError,
    }),
    ('msgbird://{}/123'.format('a' * 25), {
        # invalid source phone number
        'instance': TypeError,
    }),
    ('msgbird://{}/15551232000'.format('a' * 25), {
        # target phone number becomes who we text too; all is good
        'instance': plugins.NotifyMessageBird,
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'msgbird://a...a/15551232000',
    }),
    ('msgbird://{}/15551232000/abcd'.format('a' * 25), {
        # invalid target phone number; we have no one to notify
        'instance': TypeError,
    }),
    ('msgbird://{}/15551232000/123'.format('a' * 25), {
        # invalid target phone number
        'instance': TypeError,
    }),
    ('msgbird://{}/?from=15551233000&to=15551232000'.format('a' * 25), {
        # reference to to= and from=
        'instance': plugins.NotifyMessageBird,
    }),
    ('msgbird://{}/15551232000'.format('a' * 25), {
        'instance': plugins.NotifyMessageBird,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('msgbird://{}/15551232000'.format('a' * 25), {
        'instance': plugins.NotifyMessageBird,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('msgbird://{}/15551232000'.format('a' * 25), {
        'instance': plugins.NotifyMessageBird,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyWebexTeams
    ##################################
    ('wxteams://', {
        # Teams Token missing
        'instance': TypeError,
    }),
    ('wxteams://:@/', {
        # We don't have strict host checking on for wxteams, so this URL
        # actually becomes parseable and :@ becomes a hostname.
        # The below errors because a second token wasn't found
        'instance': TypeError,
    }),
    ('wxteams://{}'.format('a' * 80), {
        # token provided - we're good
        'instance': plugins.NotifyWebexTeams,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'wxteams://a...a/',
    }),
    # Support Native URLs
    ('https://api.ciscospark.com/v1/webhooks/incoming/{}'.format('a' * 80), {
        # token provided - we're good
        'instance': plugins.NotifyWebexTeams,
    }),
    # Support Native URLs with arguments
    ('https://api.ciscospark.com/v1/webhooks/incoming/{}?format=text'.format(
        'a' * 80), {
        # token provided - we're good
        'instance': plugins.NotifyWebexTeams,
    }),
    ('wxteams://{}'.format('a' * 80), {
        'instance': plugins.NotifyWebexTeams,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('wxteams://{}'.format('a' * 80), {
        'instance': plugins.NotifyWebexTeams,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('wxteams://{}'.format('a' * 80), {
        'instance': plugins.NotifyWebexTeams,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyKODI
    ##################################
    ('xbmc://', {
        'instance': None,
    }),
    ('xbmc://localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://localhost?duration=14', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://localhost?duration=invalid', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://localhost?duration=-1', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://user:pass@localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://user:pass@localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://user@localhost', {
        'instance': plugins.NotifyXBMC,
        # don't include an image by default
        'include_image': False,
    }),
    ('xbmc://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.WARNING,
    }),
    ('xbmc://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.FAILURE,
    }),
    ('xbmc://:@/', {
        'instance': None,
    }),
    ('xbmc://user:pass@localhost:8081', {
        'instance': plugins.NotifyXBMC,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('xbmc://user:pass@localhost:8082', {
        'instance': plugins.NotifyXBMC,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('xbmc://user:pass@localhost:8083', {
        'instance': plugins.NotifyXBMC,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyXML
    ##################################
    ('xml://:@/', {
        'instance': None,
    }),
    ('xml://', {
        'instance': None,
    }),
    ('xmls://', {
        'instance': None,
    }),
    ('xml://localhost', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://user@localhost', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://user:pass@localhost', {
        'instance': plugins.NotifyXML,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'xml://user:****@localhost',
    }),
    ('xml://localhost:8080', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://user:pass@localhost:8080', {
        'instance': plugins.NotifyXML,
    }),
    ('xmls://localhost', {
        'instance': plugins.NotifyXML,
    }),
    ('xmls://user:pass@localhost', {
        'instance': plugins.NotifyXML,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'xmls://user:****@localhost',
    }),
    ('xmls://localhost:8080/path/', {
        'instance': plugins.NotifyXML,
        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'xmls://localhost:8080/path/',
    }),
    ('xmls://user:pass@localhost:8080', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://localhost:8080/path?-HeaderKey=HeaderValue', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://user:pass@localhost:8081', {
        'instance': plugins.NotifyXML,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('xml://user:pass@localhost:8082', {
        'instance': plugins.NotifyXML,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('xml://user:pass@localhost:8083', {
        'instance': plugins.NotifyXML,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyZulip
    ##################################
    ('zulip://', {
        'instance': None,
    }),
    ('zulip://:@/', {
        'instance': None,
    }),
    ('zulip://apprise', {
        # Just org provided (no token or botname)
        'instance': TypeError,
    }),
    ('zulip://botname@apprise', {
        # Just org and botname provided (no token)
        'instance': TypeError,
    }),
    # invalid token
    ('zulip://botname@apprise/{}'.format('a' * 24), {
        'instance': TypeError,
    }),
    # invalid botname
    ('zulip://....@apprise/{}'.format('a' * 32), {
        'instance': TypeError,
    }),
    # Valid everything - no target so default is used
    ('zulip://botname@apprise/{}'.format('a' * 32), {
        'instance': plugins.NotifyZulip,

        # Our expected url(privacy=True) startswith() response:
        'privacy_url': 'zulip://botname@apprise/a...a/',
    }),
    # Valid everything - organization as hostname
    ('zulip://botname@apprise.zulipchat.com/{}'.format('a' * 32), {
        'instance': plugins.NotifyZulip,
    }),
    # Valid everything - 2 channels specified
    ('zulip://botname@apprise/{}/channel1/channel2'.format('a' * 32), {
        'instance': plugins.NotifyZulip,
    }),
    # Valid everything - 2 channels specified (using to=)
    ('zulip://botname@apprise/{}/?to=channel1/channel2'.format('a' * 32), {
        'instance': plugins.NotifyZulip,
    }),
    # Valid everything - 2 emails specified
    ('zulip://botname@apprise/{}/user@example.com/user2@example.com'.format(
        'a' * 32), {
        'instance': plugins.NotifyZulip,
    }),
    ('zulip://botname@apprise/{}'.format('a' * 32), {
        'instance': plugins.NotifyZulip,
        # don't include an image by default
        'include_image': False,
    }),
    ('zulip://botname@apprise/{}'.format('a' * 32), {
        'instance': plugins.NotifyZulip,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('zulip://botname@apprise/{}'.format('a' * 32), {
        'instance': plugins.NotifyZulip,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('zulip://botname@apprise/{}'.format('a' * 32), {
        'instance': plugins.NotifyZulip,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
)


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_rest_plugins(mock_post, mock_get):
    """
    API: REST Based Plugins()

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Define how many characters exist per line
    row = 80

    # Some variables we use to control the data we work with
    body_len = 1024
    title_len = 1024

    # Create a large body and title with random data
    body = ''.join(choice(str_alpha + str_num + ' ') for _ in range(body_len))
    body = '\r\n'.join([body[i: i + row] for i in range(0, len(body), row)])

    # Create our title using random data
    title = ''.join(choice(str_alpha + str_num) for _ in range(title_len))

    # iterate over our dictionary and test it out
    for (url, meta) in TEST_URLS:
        # Our expected instance
        instance = meta.get('instance', None)

        # Our expected server objects
        self = meta.get('self', None)

        # Our expected Query response (True, False, or exception type)
        response = meta.get('response', True)

        # Our expected Notify response (True or False)
        notify_response = meta.get('notify_response', response)

        # Our expected Notify Attachment response (True or False)
        attach_response = meta.get('attach_response', notify_response)

        # Our expected privacy url
        # Don't set this if don't need to check it's value
        privacy_url = meta.get('privacy_url')

        # Test attachments
        # Don't set this if don't need to check it's value
        check_attachments = meta.get('check_attachments', True)

        # Allow us to force the server response code to be something other then
        # the defaults
        requests_response_code = meta.get(
            'requests_response_code',
            requests.codes.ok if response else requests.codes.not_found,
        )

        # Allow us to force the server response text to be something other then
        # the defaults
        requests_response_text = meta.get('requests_response_text')
        if not isinstance(requests_response_text, six.string_types):
            # Convert to string
            requests_response_text = dumps(requests_response_text)

        # Allow notification type override, otherwise default to INFO
        notify_type = meta.get('notify_type', NotifyType.INFO)

        # Whether or not we should include an image with our request; unless
        # otherwise specified, we assume that images are to be included
        include_image = meta.get('include_image', True)
        if include_image:
            # a default asset
            asset = AppriseAsset()

        else:
            # Disable images
            asset = AppriseAsset(image_path_mask=False, image_url_mask=False)
            asset.image_url_logo = None

        test_requests_exceptions = meta.get(
            'test_requests_exceptions', False)

        # A request
        robj = mock.Mock()
        robj.content = u''
        mock_get.return_value = robj
        mock_post.return_value = robj

        if test_requests_exceptions is False:
            # Handle our default response
            mock_post.return_value.status_code = requests_response_code
            mock_get.return_value.status_code = requests_response_code

            # Handle our default text response
            mock_get.return_value.content = requests_response_text
            mock_post.return_value.content = requests_response_text

            # Ensure there is no side effect set
            mock_post.side_effect = None
            mock_get.side_effect = None

        else:
            # Handle exception testing; first we turn the boolean flag ito
            # a list of exceptions
            test_requests_exceptions = REQUEST_EXCEPTIONS

        try:
            obj = Apprise.instantiate(
                url, asset=asset, suppress_exceptions=False)

            if obj is None:
                if instance is not None:
                    # We're done (assuming this is what we were expecting)
                    print("{} didn't instantiate itself "
                          "(we expected it to be a {})".format(url, instance))
                    assert False
                continue

            if instance is None:
                # Expected None but didn't get it
                print('%s instantiated %s (but expected None)' % (
                    url, str(obj)))
                assert False

            assert isinstance(obj, instance) is True

            if isinstance(obj, plugins.NotifyBase):
                # We loaded okay; now lets make sure we can reverse this url
                assert isinstance(obj.url(), six.string_types) is True

                # Test url() with privacy=True
                assert isinstance(
                    obj.url(privacy=True), six.string_types) is True

                # Some Simple Invalid Instance Testing
                assert instance.parse_url(None) is None
                assert instance.parse_url(object) is None
                assert instance.parse_url(42) is None

                if privacy_url:
                    # Assess that our privacy url is as expected
                    assert obj.url(privacy=True).startswith(privacy_url)

                # Instantiate the exact same object again using the URL from
                # the one that was already created properly
                obj_cmp = Apprise.instantiate(obj.url())

                # Our object should be the same instance as what we had
                # originally expected above.
                if not isinstance(obj_cmp, plugins.NotifyBase):
                    # Assert messages are hard to trace back with the way
                    # these tests work. Just printing before throwing our
                    # assertion failure makes things easier to debug later on
                    print('TEST FAIL: {} regenerated as {}'.format(
                        url, obj.url()))
                    assert False

                # Tidy our object
                del obj_cmp

            if self:
                # Iterate over our expected entries inside of our object
                for key, val in self.items():
                    # Test that our object has the desired key
                    assert hasattr(key, obj) is True
                    assert getattr(key, obj) == val

            #
            # Stage 1: with title defined
            #
            try:
                if test_requests_exceptions is False:
                    # Disable throttling
                    obj.request_rate_per_sec = 0

                    # check that we're as expected
                    assert obj.notify(
                        body=body, title=title,
                        notify_type=notify_type) == notify_response

                    # check that this doesn't change using different overflow
                    # methods
                    assert obj.notify(
                        body=body, title=title,
                        notify_type=notify_type,
                        overflow=OverflowMode.UPSTREAM) == notify_response
                    assert obj.notify(
                        body=body, title=title,
                        notify_type=notify_type,
                        overflow=OverflowMode.TRUNCATE) == notify_response
                    assert obj.notify(
                        body=body, title=title,
                        notify_type=notify_type,
                        overflow=OverflowMode.SPLIT) == notify_response

                    if check_attachments:
                        # Test single attachment support; even if the service
                        # doesn't support attachments, it should still
                        # gracefully ignore the data
                        attach = os.path.join(TEST_VAR_DIR, 'apprise-test.gif')
                        assert obj.notify(
                            body=body, title=title,
                            notify_type=notify_type,
                            attach=attach) == attach_response

                        # Same results should apply to a list of attachments
                        attach = AppriseAttachment((
                            os.path.join(TEST_VAR_DIR, 'apprise-test.gif'),
                            os.path.join(TEST_VAR_DIR, 'apprise-test.png'),
                            os.path.join(TEST_VAR_DIR, 'apprise-test.jpeg'),
                        ))
                        assert obj.notify(
                            body=body, title=title,
                            notify_type=notify_type,
                            attach=attach) == attach_response

                else:
                    # Disable throttling
                    obj.request_rate_per_sec = 0

                    for _exception in REQUEST_EXCEPTIONS:
                        mock_post.side_effect = _exception
                        mock_get.side_effect = _exception

                        try:
                            assert obj.notify(
                                body=body, title=title,
                                notify_type=NotifyType.INFO) is False

                        except AssertionError:
                            # Don't mess with these entries
                            raise

                        except Exception:
                            # We can't handle this exception type
                            raise

            except AssertionError:
                # Don't mess with these entries
                raise

            except Exception as e:
                # Check that we were expecting this exception to happen
                try:
                    if not isinstance(e, response):
                        raise e

                except TypeError:
                    print('%s Unhandled response %s' % (url, type(e)))
                    raise e

            #
            # Stage 2: without title defined
            #
            try:
                if test_requests_exceptions is False:
                    # check that we're as expected
                    assert obj.notify(body='body', notify_type=notify_type) \
                        == notify_response

                else:
                    for _exception in REQUEST_EXCEPTIONS:
                        mock_post.side_effect = _exception
                        mock_get.side_effect = _exception

                        try:
                            assert obj.notify(
                                body=body,
                                notify_type=NotifyType.INFO) is False

                        except AssertionError:
                            # Don't mess with these entries
                            raise

                        except Exception:
                            # We can't handle this exception type
                            raise

            except AssertionError:
                # Don't mess with these entries
                raise

            except Exception as e:
                # Check that we were expecting this exception to happen
                if not isinstance(e, response):
                    raise e

            # Tidy our object and allow any possible defined deconstructors to
            # be executed.
            del obj

        except AssertionError:
            # Don't mess with these entries
            print('%s AssertionError' % url)
            raise

        except Exception as e:
            # Handle our exception
            if instance is None:
                print('%s %s' % (url, str(e)))
                raise e

            if not isinstance(e, instance):
                print('%s %s' % (url, str(e)))
                raise e


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_boxcar_plugin(mock_post, mock_get):
    """
    API: NotifyBoxcar() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Generate some generic message types
    device = 'A' * 64
    tag = '@B' * 63

    access = '-' * 64
    secret = '_' * 64

    # Initializes the plugin with recipients set to None
    plugins.NotifyBoxcar(access=access, secret=secret, targets=None)

    # Initializes the plugin with a valid access, but invalid access key
    with pytest.raises(TypeError):
        plugins.NotifyBoxcar(access=None, secret=secret, targets=None)

    # Initializes the plugin with a valid access, but invalid secret
    with pytest.raises(TypeError):
        plugins.NotifyBoxcar(access=access, secret=None, targets=None)

    # Initializes the plugin with recipients list
    # the below also tests our the variation of recipient types
    plugins.NotifyBoxcar(
        access=access, secret=secret, targets=[device, tag])

    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.created
    mock_get.return_value.status_code = requests.codes.created

    # Test notifications without a body or a title
    p = plugins.NotifyBoxcar(access=access, secret=secret, targets=None)

    assert p.notify(body=None, title=None, notify_type=NotifyType.INFO) is True

    # Test comma, separate values
    device = 'a' * 64

    p = plugins.NotifyBoxcar(
        access=access, secret=secret,
        targets=','.join([device, device, device]))
    assert len(p.device_tokens) == 3


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_emby_plugin_login(mock_post, mock_get):
    """
    API: NotifyEmby.login()

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()

    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost')
    assert isinstance(obj, plugins.NotifyEmby)

    # Test our exception handling
    for _exception in REQUEST_EXCEPTIONS:
        mock_post.side_effect = _exception
        mock_get.side_effect = _exception
        # We'll fail to log in each time
        assert obj.login() is False

    # Disable Exceptions
    mock_post.side_effect = None
    mock_get.side_effect = None

    # Our login flat out fails if we don't have proper parseable content
    mock_post.return_value.content = u''
    mock_get.return_value.content = mock_post.return_value.content

    # KeyError handling
    mock_post.return_value.status_code = 999
    mock_get.return_value.status_code = 999
    assert obj.login() is False

    # General Internal Server Error
    mock_post.return_value.status_code = requests.codes.internal_server_error
    mock_get.return_value.status_code = requests.codes.internal_server_error
    assert obj.login() is False

    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost:%d' % (
        # Increment our port so it will always be something different than
        # the default
        plugins.NotifyEmby.emby_default_port + 1))
    assert isinstance(obj, plugins.NotifyEmby)
    assert obj.port == (plugins.NotifyEmby.emby_default_port + 1)

    # The login will fail because '' is not a parseable JSON response
    assert obj.login() is False

    # Disable the port completely
    obj.port = None
    assert obj.login() is False

    # Default port assigments
    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost')
    assert isinstance(obj, plugins.NotifyEmby)
    assert obj.port == plugins.NotifyEmby.emby_default_port

    # The login will (still) fail because '' is not a parseable JSON response
    assert obj.login() is False

    # Our login flat out fails if we don't have proper parseable content
    mock_post.return_value.content = dumps({
        u'AccessToken': u'0000-0000-0000-0000',
    })
    mock_get.return_value.content = mock_post.return_value.content

    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost')
    assert isinstance(obj, plugins.NotifyEmby)

    # The login will fail because the 'User' or 'Id' field wasn't parsed
    assert obj.login() is False

    # Our text content (we intentionally reverse the 2 locations
    # that store the same thing; we do this so we can test which
    # one it defaults to if both are present
    mock_post.return_value.content = dumps({
        u'User': {
            u'Id': u'abcd123',
        },
        u'Id': u'123abc',
        u'AccessToken': u'0000-0000-0000-0000',
    })
    mock_get.return_value.content = mock_post.return_value.content

    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost')
    assert isinstance(obj, plugins.NotifyEmby)

    # Login
    assert obj.login() is True
    assert obj.user_id == '123abc'
    assert obj.access_token == '0000-0000-0000-0000'

    # We're going to log in a second time which checks that we logout
    # first before logging in again. But this time we'll scrap the
    # 'Id' area and use the one found in the User area if detected
    mock_post.return_value.content = dumps({
        u'User': {
            u'Id': u'abcd123',
        },
        u'AccessToken': u'0000-0000-0000-0000',
    })
    mock_get.return_value.content = mock_post.return_value.content

    # Login
    assert obj.login() is True
    assert obj.user_id == 'abcd123'
    assert obj.access_token == '0000-0000-0000-0000'


@mock.patch('apprise.plugins.NotifyEmby.login')
@mock.patch('apprise.plugins.NotifyEmby.logout')
@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_emby_plugin_sessions(mock_post, mock_get, mock_logout,
                                     mock_login):
    """
    API: NotifyEmby.sessions()

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()

    # This is done so we don't obstruct our access_token and user_id values
    mock_login.return_value = True
    mock_logout.return_value = True

    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost')
    assert isinstance(obj, plugins.NotifyEmby)
    obj.access_token = 'abc'
    obj.user_id = '123'

    # Test our exception handling
    for _exception in REQUEST_EXCEPTIONS:
        mock_post.side_effect = _exception
        mock_get.side_effect = _exception
        # We'll fail to log in each time
        sessions = obj.sessions()
        assert isinstance(sessions, dict) is True
        assert len(sessions) == 0

    # Disable Exceptions
    mock_post.side_effect = None
    mock_get.side_effect = None

    # Our login flat out fails if we don't have proper parseable content
    mock_post.return_value.content = u''
    mock_get.return_value.content = mock_post.return_value.content

    # KeyError handling
    mock_post.return_value.status_code = 999
    mock_get.return_value.status_code = 999
    sessions = obj.sessions()
    assert isinstance(sessions, dict) is True
    assert len(sessions) == 0

    # General Internal Server Error
    mock_post.return_value.status_code = requests.codes.internal_server_error
    mock_get.return_value.status_code = requests.codes.internal_server_error
    sessions = obj.sessions()
    assert isinstance(sessions, dict) is True
    assert len(sessions) == 0

    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok
    mock_get.return_value.content = mock_post.return_value.content

    # Disable the port completely
    obj.port = None

    sessions = obj.sessions()
    assert isinstance(sessions, dict) is True
    assert len(sessions) == 0

    # Let's get some results
    mock_post.return_value.content = dumps([
        {
            u'Id': u'abc123',
        },
        {
            u'Id': u'def456',
        },
        {
            u'InvalidEntry': None,
        },
    ])
    mock_get.return_value.content = mock_post.return_value.content

    sessions = obj.sessions(user_controlled=True)
    assert isinstance(sessions, dict) is True
    assert len(sessions) == 2

    # Test it without setting user-controlled sessions
    sessions = obj.sessions(user_controlled=False)
    assert isinstance(sessions, dict) is True
    assert len(sessions) == 2

    # Triggers an authentication failure
    obj.user_id = None
    mock_login.return_value = False
    sessions = obj.sessions()
    assert isinstance(sessions, dict) is True
    assert len(sessions) == 0


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_flock_plugin(mock_post, mock_get):
    """
    API: NotifyFlock() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Initializes the plugin with an invalid token
    with pytest.raises(TypeError):
        plugins.NotifyFlock(token=None)
    # Whitespace also acts as an invalid token value
    with pytest.raises(TypeError):
        plugins.NotifyFlock(token="   ")


def test_notify_gitter_plugin():
    """
    API: NotifyGitter() Extra Checks

    """
    # Define our channels
    targets = ['apprise']

    # Initializes the plugin with an invalid token
    with pytest.raises(TypeError):
        plugins.NotifyGitter(token=None, targets=targets)
    # Whitespace also acts as an invalid token value
    with pytest.raises(TypeError):
        plugins.NotifyGitter(token="   ", targets=targets)


def test_notify_gotify_plugin():
    """
    API: NotifyGotify() Extra Checks

    """
    # Initializes the plugin with an invalid token
    with pytest.raises(TypeError):
        plugins.NotifyGotify(token=None)
    # Whitespace also acts as an invalid token value
    with pytest.raises(TypeError):
        plugins.NotifyGotify(token="   ")


@mock.patch('requests.post')
def test_notify_msg91_plugin(mock_post):
    """
    API: NotifyMSG91() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare our response
    response = requests.Request()
    response.status_code = requests.codes.ok

    # Prepare Mock
    mock_post.return_value = response

    # Initialize some generic (but valid) tokens
    # authkey = '{}'.format('a' * 24)
    target = '+1 (555) 123-3456'

    # No authkey specified
    with pytest.raises(TypeError):
        plugins.NotifyMSG91(authkey=None, targets=target)
    with pytest.raises(TypeError):
        plugins.NotifyMSG91(authkey="    ", targets=target)


def test_notify_msteams_plugin():
    """
    API: NotifyMSTeams() Extra Checks

    """
    # Initializes the plugin with an invalid token
    with pytest.raises(TypeError):
        plugins.NotifyMSTeams(token_a=None, token_b='abcd', token_c='abcd')
    # Whitespace also acts as an invalid token value
    with pytest.raises(TypeError):
        plugins.NotifyMSTeams(token_a='  ', token_b='abcd', token_c='abcd')

    with pytest.raises(TypeError):
        plugins.NotifyMSTeams(token_a='abcd', token_b=None, token_c='abcd')
    # Whitespace also acts as an invalid token value
    with pytest.raises(TypeError):
        plugins.NotifyMSTeams(token_a='abcd', token_b='  ', token_c='abcd')

    with pytest.raises(TypeError):
        plugins.NotifyMSTeams(token_a='abcd', token_b='abcd', token_c=None)
    # Whitespace also acts as an invalid token value
    with pytest.raises(TypeError):
        plugins.NotifyMSTeams(token_a='abcd', token_b='abcd', token_c='  ')


def test_notify_prowl_plugin():
    """
    API: NotifyProwl() Extra Checks

    """
    # Initializes the plugin with an invalid apikey
    with pytest.raises(TypeError):
        plugins.NotifyProwl(apikey=None)
    # Whitespace also acts as an invalid apikey value
    with pytest.raises(TypeError):
        plugins.NotifyProwl(apikey='  ')

    # Whitespace also acts as an invalid provider key
    with pytest.raises(TypeError):
        plugins.NotifyProwl(apikey='abcd', providerkey=object())
    with pytest.raises(TypeError):
        plugins.NotifyProwl(apikey='abcd', providerkey='  ')


@mock.patch('requests.post')
def test_notify_sinch_plugin(mock_post):
    """
    API: NotifySinch() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare our response
    response = requests.Request()
    response.status_code = requests.codes.ok

    # Prepare Mock
    mock_post.return_value = response

    # Initialize some generic (but valid) tokens
    service_plan_id = '{}'.format('b' * 32)
    api_token = '{}'.format('b' * 32)
    source = '+1 (555) 123-3456'

    # No service_plan_id specified
    with pytest.raises(TypeError):
        plugins.NotifySinch(
            service_plan_id=None, api_token=api_token, source=source)

    # No api_token specified
    with pytest.raises(TypeError):
        plugins.NotifySinch(
            service_plan_id=service_plan_id, api_token=None, source=source)

    # a error response
    response.status_code = 400
    response.content = dumps({
        'code': 21211,
        'message': "The 'To' number +1234567 is not a valid phone number.",
    })
    mock_post.return_value = response

    # Initialize our object
    obj = plugins.NotifySinch(
        service_plan_id=service_plan_id, api_token=api_token, source=source)

    # We will fail with the above error code
    assert obj.notify('title', 'body', 'info') is False


@mock.patch('requests.post')
def test_notify_twilio_plugin(mock_post):
    """
    API: NotifyTwilio() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare our response
    response = requests.Request()
    response.status_code = requests.codes.ok

    # Prepare Mock
    mock_post.return_value = response

    # Initialize some generic (but valid) tokens
    account_sid = 'AC{}'.format('b' * 32)
    auth_token = '{}'.format('b' * 32)
    source = '+1 (555) 123-3456'

    # No account_sid specified
    with pytest.raises(TypeError):
        plugins.NotifyTwilio(
            account_sid=None, auth_token=auth_token, source=source)

    # No auth_token specified
    with pytest.raises(TypeError):
        plugins.NotifyTwilio(
            account_sid=account_sid, auth_token=None, source=source)

    # a error response
    response.status_code = 400
    response.content = dumps({
        'code': 21211,
        'message': "The 'To' number +1234567 is not a valid phone number.",
    })
    mock_post.return_value = response

    # Initialize our object
    obj = plugins.NotifyTwilio(
        account_sid=account_sid, auth_token=auth_token, source=source)

    # We will fail with the above error code
    assert obj.notify('title', 'body', 'info') is False


@mock.patch('requests.post')
def test_notify_nexmo_plugin(mock_post):
    """
    API: NotifyNexmo() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare our response
    response = requests.Request()
    response.status_code = requests.codes.ok

    # Prepare Mock
    mock_post.return_value = response

    # Initialize some generic (but valid) tokens
    apikey = 'AC{}'.format('b' * 8)
    secret = '{}'.format('b' * 16)
    source = '+1 (555) 123-3456'

    # No apikey specified
    with pytest.raises(TypeError):
        plugins.NotifyNexmo(apikey=None, secret=secret, source=source)

    with pytest.raises(TypeError):
        plugins.NotifyNexmo(apikey="  ", secret=secret, source=source)

    # No secret specified
    with pytest.raises(TypeError):
        plugins.NotifyNexmo(apikey=apikey, secret=None, source=source)

    with pytest.raises(TypeError):
        plugins.NotifyNexmo(apikey=apikey, secret="  ", source=source)

    # a error response
    response.status_code = 400
    response.content = dumps({
        'code': 21211,
        'message': "The 'To' number +1234567 is not a valid phone number.",
    })
    mock_post.return_value = response

    # Initialize our object
    obj = plugins.NotifyNexmo(
        apikey=apikey, secret=secret, source=source)

    # We will fail with the above error code
    assert obj.notify('title', 'body', 'info') is False


@mock.patch('apprise.plugins.NotifyEmby.login')
@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_emby_plugin_logout(mock_post, mock_get, mock_login):
    """
    API: NotifyEmby.sessions()

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()

    # This is done so we don't obstruct our access_token and user_id values
    mock_login.return_value = True

    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost')
    assert isinstance(obj, plugins.NotifyEmby)
    obj.access_token = 'abc'
    obj.user_id = '123'

    # Test our exception handling
    for _exception in REQUEST_EXCEPTIONS:
        mock_post.side_effect = _exception
        mock_get.side_effect = _exception
        # We'll fail to log in each time
        obj.logout()
        obj.access_token = 'abc'
        obj.user_id = '123'

    # Disable Exceptions
    mock_post.side_effect = None
    mock_get.side_effect = None

    # Our login flat out fails if we don't have proper parseable content
    mock_post.return_value.content = u''
    mock_get.return_value.content = mock_post.return_value.content

    # KeyError handling
    mock_post.return_value.status_code = 999
    mock_get.return_value.status_code = 999
    obj.logout()
    obj.access_token = 'abc'
    obj.user_id = '123'

    # General Internal Server Error
    mock_post.return_value.status_code = requests.codes.internal_server_error
    mock_get.return_value.status_code = requests.codes.internal_server_error
    obj.logout()
    obj.access_token = 'abc'
    obj.user_id = '123'

    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok
    mock_get.return_value.content = mock_post.return_value.content

    # Disable the port completely
    obj.port = None

    # Perform logout
    obj.logout()

    # Calling logout on an object already logged out
    obj.logout()

    # Test Python v3.5 LookupError Bug: https://bugs.python.org/issue29288
    mock_post.side_effect = LookupError()
    mock_get.side_effect = LookupError()
    obj.access_token = 'abc'
    obj.user_id = '123'

    # Tidy object
    del obj


@mock.patch('apprise.plugins.NotifyEmby.sessions')
@mock.patch('apprise.plugins.NotifyEmby.login')
@mock.patch('apprise.plugins.NotifyEmby.logout')
@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_emby_plugin_notify(mock_post, mock_get, mock_logout,
                                   mock_login, mock_sessions):
    """
    API: NotifyEmby.notify()

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    req = requests.Request()
    req.status_code = requests.codes.ok
    req.content = ''
    mock_get.return_value = req
    mock_post.return_value = req

    # This is done so we don't obstruct our access_token and user_id values
    mock_login.return_value = True
    mock_logout.return_value = True
    mock_sessions.return_value = {'abcd': {}}

    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost?modal=False')
    assert isinstance(obj, plugins.NotifyEmby)
    assert obj.notify('title', 'body', 'info') is True
    obj.access_token = 'abc'
    obj.user_id = '123'

    # Test Modal support
    obj = Apprise.instantiate('emby://l2g:l2gpass@localhost?modal=True')
    assert isinstance(obj, plugins.NotifyEmby)
    assert obj.notify('title', 'body', 'info') is True
    obj.access_token = 'abc'
    obj.user_id = '123'

    # Test our exception handling
    for _exception in REQUEST_EXCEPTIONS:
        mock_post.side_effect = _exception
        mock_get.side_effect = _exception
        # We'll fail to log in each time
        assert obj.notify('title', 'body', 'info') is False

    # Disable Exceptions
    mock_post.side_effect = None
    mock_get.side_effect = None

    # Our login flat out fails if we don't have proper parseable content
    mock_post.return_value.content = u''
    mock_get.return_value.content = mock_post.return_value.content

    # KeyError handling
    mock_post.return_value.status_code = 999
    mock_get.return_value.status_code = 999
    assert obj.notify('title', 'body', 'info') is False

    # General Internal Server Error
    mock_post.return_value.status_code = requests.codes.internal_server_error
    mock_get.return_value.status_code = requests.codes.internal_server_error
    assert obj.notify('title', 'body', 'info') is False

    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok
    mock_get.return_value.content = mock_post.return_value.content

    # Disable the port completely
    obj.port = None
    assert obj.notify('title', 'body', 'info') is True

    # An Empty return set (no query is made, but notification will still
    # succeed
    mock_sessions.return_value = {}
    assert obj.notify('title', 'body', 'info') is True

    # Tidy our object
    del obj


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_ifttt_plugin(mock_post, mock_get):
    """
    API: NotifyIFTTT() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Initialize some generic (but valid) tokens
    webhook_id = 'webhook_id'
    events = ['event1', 'event2']

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok
    mock_get.return_value.content = '{}'
    mock_post.return_value.content = '{}'

    # No webhook_id specified
    with pytest.raises(TypeError):
        plugins.NotifyIFTTT(webhook_id=None, events=None)

    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Initializes the plugin with an invalid webhook id
    with pytest.raises(TypeError):
        plugins.NotifyIFTTT(webhook_id=None, events=events)

    # Whitespace also acts as an invalid webhook id
    with pytest.raises(TypeError):
        plugins.NotifyIFTTT(webhook_id="   ", events=events)

    # No events specified
    with pytest.raises(TypeError):
        plugins.NotifyIFTTT(webhook_id=webhook_id, events=None)

    obj = plugins.NotifyIFTTT(webhook_id=webhook_id, events=events)
    assert isinstance(obj, plugins.NotifyIFTTT) is True

    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is True

    # Test the addition of tokens
    obj = plugins.NotifyIFTTT(
        webhook_id=webhook_id, events=events,
        add_tokens={'Test': 'ValueA', 'Test2': 'ValueB'})

    assert isinstance(obj, plugins.NotifyIFTTT) is True

    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is True

    # Invalid del_tokens entry
    with pytest.raises(TypeError):
        plugins.NotifyIFTTT(
            webhook_id=webhook_id, events=events,
            del_tokens=plugins.NotifyIFTTT.ifttt_default_title_key)

    assert isinstance(obj, plugins.NotifyIFTTT) is True

    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is True

    # Test removal of tokens by a list
    obj = plugins.NotifyIFTTT(
        webhook_id=webhook_id, events=events,
        add_tokens={
            'MyKey': 'MyValue'
        },
        del_tokens=(
            plugins.NotifyIFTTT.ifttt_default_title_key,
            plugins.NotifyIFTTT.ifttt_default_body_key,
            plugins.NotifyIFTTT.ifttt_default_type_key))

    assert isinstance(obj, plugins.NotifyIFTTT) is True

    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is True

    # Test removal of tokens as dict
    obj = plugins.NotifyIFTTT(
        webhook_id=webhook_id, events=events,
        add_tokens={
            'MyKey': 'MyValue'
        },
        del_tokens={
            plugins.NotifyIFTTT.ifttt_default_title_key: None,
            plugins.NotifyIFTTT.ifttt_default_body_key: None,
            plugins.NotifyIFTTT.ifttt_default_type_key: None})

    assert isinstance(obj, plugins.NotifyIFTTT) is True


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_join_plugin(mock_post, mock_get):
    """
    API: NotifyJoin() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Generate some generic message types
    device = 'A' * 32
    group = 'group.chrome'
    apikey = 'a' * 32

    # Initializes the plugin with devices set to a string
    plugins.NotifyJoin(apikey=apikey, targets=group)

    # Initializes the plugin with devices set to None
    plugins.NotifyJoin(apikey=apikey, targets=None)

    # Initializes the plugin with an invalid apikey
    with pytest.raises(TypeError):
        plugins.NotifyJoin(apikey=None)

    # Whitespace also acts as an invalid apikey
    with pytest.raises(TypeError):
        plugins.NotifyJoin(apikey="   ")

    # Initializes the plugin with devices set to a set
    p = plugins.NotifyJoin(apikey=apikey, targets=[group, device])

    # Prepare our mock responses
    req = requests.Request()
    req.status_code = requests.codes.created
    req.content = ''
    mock_get.return_value = req
    mock_post.return_value = req

    # Test notifications without a body or a title; nothing to send
    # so we return False
    p.notify(body=None, title=None, notify_type=NotifyType.INFO) is False


def test_notify_kumulos_plugin():
    """
    API: NotifyKumulos() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Invalid API Key
    with pytest.raises(TypeError):
        plugins.NotifyKumulos(None, None)
    with pytest.raises(TypeError):
        plugins.NotifyKumulos("     ", None)

    # Invalid Server Key
    with pytest.raises(TypeError):
        plugins.NotifyKumulos("abcd", None)
    with pytest.raises(TypeError):
        plugins.NotifyKumulos("abcd", "       ")


def test_notify_mattermost_plugin():
    """
    API: NotifyMatterMost() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Invalid Authorization Token
    with pytest.raises(TypeError):
        plugins.NotifyMatterMost(None)
    with pytest.raises(TypeError):
        plugins.NotifyMatterMost("     ")


@mock.patch('requests.post')
def test_notify_messagebird_plugin(mock_post):
    """
    API: NotifyMessageBird() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Prepare our response
    response = requests.Request()
    response.status_code = requests.codes.ok

    # Prepare Mock
    mock_post.return_value = response

    # Initialize some generic (but valid) tokens
    # authkey = '{}'.format('a' * 24)
    source = '+1 (555) 123-3456'

    # No apikey specified
    with pytest.raises(TypeError):
        plugins.NotifyMessageBird(apikey=None, source=source)
    with pytest.raises(TypeError):
        plugins.NotifyMessageBird(apikey="     ", source=source)


def test_notify_pover_plugin():
    """
    API: NotifyPushover() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # No token
    with pytest.raises(TypeError):
        plugins.NotifyPushover(token=None)


def test_notify_ryver_plugin():
    """
    API: NotifyRyver() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # No token
    with pytest.raises(TypeError):
        plugins.NotifyRyver(organization="abc", token=None)

    with pytest.raises(TypeError):
        plugins.NotifyRyver(organization="abc", token="  ")

    # No organization
    with pytest.raises(TypeError):
        plugins.NotifyRyver(organization=None, token="abc")

    with pytest.raises(TypeError):
        plugins.NotifyRyver(organization="  ", token="abc")


def test_notify_simplepush_plugin():
    """
    API: NotifySimplePush() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # No token
    with pytest.raises(TypeError):
        plugins.NotifySimplePush(apikey=None)

    with pytest.raises(TypeError):
        plugins.NotifySimplePush(apikey="  ")

    # Bad event
    with pytest.raises(TypeError):
        plugins.NotifySimplePush(apikey="abc", event=object)

    with pytest.raises(TypeError):
        plugins.NotifySimplePush(apikey="abc", event="  ")


def test_notify_zulip_plugin():
    """
    API: NotifyZulip() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # must be 32 characters long
    token = 'a' * 32

    # Invalid organization
    with pytest.raises(TypeError):
        plugins.NotifyZulip(
            botname='test', organization='#', token=token)


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_sendgrid_plugin(mock_post, mock_get):
    """
    API: NotifySendGrid() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # no apikey
    with pytest.raises(TypeError):
        plugins.NotifySendGrid(
            apikey=None, from_email='user@example.com')

    # invalid from email
    with pytest.raises(TypeError):
        plugins.NotifySendGrid(
            apikey='abcd', from_email='!invalid')

    # no email
    with pytest.raises(TypeError):
        plugins.NotifySendGrid(apikey='abcd', from_email=None)

    # Invalid To email address
    plugins.NotifySendGrid(
        apikey='abcd', from_email='user@example.com', targets="!invalid")

    # Test invalid bcc/cc entries mixed with good ones
    assert isinstance(plugins.NotifySendGrid(
        apikey='abcd',
        from_email='l2g@example.com',
        bcc=('abc@def.com', '!invalid'),
        cc=('abc@test.org', '!invalid')), plugins.NotifySendGrid)


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_pushbullet_plugin(mock_post, mock_get):
    """
    API: NotifyPushBullet() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Initialize some generic (but valid) tokens
    accesstoken = 'a' * 32

    # Support strings
    recipients = '#chan1,#chan2,device,user@example.com,,,'

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    # Invalid Access Token
    with pytest.raises(TypeError):
        plugins.NotifyPushBullet(accesstoken=None)
    with pytest.raises(TypeError):
        plugins.NotifyPushBullet(accesstoken="     ")

    obj = plugins.NotifyPushBullet(
        accesstoken=accesstoken, targets=recipients)
    assert isinstance(obj, plugins.NotifyPushBullet) is True
    assert len(obj.targets) == 4

    obj = plugins.NotifyPushBullet(accesstoken=accesstoken)
    assert isinstance(obj, plugins.NotifyPushBullet) is True
    # Default is to send to all devices, so there will be a
    # recipient here
    assert len(obj.targets) == 1

    obj = plugins.NotifyPushBullet(accesstoken=accesstoken, targets=set())
    assert isinstance(obj, plugins.NotifyPushBullet) is True
    # Default is to send to all devices, so there will be a
    # recipient here
    assert len(obj.targets) == 1


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_pushed_plugin(mock_post, mock_get):
    """
    API: NotifyPushed() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Chat ID
    recipients = '@ABCDEFG, @DEFGHIJ, #channel, #channel2'

    # Some required input
    app_key = 'ABCDEFG'
    app_secret = 'ABCDEFG'

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    # No application Key specified
    with pytest.raises(TypeError):
        plugins.NotifyPushed(
            app_key=None,
            app_secret=app_secret,
            recipients=None,
        )

    with pytest.raises(TypeError):
        plugins.NotifyPushed(
            app_key="  ",
            app_secret=app_secret,
            recipients=None,
        )
    # No application Secret specified
    with pytest.raises(TypeError):
        plugins.NotifyPushed(
            app_key=app_key,
            app_secret=None,
            recipients=None,
        )

    with pytest.raises(TypeError):
        plugins.NotifyPushed(
            app_key=app_key,
            app_secret="   ",
        )

    # recipients list set to (None) is perfectly fine; in this case it will
    # notify the App
    obj = plugins.NotifyPushed(
        app_key=app_key,
        app_secret=app_secret,
        recipients=None,
    )
    assert isinstance(obj, plugins.NotifyPushed) is True
    assert len(obj.channels) == 0
    assert len(obj.users) == 0

    obj = plugins.NotifyPushed(
        app_key=app_key,
        app_secret=app_secret,
        targets=recipients,
    )
    assert isinstance(obj, plugins.NotifyPushed) is True
    assert len(obj.channels) == 2
    assert len(obj.users) == 2

    # Prepare Mock to fail
    mock_post.return_value.status_code = requests.codes.internal_server_error
    mock_get.return_value.status_code = requests.codes.internal_server_error


def test_notify_pushjet_plugin():
    """
    API: NotifyPushjet() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # No application Key specified
    with pytest.raises(TypeError):
        plugins.NotifyPushjet(secret_key=None)

    with pytest.raises(TypeError):
        plugins.NotifyPushjet(secret_key="  ")


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_pushover_plugin(mock_post, mock_get):
    """
    API: NotifyPushover() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Initialize some generic (but valid) tokens
    token = 'a' * 30
    user_key = 'u' * 30

    invalid_device = 'd' * 35

    # Support strings
    devices = 'device1,device2,,,,%s' % invalid_device

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    # No webhook id specified
    with pytest.raises(TypeError):
        plugins.NotifyPushover(user_key=user_key, webhook_id=None)

    obj = plugins.NotifyPushover(
        user_key=user_key, token=token, targets=devices)
    assert isinstance(obj, plugins.NotifyPushover) is True
    assert len(obj.targets) == 3

    # This call fails because there is 1 invalid device
    assert obj.notify(
        body='body', title='title',
        notify_type=NotifyType.INFO) is False

    obj = plugins.NotifyPushover(user_key=user_key, token=token)
    assert isinstance(obj, plugins.NotifyPushover) is True
    # Default is to send to all devices, so there will be a
    # device defined here
    assert len(obj.targets) == 1

    # This call succeeds because all of the devices are valid
    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is True

    obj = plugins.NotifyPushover(user_key=user_key, token=token, targets=set())
    assert isinstance(obj, plugins.NotifyPushover) is True
    # Default is to send to all devices, so there will be a
    # device defined here
    assert len(obj.targets) == 1

    # No User Key specified
    with pytest.raises(TypeError):
        plugins.NotifyPushover(user_key=None, token="abcd")

    # No Access Token specified
    with pytest.raises(TypeError):
        plugins.NotifyPushover(user_key="abcd", token=None)

    with pytest.raises(TypeError):
        plugins.NotifyPushover(user_key="abcd", token="  ")


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_rocketchat_plugin(mock_post, mock_get):
    """
    API: NotifyRocketChat() Extra Checks

    """
    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Chat ID
    recipients = 'AbcD1245, @l2g, @lead2gold, #channel, #channel2'

    # Authentication
    user = 'myuser'
    password = 'mypass'

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok
    mock_post.return_value.content = ''
    mock_get.return_value.content = ''

    obj = plugins.NotifyRocketChat(
        user=user, password=password, targets=recipients)
    assert isinstance(obj, plugins.NotifyRocketChat) is True
    assert len(obj.channels) == 2
    assert len(obj.users) == 2
    assert len(obj.rooms) == 1

    # No Webhook specified
    with pytest.raises(TypeError):
        obj = plugins.NotifyRocketChat(webhook=None, mode='webhook')

    #
    # Logout
    #
    assert obj.logout() is True

    # Invalid JSON during Login
    mock_post.return_value.content = '{'
    mock_get.return_value.content = '}'
    assert obj.login() is False

    # Prepare Mock to fail
    mock_post.return_value.content = ''
    mock_get.return_value.content = ''
    mock_post.return_value.status_code = requests.codes.internal_server_error
    mock_get.return_value.status_code = requests.codes.internal_server_error

    #
    # Send Notification
    #
    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is False
    assert obj._send(payload='test', notify_type=NotifyType.INFO) is False

    #
    # Logout
    #
    assert obj.logout() is False

    # KeyError handling
    mock_post.return_value.status_code = 999
    mock_get.return_value.status_code = 999

    #
    # Send Notification
    #
    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is False
    assert obj._send(payload='test', notify_type=NotifyType.INFO) is False

    #
    # Logout
    #
    assert obj.logout() is False

    # Generate exceptions
    mock_get.side_effect = requests.ConnectionError(
        0, 'requests.ConnectionError() not handled')
    mock_post.side_effect = mock_get.side_effect

    #
    # Send Notification
    #
    assert obj._send(payload='test', notify_type=NotifyType.INFO) is False

    # Attempt the check again but fake a successful login
    obj.login = mock.Mock()
    obj.login.return_value = True
    assert obj.notify(
        body='body', title='title', notify_type=NotifyType.INFO) is False
    #
    # Logout
    #
    assert obj.logout() is False


def test_notify_overflow_truncate():
    """
    API: Overflow Truncate Functionality Testing

    """
    #
    # A little preparation
    #

    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Number of characters per line
    row = 24

    # Some variables we use to control the data we work with
    body_len = 1024
    title_len = 1024

    # Create a large body and title with random data
    body = ''.join(choice(str_alpha + str_num + ' ') for _ in range(body_len))
    body = '\r\n'.join([body[i: i + row] for i in range(0, len(body), row)])

    # the new lines add a large amount to our body; lets force the content
    # back to being 1024 characters.
    body = body[0:1024]

    # Create our title using random data
    title = ''.join(choice(str_alpha + str_num) for _ in range(title_len))

    #
    # First Test: Truncated Title
    #
    class TestNotification(NotifyBase):

        # Test title max length
        title_maxlen = 10

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # We should throw an exception because our specified overflow is wrong.
    with pytest.raises(TypeError):
        # Load our object
        obj = TestNotification(overflow='invalid')

    # Load our object
    obj = TestNotification(overflow=OverflowMode.TRUNCATE)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched
    chunks = obj._apply_overflow(body=body, title=title, overflow=None)
    chunks = obj._apply_overflow(
        body=body, title=title, overflow=OverflowMode.SPLIT)
    assert len(chunks) == 1
    assert body.rstrip() == chunks[0].get('body')
    assert title[0:TestNotification.title_maxlen] == chunks[0].get('title')

    #
    # Next Test: Line Count Control
    #

    class TestNotification(NotifyBase):

        # Test title max length
        title_maxlen = 5

        # Maximum number of lines
        body_max_line_count = 5

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # Load our object
    obj = TestNotification(overflow=OverflowMode.TRUNCATE)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched
    chunks = obj._apply_overflow(body=body, title=title)
    assert len(chunks) == 1
    assert len(chunks[0].get('body').split('\n')) == \
        TestNotification.body_max_line_count
    assert title[0:TestNotification.title_maxlen] == chunks[0].get('title')

    #
    # Next Test: Truncated body
    #

    class TestNotification(NotifyBase):

        # Test title max length
        title_maxlen = title_len

        # Enforce a body length of just 10
        body_maxlen = 10

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # Load our object
    obj = TestNotification(overflow=OverflowMode.TRUNCATE)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched
    chunks = obj._apply_overflow(body=body, title=title)
    assert len(chunks) == 1
    assert body[0:TestNotification.body_maxlen] == chunks[0].get('body')
    assert title == chunks[0].get('title')

    #
    # Next Test: Append title to body + Truncated body
    #

    class TestNotification(NotifyBase):

        # Enforce no title
        title_maxlen = 0

        # Enforce a body length of just 100
        body_maxlen = 100

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # Load our object
    obj = TestNotification(overflow=OverflowMode.TRUNCATE)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched

    obj.notify_format = NotifyFormat.HTML
    chunks = obj._apply_overflow(body=body, title=title)
    assert len(chunks) == 1

    obj.notify_format = NotifyFormat.MARKDOWN
    chunks = obj._apply_overflow(body=body, title=title)
    assert len(chunks) == 1

    obj.notify_format = NotifyFormat.TEXT
    chunks = obj._apply_overflow(body=body, title=title)
    assert len(chunks) == 1

    # The below line should be read carefully... We're actually testing to see
    # that our title is matched against our body. Behind the scenes, the title
    # was appended to the body. The body was then truncated to the maxlen.
    # The thing is, since the title is so large, all of the body was lost
    # and a good chunk of the title was too.  The message sent will just be a
    # small portion of the title
    assert len(chunks[0].get('body')) == TestNotification.body_maxlen
    assert title[0:TestNotification.body_maxlen] == chunks[0].get('body')


def test_notify_overflow_split():
    """
    API: Overflow Split Functionality Testing

    """

    #
    # A little preparation
    #

    # Disable Throttling to speed testing
    plugins.NotifyBase.request_rate_per_sec = 0

    # Number of characters per line
    row = 24

    # Some variables we use to control the data we work with
    body_len = 1024
    title_len = 1024

    # Create a large body and title with random data
    body = ''.join(choice(str_alpha + str_num) for _ in range(body_len))
    body = '\r\n'.join([body[i: i + row] for i in range(0, len(body), row)])

    # the new lines add a large amount to our body; lets force the content
    # back to being 1024 characters.
    body = body[0:1024]

    # Create our title using random data
    title = ''.join(choice(str_alpha + str_num) for _ in range(title_len))

    #
    # First Test: Truncated Title
    #
    class TestNotification(NotifyBase):

        # Test title max length
        title_maxlen = 10

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # Load our object
    obj = TestNotification(overflow=OverflowMode.SPLIT)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched
    chunks = obj._apply_overflow(body=body, title=title)
    assert len(chunks) == 1
    assert body == chunks[0].get('body')
    assert title[0:TestNotification.title_maxlen] == chunks[0].get('title')

    #
    # Next Test: Line Count Control
    #

    class TestNotification(NotifyBase):

        # Test title max length
        title_maxlen = 5

        # Maximum number of lines
        body_max_line_count = 5

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # Load our object
    obj = TestNotification(overflow=OverflowMode.SPLIT)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched
    chunks = obj._apply_overflow(body=body, title=title)
    assert len(chunks) == 1
    assert len(chunks[0].get('body').split('\n')) == \
        TestNotification.body_max_line_count
    assert title[0:TestNotification.title_maxlen] == chunks[0].get('title')

    #
    # Next Test: Split body
    #

    class TestNotification(NotifyBase):

        # Test title max length
        title_maxlen = title_len

        # Enforce a body length
        # Wrap in int() so Python v3 doesn't convert the response into a float
        body_maxlen = int(body_len / 4)

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # Load our object
    obj = TestNotification(overflow=OverflowMode.SPLIT)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched
    chunks = obj._apply_overflow(body=body, title=title)
    offset = 0
    assert len(chunks) == 4
    for chunk in chunks:
        # Our title never changes
        assert title == chunk.get('title')

        # Our body is only broken up; not lost
        _body = chunk.get('body')
        assert body[offset: len(_body) + offset].rstrip() == _body
        offset += len(_body)

    #
    # Next Test: Append title to body + split body
    #

    class TestNotification(NotifyBase):

        # Enforce no title
        title_maxlen = 0

        # Enforce a body length based on the title
        # Wrap in int() so Python v3 doesn't convert the response into a float
        body_maxlen = int(title_len / 4)

        def __init__(self, *args, **kwargs):
            super(TestNotification, self).__init__(**kwargs)

        def notify(self, *args, **kwargs):
            # Pretend everything is okay
            return True

    # Load our object
    obj = TestNotification(overflow=OverflowMode.SPLIT)
    assert obj is not None

    # Verify that we break the title to a max length of our title_max
    # and that the body remains untouched
    chunks = obj._apply_overflow(body=body, title=title)

    # Our final product is that our title has been appended to our body to
    # create one great big body. As a result we'll get quite a few lines back
    # now.
    offset = 0

    # Our body will look like this in small chunks at the end of the day
    bulk = title + '\r\n' + body

    # Due to the new line added to the end
    assert len(chunks) == (
        # wrap division in int() so Python 3 doesn't convert it to a float on
        # us
        int(len(bulk) / TestNotification.body_maxlen) +
        (1 if len(bulk) % TestNotification.body_maxlen else 0))

    for chunk in chunks:
        # Our title is empty every time
        assert chunk.get('title') == ''

        _body = chunk.get('body')
        assert bulk[offset: len(_body) + offset] == _body
        offset += len(_body)
