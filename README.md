![Apprise Logo](https://raw.githubusercontent.com/caronc/apprise/master/apprise/assets/themes/default/apprise-logo.png)

<hr/>

**ap·prise** / *verb*<br/>
To inform or tell (someone). To make one aware of something.
<hr/>

*Apprise* allows you to send a notification to *almost* all of the most popular *notification* services available to us today such as: Telegram, Discord, Slack, Amazon SNS, Gotify, etc.

* One notification library to rule them all.
* A common and intuitive notification syntax.
* Supports the handling of images and attachments (to the notification services that will accept them).

System owners who wish to provide a notification service no longer need to research each and every new one as they appear. They just need to include this one library and then they can immediately gain access to almost all of the notifications services available to us today.

System Administrators who wish to send a notification from a scheduled task or from the command line also no longer need to find the right tool for the job.  Everything is already wrapped and supported within the *apprise* script that ships with this product.

[![Paypal](https://img.shields.io/badge/paypal-donate-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=MHANV39UZNQ5E)
[![Follow](https://img.shields.io/twitter/follow/l2gnux)](https://twitter.com/l2gnux/)<br/>
[![Discord](https://img.shields.io/discord/558793703356104724.svg?colorB=7289DA&label=Discord&logo=Discord&logoColor=7289DA&style=flat-square)](https://discord.gg/MMPeN2D)
[![Python](https://img.shields.io/pypi/pyversions/apprise.svg?style=flat-square)](https://pypi.org/project/apprise/)
[![Build Status](https://travis-ci.org/caronc/apprise.svg?branch=master)](https://travis-ci.org/caronc/apprise)
[![CodeCov Status](https://codecov.io/github/caronc/apprise/branch/master/graph/badge.svg)](https://codecov.io/github/caronc/apprise)
[![PyPi](https://img.shields.io/pypi/dm/apprise.svg?style=flat-square)](https://pypi.org/project/apprise/)

## Supported Notifications
The section identifies all of the services supported by this library. [Check out the wiki for more information on the supported modules here](https://github.com/caronc/apprise/wiki).

### Popular Notification Services
The table below identifies the services this tool supports and some example service urls you need to use in order to take advantage of it. Click on any of the services listed below to get more details on how you can configure Apprise to access them.

| Notification Service | Service ID | Default Port | Example Syntax |
| -------------------- | ---------- | ------------ | -------------- |
| [Boxcar](https://github.com/caronc/apprise/wiki/Notify_boxcar)  | boxcar://   | (TCP) 443   | boxcar://hostname<br />boxcar://hostname/@tag<br/>boxcar://hostname/device_token<br />boxcar://hostname/device_token1/device_token2/device_tokenN<br />boxcar://hostname/@tag/@tag2/device_token
| [DingTalk](https://github.com/caronc/apprise/wiki/Notify_dingtalk)  | dingtalk://   | (TCP) 443   | dingtalk://token/<br />dingtalk://token/ToPhoneNo<br />dingtalk://token/ToPhoneNo1/ToPhoneNo2/ToPhoneNo1/
| [Discord](https://github.com/caronc/apprise/wiki/Notify_discord)  | discord://   | (TCP) 443   | discord://webhook_id/webhook_token<br />discord://avatar@webhook_id/webhook_token
| [Dbus](https://github.com/caronc/apprise/wiki/Notify_dbus)  | dbus://<br />qt://<br />glib://<br />kde://  | n/a  | dbus://<br />qt://<br />glib://<br />kde://
| [Emby](https://github.com/caronc/apprise/wiki/Notify_emby)  | emby:// or embys:// | (TCP) 8096 | emby://user@hostname/<br />emby://user:password@hostname
| [Enigma2](https://github.com/caronc/apprise/wiki/Notify_enigma2)  | enigma2:// or enigma2s:// | (TCP) 80 or 443 | enigma2://hostname
| [Faast](https://github.com/caronc/apprise/wiki/Notify_faast) | faast://    | (TCP) 443    | faast://authorizationtoken
| [Flock](https://github.com/caronc/apprise/wiki/Notify_flock) | flock://    | (TCP) 443    | flock://token<br/>flock://botname@token<br/>flock://app_token/u:userid<br/>flock://app_token/g:channel_id<br/>flock://app_token/u:userid/g:channel_id
| [Gitter](https://github.com/caronc/apprise/wiki/Notify_gitter) | gitter://    | (TCP) 443    | gitter://token/room<br/>gitter://token/room1/room2/roomN
| [Gnome](https://github.com/caronc/apprise/wiki/Notify_gnome) | gnome://    |        n/a          | gnome://
| [Gotify](https://github.com/caronc/apprise/wiki/Notify_gotify) | gotify:// or gotifys://   | (TCP) 80 or 443    | gotify://hostname/token<br />gotifys://hostname/token?priority=high
| [Growl](https://github.com/caronc/apprise/wiki/Notify_growl)  | growl://   | (UDP) 23053   | growl://hostname<br />growl://hostname:portno<br />growl://password@hostname<br />growl://password@hostname:port</br>**Note**: you can also use the get parameter _version_ which can allow the growl request to behave using the older v1.x protocol. An example would look like: growl://hostname?version=1
| [IFTTT](https://github.com/caronc/apprise/wiki/Notify_ifttt) | ifttt://    | (TCP) 443    | ifttt://webhooksID/Event<br />ifttt://webhooksID/Event1/Event2/EventN<br/>ifttt://webhooksID/Event1/?+Key=Value<br/>ifttt://webhooksID/Event1/?-Key=value1
| [Join](https://github.com/caronc/apprise/wiki/Notify_join) | join://   | (TCP) 443    | join://apikey/device<br />join://apikey/device1/device2/deviceN/<br />join://apikey/group<br />join://apikey/groupA/groupB/groupN<br />join://apikey/DeviceA/groupA/groupN/DeviceN/
| [KODI](https://github.com/caronc/apprise/wiki/Notify_kodi) | kodi:// or kodis://    | (TCP) 8080 or 443   | kodi://hostname<br />kodi://user@hostname<br />kodi://user:password@hostname:port
| [Kumulos](https://github.com/caronc/apprise/wiki/Notify_kumulos) | kumulos:// | (TCP) 443 | kumulos://apikey/serverkey
| [Mailgun](https://github.com/caronc/apprise/wiki/Notify_mailgun) | mailgun:// | (TCP) 443 | mailgun://user@hostname/apikey<br />mailgun://user@hostname/apikey/email<br />mailgun://user@hostname/apikey/email1/email2/emailN<br />mailgun://user@hostname/apikey/?name="From%20User"
| [Matrix](https://github.com/caronc/apprise/wiki/Notify_matrix) | matrix:// or matrixs://  | (TCP) 80 or 443 | matrix://hostname<br />matrix://user@hostname<br />matrixs://user:pass@hostname:port/#room_alias<br />matrixs://user:pass@hostname:port/!room_id<br />matrixs://user:pass@hostname:port/#room_alias/!room_id/#room2<br />matrixs://token@hostname:port/?webhook=matrix<br />matrix://user:token@hostname/?webhook=slack&format=markdown
| [Mattermost](https://github.com/caronc/apprise/wiki/Notify_mattermost) | mmost://  | (TCP) 8065 | mmost://hostname/authkey<br />mmost://hostname:80/authkey<br />mmost://user@hostname:80/authkey<br />mmost://hostname/authkey?channel=channel<br />mmosts://hostname/authkey<br />mmosts://user@hostname/authkey<br />
| [Microsoft Teams](https://github.com/caronc/apprise/wiki/Notify_msteams) | msteams://  | (TCP) 443   | msteams://TokenA/TokenB/TokenC/
| [Nextcloud](https://github.com/caronc/apprise/wiki/Notify_nextcloud) | ncloud:// or nclouds:// | (TCP) 80 or 443 | ncloud://adminuser:pass@host/User<br/>nclouds://adminuser:pass@host/User1/User2/UserN
| [Notica](https://github.com/caronc/apprise/wiki/Notify_notica) | notica://  | (TCP) 443   | notica://Token/
| [Notifico](https://github.com/caronc/apprise/wiki/Notify_notifico) | notifico://  | (TCP) 443   | notifico://ProjectID/MessageHook/
| [Prowl](https://github.com/caronc/apprise/wiki/Notify_prowl) | prowl://   | (TCP) 443    | prowl://apikey<br />prowl://apikey/providerkey
| [PushBullet](https://github.com/caronc/apprise/wiki/Notify_pushbullet) | pbul://    | (TCP) 443    | pbul://accesstoken<br />pbul://accesstoken/#channel<br/>pbul://accesstoken/A_DEVICE_ID<br />pbul://accesstoken/email@address.com<br />pbul://accesstoken/#channel/#channel2/email@address.net/DEVICE
| [Pushjet](https://github.com/caronc/apprise/wiki/Notify_pushjet) | pjet:// or pjets:// | (TCP) 80 or 443 | pjet://hostname/secret<br />pjet://hostname:port/secret<br />pjets://secret@hostname/secret<br />pjets://hostname:port/secret
| [Push (Techulus)](https://github.com/caronc/apprise/wiki/Notify_techulus) | push://    | (TCP) 443    | push://apikey/
| [Pushed](https://github.com/caronc/apprise/wiki/Notify_pushed) | pushed://    | (TCP) 443    | pushed://appkey/appsecret/<br/>pushed://appkey/appsecret/#ChannelAlias<br/>pushed://appkey/appsecret/#ChannelAlias1/#ChannelAlias2/#ChannelAliasN<br/>pushed://appkey/appsecret/@UserPushedID<br/>pushed://appkey/appsecret/@UserPushedID1/@UserPushedID2/@UserPushedIDN
| [Pushover](https://github.com/caronc/apprise/wiki/Notify_pushover)  | pover://   | (TCP) 443   | pover://user@token<br />pover://user@token/DEVICE<br />pover://user@token/DEVICE1/DEVICE2/DEVICEN<br />**Note**: you must specify both your user_id and token
| [PushSafer](https://github.com/caronc/apprise/wiki/Notify_pushsafer)  | psafer:// or psafers://  | (TCP) 80 or 443  | psafer://privatekey<br />psafers://privatekey/DEVICE<br />psafer://privatekey/DEVICE1/DEVICE2/DEVICEN
| [Rocket.Chat](https://github.com/caronc/apprise/wiki/Notify_rocketchat) | rocket:// or rockets://  | (TCP) 80 or 443   | rocket://user:password@hostname/RoomID/Channel<br />rockets://user:password@hostname:443/#Channel1/#Channel1/RoomID<br />rocket://user:password@hostname/#Channel<br />rocket://webhook@hostname<br />rockets://webhook@hostname/@User/#Channel
| [Ryver](https://github.com/caronc/apprise/wiki/Notify_ryver) | ryver://  | (TCP) 443   | ryver://Organization/Token<br />ryver://botname@Organization/Token
| [SendGrid](https://github.com/caronc/apprise/wiki/Notify_sendgrid) | sendgrid://  | (TCP) 443   | sendgrid://APIToken:FromEmail/<br />sendgrid://APIToken:FromEmail/ToEmail<br />sendgrid://APIToken:FromEmail/ToEmail1/ToEmail2/ToEmailN/
| [SimplePush](https://github.com/caronc/apprise/wiki/Notify_simplepush) | spush://   | (TCP) 443    | spush://apikey<br />spush://salt:password@apikey<br />spush://apikey?event=Apprise
| [Slack](https://github.com/caronc/apprise/wiki/Notify_slack) | slack://  | (TCP) 443   | slack://TokenA/TokenB/TokenC/<br />slack://TokenA/TokenB/TokenC/Channel<br />slack://botname@TokenA/TokenB/TokenC/Channel<br />slack://user@TokenA/TokenB/TokenC/Channel1/Channel2/ChannelN
| [Syslog](https://github.com/caronc/apprise/wiki/Notify_syslog) | syslog://  | n/a  | syslog://<br />syslog://Facility
| [Telegram](https://github.com/caronc/apprise/wiki/Notify_telegram) | tgram://  | (TCP) 443   | tgram://bottoken/ChatID<br />tgram://bottoken/ChatID1/ChatID2/ChatIDN
| [Twitter](https://github.com/caronc/apprise/wiki/Notify_twitter) | twitter://  | (TCP) 443   | twitter://CKey/CSecret/AKey/ASecret<br/>twitter://user@CKey/CSecret/AKey/ASecret<br/>twitter://CKey/CSecret/AKey/ASecret/User1/User2/User2<br/>twitter://CKey/CSecret/AKey/ASecret?mode=tweet
| [Twist](https://github.com/caronc/apprise/wiki/Notify_twist) | twist://  | (TCP) 443   | twist://pasword:login<br/>twist://password:login/#channel<br/>twist://password:login/#team:channel<br/>twist://password:login/#team:channel1/channel2/#team3:channel
| [XBMC](https://github.com/caronc/apprise/wiki/Notify_xbmc) | xbmc:// or xbmcs://    | (TCP) 8080 or 443   | xbmc://hostname<br />xbmc://user@hostname<br />xbmc://user:password@hostname:port
| [XMPP](https://github.com/caronc/apprise/wiki/Notify_xmpp) | xmpp:// or xmpps://    | (TCP) 5222 or 5223   | xmpp://password@hostname<br />xmpp://user:password@hostname<br />xmpps://user:password@hostname:port?jid=user@hostname/resource<br/>xmpps://password@hostname/target@myhost, target2@myhost/resource
| [Windows Notification](https://github.com/caronc/apprise/wiki/Notify_windows) | windows://    |        n/a          | windows://
| [Webex Teams (Cisco)](https://github.com/caronc/apprise/wiki/Notify_wxteams) | wxteams://  | (TCP) 443   | wxteams://Token
| [Zulip Chat](https://github.com/caronc/apprise/wiki/Notify_zulip) | zulip://  | (TCP) 443   | zulip://botname@Organization/Token<br />zulip://botname@Organization/Token/Channel<br />zulip://botname@Organization/Token/Email


### SMS Notification Support
| Notification Service | Service ID | Default Port | Example Syntax |
| -------------------- | ---------- | ------------ | -------------- |
| [AWS SNS](https://github.com/caronc/apprise/wiki/Notify_sns)  | sns://   | (TCP) 443   | sns://AccessKeyID/AccessSecretKey/RegionName/+PhoneNo<br/>sns://AccessKeyID/AccessSecretKey/RegionName/+PhoneNo1/+PhoneNo2/+PhoneNoN<br/>sns://AccessKeyID/AccessSecretKey/RegionName/Topic<br/>sns://AccessKeyID/AccessSecretKey/RegionName/Topic1/Topic2/TopicN
| [ClickSend](https://github.com/caronc/apprise/wiki/Notify_clicksend) | clicksend://  | (TCP) 443   | clicksend://user:pass@PhoneNo<br/>clicksend://user:pass@ToPhoneNo1/ToPhoneNo2/ToPhoneNoN
| [D7 Networks](https://github.com/caronc/apprise/wiki/Notify_d7networks) | d7sms://  | (TCP) 443   | d7sms://user:pass@PhoneNo<br/>d7sms://user:pass@ToPhoneNo1/ToPhoneNo2/ToPhoneNoN
| [MessageBird](https://github.com/caronc/apprise/wiki/Notify_messagebird) | msgbird://  | (TCP) 443   | msgbird://ApiKey/FromPhoneNo<br/>msgbird://ApiKey/FromPhoneNo/ToPhoneNo<br/>msgbird://ApiKey/FromPhoneNo/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/
| [MSG91](https://github.com/caronc/apprise/wiki/Notify_msg91) | msg91://  | (TCP) 443   | msg91://AuthKey/ToPhoneNo<br/>msg91://SenderID@AuthKey/ToPhoneNo<br/>msg91://AuthKey/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/
| [Nexmo](https://github.com/caronc/apprise/wiki/Notify_nexmo) | nexmo://  | (TCP) 443   | nexmo://ApiKey:ApiSecret@FromPhoneNo<br/>nexmo://ApiKey:ApiSecret@FromPhoneNo/ToPhoneNo<br/>nexmo://ApiKey:ApiSecret@FromPhoneNo/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/
| [Sinch](https://github.com/caronc/apprise/wiki/Notify_sinch) | sinch://  | (TCP) 443   | sinch://ServicePlanId:ApiToken@FromPhoneNo<br/>sinch://ServicePlanId:ApiToken@FromPhoneNo/ToPhoneNo<br/>sinch://ServicePlanId:ApiToken@FromPhoneNo/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/<br/>sinch://ServicePlanId:ApiToken@ShortCode/ToPhoneNo<br/>sinch://ServicePlanId:ApiToken@ShortCode/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/
| [Twilio](https://github.com/caronc/apprise/wiki/Notify_twilio) | twilio://  | (TCP) 443   | twilio://AccountSid:AuthToken@FromPhoneNo<br/>twilio://AccountSid:AuthToken@FromPhoneNo/ToPhoneNo<br/>twilio://AccountSid:AuthToken@FromPhoneNo/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/<br/>twilio://AccountSid:AuthToken@ShortCode/ToPhoneNo<br/>twilio://AccountSid:AuthToken@ShortCode/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/

### Email Support
| Service ID | Default Port | Example Syntax |
| ---------- | ------------ | -------------- |
| [mailto://](https://github.com/caronc/apprise/wiki/Notify_email)  |  (TCP) 25    | mailto://userid:pass@domain.com<br />mailto://domain.com?user=userid&pass=password<br/>mailto://domain.com:2525?user=userid&pass=password<br />mailto://user@gmail.com&pass=password<br />mailto://mySendingUsername:mySendingPassword@example.com?to=receivingAddress@example.com<br />mailto://userid:password@example.com?smtp=mail.example.com&from=noreply@example.com&name=no%20reply
| [mailtos://](https://github.com/caronc/apprise/wiki/Notify_email) |  (TCP) 587   | mailtos://userid:pass@domain.com<br />mailtos://domain.com?user=userid&pass=password<br/>mailtos://domain.com:465?user=userid&pass=password<br />mailtos://user@hotmail.com&pass=password<br />mailtos://mySendingUsername:mySendingPassword@example.com?to=receivingAddress@example.com<br />mailtos://userid:password@example.com?smtp=mail.example.com&from=noreply@example.com&name=no%20reply

Apprise have some email services built right into it (such as yahoo, fastmail, hotmail, gmail, etc) that greatly simplify the mailto:// service.  See more details [here](https://github.com/caronc/apprise/wiki/Notify_email).

### Custom Notifications
| Post Method          | Service ID | Default Port | Example Syntax |
| -------------------- | ---------- | ------------ | -------------- |
| [JSON](https://github.com/caronc/apprise/wiki/Notify_Custom_JSON)       | json:// or jsons://   | (TCP) 80 or 443 | json://hostname<br />json://user@hostname<br />json://user:password@hostname:port<br />json://hostname/a/path/to/post/to
| [XML](https://github.com/caronc/apprise/wiki/Notify_Custom_XML)         | xml:// or xmls://   | (TCP) 80 or 443 | xml://hostname<br />xml://user@hostname<br />xml://user:password@hostname:port<br />xml://hostname/a/path/to/post/to

## Installation
The easiest way is to install this package is from pypi:
```bash
pip install apprise
```
## Command Line
A small command line tool is also provided with this package called *apprise*. If you know the server url's you wish to notify, you can simply provide them all on the command line and send your notifications that way:
```bash
# Send a notification to as many servers as you want
# as you can easily chain one after another:
apprise -t 'my title' -b 'my notification body' \
   'mailto://myemail:mypass@gmail.com' \
   'pbul://o.gn5kj6nfhv736I7jC3cj3QLRiyhgl98b'

# If you don't specify a --body (-b) then stdin is used allowing
# you to use the tool as part of your every day administration:
cat /proc/cpuinfo | apprise -t 'cpu info' \
      'mailto://myemail:mypass@gmail.com'

# The title field is totally optional
uptime | apprise \
 'discord:///4174216298/JHMHI8qBe7bk2ZwO5U711o3dV_js'
```

### Configuration Files
No one wants to put there credentials out for everyone to see on the command line.  No problem *apprise* also supports configuration files.  It can handle both a specific [YAML format](https://github.com/caronc/apprise/wiki/config_yaml) or a very simple [TEXT format](https://github.com/caronc/apprise/wiki/config_text). You can also pull these configuration files via an HTTP query too! You can read more about the expected structure of the configuration files [here](https://github.com/caronc/apprise/wiki/config).
```bash
# By default if no url or configuration is specified aprise will attempt to load
# configuration files (if present):
#  ~/.apprise
#  ~/.apprise.yml
#  ~/.config/apprise
#  ~/.config/apprise.yml

# Windows users can store their default configuration files here:
#  %APPDATA%/Apprise/apprise
#  %APPDATA%/Apprise/apprise.yml
#  %LOCALAPPDATA%/Apprise/apprise
#  %LOCALAPPDATA%/Apprise/apprise.yml

# If you loaded one of those files, your command line gets really easy:
apprise -t 'my title' -b 'my notification body'

# If you want to deviate from the default paths or specify more than one,
# just specify them using the --config switch:
apprise -t 'my title' -b 'my notification body' \
	--config=/path/to/my/config.yml

# Got lots of configuration locations? No problem, you can specify them all:
# Apprise can even fetch the configuration from over a network!
apprise -t 'my title' -b 'my notification body' \
	--config=/path/to/my/config.yml \
	--config=https://localhost/my/apprise/config
```

### Attaching Files
Apprise also supports file attachments too! Specify as many attachments to a notification as you want.
```bash
# Send a funny image you found on the internet to a colleague:
apprise --title 'Agile Joke' \
        --body 'Did you see this one yet?' \
        --attach https://i.redd.it/my2t4d2fx0u31.jpg \
      'mailto://myemail:mypass@gmail.com'

# Easily send an update from a critical server to your dev team
apprise --title 'system crash' \
        --body 'I do not think Jim fixed the bug; see attached...' \
        --attach /var/log/myprogram.log \
        --attach /var/debug/core.2345 \
        --tag devteam
```

## Developers
To send a notification from within your python application, just do the following:
```python
import apprise

# Create an Apprise instance
apobj = apprise.Apprise()

# Add all of the notification services by their server url.
# A sample email notification:
apobj.add('mailto://myuserid:mypass@gmail.com')

# A sample pushbullet notification
apobj.add('pbul://o.gn5kj6nfhv736I7jC3cj3QLRiyhgl98b')

# Then notify these services any time you desire. The below would
# notify all of the services loaded into our Apprise object.
apobj.notify(
    body='what a great notification service!',
    title='my notification title',
)
```

### Configuration Files
Developers need access to configuration files too. The good news is their use just involves declaring another object (called *AppriseConfig*) that the *Apprise* object can ingest.  You can also freely mix and match config and notification entries as often as you wish! You can read more about the expected structure of the configuration files [here](https://github.com/caronc/apprise/wiki/config).
```python
import apprise

# Create an Apprise instance
apobj = apprise.Apprise()

# Create an Config instance
config = apprise.AppriseConfig()

# Add a configuration source:
config.add('/path/to/my/config.yml')

# Add another...
config.add('https://myserver:8080/path/to/config')

# Make sure to add our config into our apprise object
apobj.add(config)

# You can mix and match; add an entry directly if you want too
# In this entry we associate the 'admin' tag with our notification
apobj.add('mailto://myuser:mypass@hotmail.com', tag='admin')

# Then notify these services any time you desire. The below would
# notify all of the services that have not been bound to any specific
# tag.
apobj.notify(
    body='what a great notification service!',
    title='my notification title',
)

# Tagging allows you to specifically target only specific notification
# services you've loaded:
apobj.notify(
    body='send a notification to our admin group'
    title='Attention Admins',
    # notify any services tagged with the 'admin' tag
    tag='admin',
)

# If you want to notify absolutely everything (reguardless of whether
# it's been tagged or not), just use the reserved tag of 'all':
apobj.notify(
    body='send a notification to our admin group'
    title='Attention Admins',
    # notify absolutely everything loaded, reguardless on wether
    # it has a tag associated with it or not:
    tag='all',
)
```

### Attaching Files
Attachments are very easy to send using the Apprise API:
```python
import apprise

# Create an Apprise instance
apobj = apprise.Apprise()

# Add at least one service you want to notify
apobj.add('mailto://myuser:mypass@hotmail.com')

# Then send your attachment.
apobj.notify(
    title='A great photo of our family',
    body='The flash caused Jane to close her eyes! hah! :)',
    attach='/local/path/to/my/DSC_003.jpg',
)

# Send a web based attachment too! In the below example, we connect to a home
# security camera and send a live image to an email. By default remote web
# content is cached but for a security camera, we might want to call notify
# again later in our code so we want our last image retrieved to expire(in
# this case after 3 seconds).
apobj.notify(
    title='Latest security image',
    attach='http:/admin:password@hikvision-cam01/ISAPI/Streaming/channels/101/picture?cache=3'
)
```

To send more than one attachment, you just need the **AppriseAttachment** object:
```python
import apprise

# Create an Apprise instance
apobj = apprise.Apprise()

# Add at least one service you want to notify
apobj.add('mailto://myuser:mypass@hotmail.com')

# Initialize our attachment object
attachment = apprise.AppriseAttachment()

# Now add all of the entries we're intrested in:
# ?name= allows us to rename the actual jpeg as found on the site
# to be another name when sent to our receipient(s)
attachment.add('https://i.redd.it/my2t4d2fx0u31.jpg?name=FlyingToMars.jpg')

# Now add another:
attachment.add('/path/to/funny/joke.gif')

# Send your multiple attachments with a single notify call:
apobj.notify(
    title='Some good jokes.'
    body='Hey guys, check out these!'
    attach=attachment,
)
```

## Want To Learn More?
If you're interested in reading more about this and other methods on how to customize your own notifications, please check out the following links:
* 📣 [Using the CLI](https://github.com/caronc/apprise/wiki/CLI_Usage)
* 🛠️ [Development API](https://github.com/caronc/apprise/wiki/Development_API)
* 🔧 [Troubleshooting](https://github.com/caronc/apprise/wiki/Troubleshooting)
* ⚙️ [Configuration File Help](https://github.com/caronc/apprise/wiki/config)
* 🌎 [Apprise API/Web Interface](https://github.com/caronc/apprise-api)
* 🎉 [Showcase](https://github.com/caronc/apprise/wiki/showcase)

Want to help Apprise get better?
* 💡 [Contribute to the Apprise Code Base](https://github.com/caronc/apprise/wiki/Development_Contribution)
* ❤️ [Sponsorship and Donations](https://github.com/caronc/apprise/wiki/Sponsors)
