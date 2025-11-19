NO LONGER MAINTAINED

\*\*\*\*\*\*\* ALL USERS PLEASE READ \*\*\*\*\*\*\*

UPDATE TO POWER KEYS..
In order to remove confusion of what TV supports what power keys.
I have decided to alter the Samsung handling of keys. The way Samsung
had them set up seemed to cause to much confusion. I think that everyone
will like this way better.

KEY_POWER = toggle. This is going to toggle the power. so if the TV is
off it will turn it on. and if it is on it will turn it off.

KEY_POWERON = Discrete power on. this will always turn the TV on
if it is off.

KEY_POWEROFF = You guessed it. Discrete power off. If the TV is on
this will turn it off.


This is a much easier mechanism and a whole lot easier to grasp. so no
matter what TV you have and what key it supports no longer matters.
This is what these keys will do. plain and simple.


PLEASE READ

The library has be updated and added to. There is a plethora of new
features as well as some changes to the old ones.
Be sure to read this documentation in it's entirety.

If you ask a question and the answer is in this documentation the only
thing I am going to say is `Read the documentation`.

So it is my suggestion that you do exactly that before posting any kind
of an issue.

<br></br>

\*\*\*\*\*\*\* LEGACY TV OWNERS (TV's older then 2014) PLEASE READ \*\*\*\*\*\*\*

DO NOT POST AN ISSUE ABOUT THE TV NOT POWERING ON THE TV DOES NOT SUPPORT IT!!!!
<br></br>

**SAMSUNGCTL**
==========
BIG NEWS!!!!
samsungctl now supports the ever elusive H and J model year (2014 and 2015) TV's

<br></br>
I want to give a thanks to the people that helped in the bug testing
of this version. It has been a bit of a challenge because of the different
devices/OS's that samsungctl is running on. In no special order I want to say
TY for the help. If I have missed someone please let me know.

* @eclair4151
* @fluxdigital
* @DJPsycho82
* @sebdbr
* @Murph24
* @davidgurr
* @vitalets
* @msvinth
* @dcorsus
* @xxKeoxx
* @iAbadia
* @raydog153
* @andreas-bulling


Onto the library.

samsungctl is a library and a command line tool for remote controlling
Samsung televisions via a TCP/IP connection. It currently supports
2008+ TVs with Ethernet or Wi-Fi connectivity. That includes the
H and J model year TV's as well as the TV's that have the latest
Samsung firmware that makes use of an SSL based websocket connection.

On all TV's you will be prompted to accept the connection this prompt
gets displayed ON THE TV. You will have 30 seconds to do this before it
errors out. There is a slight variation to this, on 2014 and 2015 year
TV's (H and J) a pin will be displayed ON THE TV that will have to be
entered when prompted to ON YOUR PC.

This program IS NOT the same one that is available on the Python
Packaging Index (Pypi). I do not have access to that and unfortunately
the original author Ape has been on hiatus for some time. He may no
longer be maintaining the library.

So for the time being you will need to clone this repository and
install it using the directions below.

<br></br>
***Dependencies***
------------------

- Python 2.7+
- `websocket-client`
- `requests`
- `pycryptodome`
- `lxml`
- `ifaddr`
- `six`
- `curses` (optional, for the interactive mode)


<br></br>
***Installation***
------------------
```python setup.py install```
<br></br>
It's possible to use the command line tool without installation:
<br></br>
```python -m samsungctl```

<br></br>
***Command line usage***
------------------------

You can use `samsungctl` command to send keys to a TV:
<br></br>
```samsungctl --host <host> [options] <key> [key ...]```
<br></br>
<br></br>
`host` is the hostname or IP address of the TV. `key` is a key code, e.g.
`KEY_VOLDOWN`. See Key codes.

There is also an interactive mode (ncurses) for sending the key presses:
<br></br>
```samsungctl --host <host> [options] --interactive```
<br></br>
<br></br>
Use `samsungctl --help` for more information about the command line
arguments:
<br></br>
```
usage: samsungctl [-h] [--version] [-v] [-q] [-i] [--host HOST] [--port PORT]
                  [--method METHOD] [--name NAME] [--description DESC]
                  [--id ID] [--token TOKEN] [--timeout TIMEOUT]
                  [--volume VOLUME] [--mute MUTE] [--brightness BRIGHTNESS]
                  [--contrast CONTRAST] [--sharpness SHARPNESS]
                  [--source SOURCE] [--source-label SOURCE_LABEL]
                  [--config-file PATH/FILENAME]
                  [--start-app APP NAME OR ID] [--app-metadata METADATA]
                  [--key-help]
                  [key [key ...]]

Remote control Samsung televisions via TCP/IP connection

positional arguments:
  key                 keys to be sent (e.g. KEY_VOLDOWN)
```
<br></br>
Breakdown of the parameters:
<br></br>

optional argument|description
-----------------|-----------
-h, --help|show this help message and exit
--version|show program's version number and exit
-v, --verbose|increase output verbosity
-q, --quiet|suppress non-fatal output
-i, --interactive|interactive control
--host HOST|TV hostname or IP address
--port PORT|TV port number (TCP)
--method METHOD|Connection method (legacy or websocket)
--name NAME|remote control name
--description DESC|remote control description
--id ID|remote control id
--token TOKEN|Authentication token that is used by 2014-2015 TVs and some 2016-current TVs
--timeout TIMEOUT|socket timeout in seconds (0 = no timeout)
--volume VOLUME|sets the volume allowed values: 0-100 or -1 to print the volume
--mute MUTE|sets the mute. allowed values: on, off, state. state to print the mute state
--brightness BRIGHTNESS|sets the brightness allowed values: 0-100 or -1 to print the brightness
--contrast CONTRAST|sets the contrast allowed values: 0-100 or -1 to print the contrast
--sharpness SHARPNESS|sets the sharpness allowed values: 0-100 or -1 to print the sharpness
--source SOURCE|set the source. you can use the TV defined names.. HDMI1, HDMI2, PC, USB... or you can use the programmed label that appears on the OSD.
--source-label SOURCE_LABEL|sets the source label that appears on the OSD
--config-file PATH/FILENAME|path and filename to configuration file *see below for mor information
--start-app APPLICATION NAME OR ID|starts an application
--app-metadata METADATA|string of information the application can use when it starts up. And example would be the browser. To have it open directly to a specific URL you would enter: `"http\/\/www.some-web-address.com"` wrapping the meta data in quotes will reduce the possibility of a command line parser error.
--key-help {OPTIONAL KEYS}|prints out key help

<br></br>
Example use:
<br></br>
```
samsungctl --host 192.168.0.10 --name myremote KEY_VOLDOWN
```

<br></br>
To obtain a list of all of the known keys:
<br></br>
```samsungctl --help-keys```
<br></br>

You can also get help on a specific key:
<br></br>
```samsungctl --key-help KEY_16_9```
<br></br>

or if you wanted to list more then one key:
<br></br>
```samsungctl --key-help KEY_16_9 KEY_TTX_MIX```
<br></br>
<br></br>

***--config-file***
___________________
If this is the first time you are using this library on a TV you must
specify --host and key code for the command you wish to execute along
with this parameter.
<br></br>

```samsungctl --host 192.168.1.100 --config-file "/PATH/FILE.NAME" KEY_MENU```
<br></br>

By doing this is will make all of the necessary config file settings that
are needed to be made for your TV. After the library has sent the command
to your TV it will then save the file. Any calls there after will only
need to have --config-file PATH/FILENAME along with the command you
wish to perform for a command line options.
<br></br>

```samsungctl --config-file "/PATH/FILE.NAME" KEY_MENU```
<br></br>

All other information will be retrieved from the file.

<br></br>
<br></br>
\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
<br></br>
***depreciated***
<br></br>
\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
<br></br>
The settings can be loaded from a configuration file. The file is searched from

* `$XDG_CONFIG_HOME/samsungctl.conf`
* `~/.config/samsungctl.conf`
* `/etc/samsungctl.conf`

in this order. A simple default configuration is
bundled with the source as

* `samsungctl.conf <samsungctl.conf>`


<br></br>
***Library usage***
-------------------

samsungctl can also be used as a python package.
```python
    import samsungctl
```

A context managed remote controller object of class `Remote` can be
constructed using the `with` statement:

```python
    with samsungctl.Remote(config) as remote:
        # Use the remote object
```

***Config Class***
__________________

I have put into place a class that handles all of the configuration
information. It makes it easier for saving and loading config data.

```python
import samsungctl


config = samsungctl.Config(
    name='samsungctl',
    description='samsungctl-library',
    method='websocket',
    port=8001
)
```
<br></br>
The constructor for the Config class takes these parameters
<br></br>
I added a new parameter to the config class.
This will allow for user entry of the mac address if there are issues
with detecting it.
<br></br>

Param Name|Default value|Param Type|Use
----------|-------------|----------|---
name|`"samsungctl"`|`str`|Name of the "remote" this is the name that is going to appear on the TV
description|HOSTNAME of local PC|`str`|Only used in the legacy connection (pre 2014  TVs)
host|`None`|`str`|The ip address of the TV `"192.168.1.1"`
port|`None`|`int`|The port to connect to. choices aree 55000 (< 2014), 8080 (2014 & 2015), 8001 & 8002 (>= 2016) or `None` \*
method|`None`|`str`|Connection method \(`"legacy"`, `"websocket"`, `"encrypted"` or `None` \* \)
id|`None`|`str`|This is an identifier that you can set. when using the "encrypted" method this should be left out
timeout|`0`|`int`|socket timeout, only used for the legacy method
token|`None`|`str`|Authentication token that is used for 2014 & 2015 and some 2016+ TV's
device_id|`None`|`str`|Internal Use
upnp_locations|`None`|`list`|Future Use
mac|`None`|`str`|MAC address of the TV `"00:00:00:00:00"` or `None` \*\*.
<br></br>

\* I have instituted a detection system that will automatically detect
what connection type and port to use. In order to have the detection
system activate the port and the method parameters in the call to
Config MUST be `None`.
<br></br>

\*\* The `mac` parameter in the config class does not have to be used if
you are using a legacy connection, <= 2013 TV. if you are using a
TV that is 2014 and newer if there is no mac address the power on
feature will not work. If you do not specify a mac address and the TV
is 2014 or newer the program will attempt to acquire the MAC address of
the TV for you. in order for this to be successful you need to have
your TV turned on. This process only needs to be done a single time if
you are saving the configuration data using the `save` method. If for
some reason we are unable to locate the MAC address for the TV you have
the option of manually passing it to the call to Config. If you are
entering it manually it needs to be formatted `"00:00:00:00:00"`.
<br></br>

Here is a python script example of running samsungctl using all of the
detection features activated remember in order for this to work you
need to have the TV powered on. Since we only want to go through this
process a single time (because it can take an extra second or 2) we want
to save the configuration information to file. So be sure to enter the
path and filename into the save method.
<br></br>

```python
import samsungctl


config = samsungctl.Config(host='192.168.1.100')

with samsungctl.Remote(config) as remote:
    remote.KEY_MENU()

config.save('PATH/FILE.NAME')

```
<br></br>

the Config class is also where you set your logging level
<br></br>

```python
import logging
import samsungctl


config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

config.log_level = logging.DEBUG
```
<br></br>

There are 2 nice convenience methods for saving and loading a config file.
<br></br>

```python
import samsungctl

config = samsungctl.Config.load('path/to/save/file')
```
<br></br>

If you load a file the path is saved so you can simply call save to
save any new data. If you constructed the Config class manually you will
need to pass a path when calling save. and that path is then saved so
any subsequent calls to save will not require you to pass the path
<br></br>

```python
import samsungctl


config = samsungctl.Config(
    name='samsungctl',
    description='samsungctl-library',
    method='websocket',
    host='192.168.1.100'
)

config.save('path/to/save/file')
```
<br></br>

when calling save if you pass only a folder path and not a folder/file path
the name you passed to the constructor will be used along with the
extension ".config"
<br></br>

You do not need to keep track of the config instance. once it is passed
to the Remote constructor it is then stored in that instance.
<br></br>

```python
import samsungctl


config = samsungctl.Config.load('path/to/save/file')
remote = samsungctl.Remote(config)
remote.config.save()
```
<br></br>

I also gave a little twist on the loading of the config file. I did
this so there would not need to be 2 different code blocks one for
initial setup and another for loading a saved file.
<br></br>

```python
import samsungctl

config = samsungctl.Config.load('PATH/FILE.NAME')(
    name='samsungctl',
    description='samsungctl-library',
    method='websocket',
    host='192.168.1.100'
)

config.save()

```
<br></br>

The nifty thing about the code above is it allows for several things to happen
1. It is not going to require 2 different config setup routines. only a single one is needed. If the file exists then it is used.
2. If you happen to only specify a directory and want samsungctl to use the name parameter for the filename. this is what makes that possible.
3. If the path does not exist. then it will create a new configuration with the supplied arguments and set the save of that config data.
<br></br>
<br></br>
You are still able to pass a dictionary to the Remote constructor as well.
<br></br>
<br></br>

***\*\*\* Depreciated***
The constructor takes a configuration dictionary as a parameter. All
configuration items must be specified.

<br></br>

Key|Type|Description
---|----|-----------
host|string|Hostname or IP address of the TV.
port|int|TCP port number. \(Default: `55000`\)
method|string|Connection method \(`"legacy"` or `"websocket"`\)
name|string|Name of the remote controller.
description|string|Remote controller description.
id|string|Additional remote controller ID.
token|string|Authentication token
timeout|int|Timeout in seconds. `0` means no timeout.
<br></br>

***Power Property***
____________________
Power status along with powering off and on 2014+ TV's

<br></br>
```python
import samsungctl


config = samsungctl.Config.load('path/to/save/file')
remote = samsungctl.Remote(config)
print(remote.power)

# turns the TV on
remote.power = True

print(remote.power)
# turns the TV off
remote.power = False

# toggles the power
remote.power = not remote.power
```
<br></br>

We do not have the ability to turn on the TV's older then 2014.
<br></br>
<br></br>

***Exceptions***
________________
When something goes wrong you will receive an exception:
<br></br>

Exception|Description
---------|-----------
SamsungTVError|Samsung TV Exception Base Class.
AccessDenied|Connection was denied.
ConnectionClosed|Connection was closed.
UnhandledResponse|Received unknown response.
NoTVFound|Unable to locate a TV.
ConfigError|Base class for config exceptions.
ConfigUnknownMethod|Unknown connection method.
ConfigParseError|Config data is not json formatted or is not a formatted flat file.
ConfigLoadError|Config path specified cannot be located.
ConfigSavePathError|Config save path is not valid.
ConfigSaveError|Error saving config.
ConfigSavePathNotSpecified|Config save path was not specified.
ConfigParameterError|Parameter is not a config parameter.
<br></br>

***Example program***
_____________________
This simple program opens and closes the menu a few times.
<br></br>

```python
import samsungctl
import time

config = samsungctl.Config(
    name='samsungctl',
    method='legacy',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    for i in range(10):
        remote.control("KEY_MENU")
        time.sleep(0.5)
```
<br></br>

***Mouse Control***
___________________
Mouse control can only be done by using samsungctl as a python module.
Mouse command are built. this way you can accomplish multiple movements
in a single "command" and the movement set can be stored for later use.
depending on how long it takes to accomplish a movement
(distance traveled) you will need to insert a wait period in between
each movement.
<br></br>

```python
import samsungctl

config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    mouse = remote.mouse
    mouse.move(x=100, y=300)
    mouse.wait(0.5)
    mouse.left_click()
    mouse.run()
    mouse.clear()
```
<br></br>

I designed this to all be thread safe. so only one mouse command set
can be run at a single time. So if you have the mouse running in a
thread and you need to stop the movement from another. or you simply
want to terminate the program gracefully. you would call `mouse.stop()`
<br></br>

I will be at a later date adding the wait periods on the mouse movements
so it will be done automatically. I do not own one of the TV's so I do
not know how long it takes to move the mouse different distances. I
also do not know if the time it takes to move the mouse is linear. An
example of linear movement would be it takes 1 second to move the
mouse 100 pixels so to move it 200 pixels it would take 2 seconds.
most devices that have mouse control also have acceleration and a
min/max speed which would be non linear movement. An example of non
linear is, if it took 1 second to move the mouse 100 pixels, to move it
200 it would take 1.5 seconds. You can run the code below and report
the output to me. that will aide in making this all automatic. I need
this data form several TV models and years. as Samsung could have
changed the mouse speed and acceleration between years/models.
<br></br>

```python
import samsungctl
import time


config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
     mouse = remote.mouse

    def move_mouse(_x, _y):
        mouse.move(x=x, y=y)
        start = time.time()
        mouse.run()
        stop = time.time()
        print('x:', x, 'y:', y, 'time:', (stop - start) * 1000)
        mouse.clear()
        mouse.move(x=-x, y=-y)
        mouse.run()
        mouse.clear()

    for x in range(1920):
        move_mouse(x, 0)

        for y in range(1080):
            move_mouse(0, y)
            move_mouse(x, y)
```
<br></br>

***Voice Recognition***
_______________________
If you TV supports voice recognition you have the ability to start and
stop the voice recognition service on the TV. this can be done only by
using the samsungctl library as a package to an already existing program.
example code of how to do this is below.
<br></br>

```python
import samsungctl
import time

config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    remote.start_voice_recognition()
    time.sleep(5.0)
    remote.stop_voice_recognition()
```
<br></br>

***Applications***
__________________
This is going to be a wee bit long winded. But here goes
<br></br>

below is a sample of how to access the applications on the TV
<br></br>

```python
import samsungctl

config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    for app in remote.applications:
        print('name:', app.name)
        print('=' * 30)
        print('id:', app.app_id)
        print('is running:', app.is_running)
        print('version:', app.version)
        print()
```
<br></br>

if you want to access a specific application by name or by the app id
<br></br>

```python
import samsungctl

config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    app = remote.get_application('YouTube')
    if app is not None:
        print('name:', app.name)
        print('=' * 30)
        print('id:', app.app_id)
        print('is running:', app.is_running)
        print('version:', app.version)
        print()
```
<br></br>

these are the available properties for an application

* is_lock
* name
* app_type
* position
* app_id
* launcher_type
* mbr_index
* source_type_num
* icon
* id
* mbr_source
* action_type
* version
* is_visible
* is_running

<br></br>
now here is a little bonus. we can also iterate over an application for
any content groups. and then we can iterate over the content group for
the available content in that group
<br></br>

```python
import samsungctl

config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    for app in remote.applications:
        print('name:', app.name)
        print('=' * 30)
        for content_group in app:
            print('   ', content_group.title)
            print('   ', '-' * 26)
            for content in content_group:
                print('       ', content.title)
```
<br></br>

here are the available properties for the content group

* title

<br></br>
here are the available properties for the content

* is_playable
* subtitle
* app_type
* title
* mbr_index
* live_launcher_type
* action_play_url
* service_id
* launcher_type
* source_type_num
* action_type
* app_id
* subtitle2
* display_from
* display_until
* mbr_source
* id
* subtitle3
* icon

<br></br>

You can also run an application or a piece of content by calling `run()`
on either an application or on the content.
<br></br>

***Key codes***
---------------
Here is the new list of keycodes that are supported.
<br></br>
<br></br>

*Power Keys*
____________
Key|Description
---|-----------
KEY_POWEROFF|PowerOFF
KEY_POWERON|PowerOn
KEY_POWER|PowerToggle

<br></br>
*Input Keys*
____________
Key|Description
---|-----------
KEY_SOURCE|Source
KEY_COMPONENT1|Component1
KEY_COMPONENT2|Component2
KEY_AV1|AV1
KEY_AV2|AV2
KEY_AV3|AV3
KEY_SVIDEO1|SVideo1
KEY_SVIDEO2|SVideo2
KEY_SVIDEO3|SVideo3
KEY_HDMI|HDMI
KEY_HDMI1|HDMI1
KEY_HDMI2|HDMI2
KEY_HDMI3|HDMI3
KEY_HDMI4|HDMI4
KEY_FM_RADIO|FMRadio
KEY_DVI|DVI
KEY_DVR|DVR
KEY_TV|TV
KEY_ANTENA|AnalogTV
KEY_DTV|DigitalTV

<br></br>
*Number Keys*
_____________
Key|Description
---|-----------
KEY_1|Key1
KEY_2|Key2
KEY_3|Key3
KEY_4|Key4
KEY_5|Key5
KEY_6|Key6
KEY_7|Key7
KEY_8|Key8
KEY_9|Key9
KEY_0|Key0

<br></br>
*Misc Keys*
___________
Key|Description
---|-----------
KEY_PANNEL_CHDOWN|3D
KEY_ANYNET|AnyNet+
KEY_ESAVING|EnergySaving
KEY_SLEEP|SleepTimer
KEY_DTV_SIGNAL|DTVSignal

<br></br>
*Channel Keys*
______________
Key|Description
---|-----------
KEY_CHUP|ChannelUp
KEY_CHDOWN|ChannelDown
KEY_PRECH|PreviousChannel
KEY_FAVCH|FavoriteChannels
KEY_CH_LIST|ChannelList
KEY_AUTO_PROGRAM|AutoProgram
KEY_MAGIC_CHANNEL|MagicChannel

<br></br>
*Volume Keys*
_____________
Key|Description
---|-----------
KEY_VOLUP|VolumeUp
KEY_VOLDOWN|VolumeDown
KEY_MUTE|Mute

<br></br>
*Direction Keys*
________________
Key|Description
---|-----------
KEY_UP|NavigationUp
KEY_DOWN|NavigationDown
KEY_LEFT|NavigationLeft
KEY_RIGHT|NavigationRight
KEY_RETURN|NavigationReturn/Back
KEY_ENTER|NavigationEnter

<br></br>
*Media Keys*
____________
Key|Description
---|-----------
KEY_REWIND|Rewind
KEY_STOP|Stop
KEY_PLAY|Play
KEY_FF|FastForward
KEY_REC|Record
KEY_PAUSE|Pause
KEY_LIVE|Live
KEY_QUICK_REPLAY|fnKEY_QUICK_REPLAY
KEY_STILL_PICTURE|fnKEY_STILL_PICTURE
KEY_INSTANT_REPLAY|fnKEY_INSTANT_REPLAY

<br></br>
*Picture in Picture*
____________________
Key|Description
---|-----------
KEY_PIP_ONOFF|PIPOn/Off
KEY_PIP_SWAP|PIPSwap
KEY_PIP_SIZE|PIPSize
KEY_PIP_CHUP|PIPChannelUp
KEY_PIP_CHDOWN|PIPChannelDown
KEY_AUTO_ARC_PIP_SMALL|PIPSmall
KEY_AUTO_ARC_PIP_WIDE|PIPWide
KEY_AUTO_ARC_PIP_RIGHT_BOTTOM|PIPBottomRight
KEY_AUTO_ARC_PIP_SOURCE_CHANGE|PIPSourceChange
KEY_PIP_SCAN|PIPScan

<br></br>
*Modes*
_______
Key|Description
---|-----------
KEY_VCR_MODE|VCRMode
KEY_CATV_MODE|CATVMode
KEY_DSS_MODE|DSSMode
KEY_TV_MODE|TVMode
KEY_DVD_MODE|DVDMode
KEY_STB_MODE|STBMode
KEY_PCMODE|PCMode

<br></br>
*Color Keys*
____________
Key|Description
---|-----------
KEY_GREEN|Green
KEY_YELLOW|Yellow
KEY_CYAN|Cyan
KEY_RED|Red

<br></br>
*Teletext*
__________
Key|Description
---|-----------
KEY_TTX_MIX|TeletextMix
KEY_TTX_SUBFACE|TeletextSubface

<br></br>
*AspectRatio*
______________
Key|Description
---|-----------
KEY_ASPECT|AspectRatio
KEY_PICTURE_SIZE|PictureSize
KEY_4_3|AspectRatio4:3
KEY_16_9|AspectRatio16:9
KEY_EXT14|AspectRatio3:4(Alt)
KEY_EXT15|AspectRatio16:9(Alt)


*Picture Mode*
______________
Key|Description
---|-----------
KEY_PMODE|PictureMode
KEY_PANORAMA|PictureModePanorama
KEY_DYNAMIC|PictureModeDynamic
KEY_STANDARD|PictureModeStandard
KEY_MOVIE1|PictureModeMovie
KEY_GAME|PictureModeGame
KEY_CUSTOM|PictureModeCustom
KEY_EXT9|PictureModeMovie(Alt)
KEY_EXT10|PictureModeStandard(Alt)

<br></br>
*Menus*
_______
Key|Description
---|-----------
KEY_MENU|Menu
KEY_TOPMENU|TopMenu
KEY_TOOLS|Tools
KEY_HOME|Home
KEY_CONTENTS|Contents
KEY_GUIDE|Guide
KEY_DISC_MENU|DiscMenu
KEY_DVR_MENU|DVRMenu
KEY_HELP|Help

<br></br>
*OSD*
_____
Key|Description
---|-----------
KEY_INFO|Info
KEY_CAPTION|Caption
KEY_CLOCK_DISPLAY|ClockDisplay
KEY_SETUP_CLOCK_TIMER|SetupClock
KEY_SUB_TITLE|Subtitle

<br></br>
*Zoom*
______
Key|Description
---|-----------
KEY_ZOOM_MOVE|ZoomMove
KEY_ZOOM_IN|ZoomIn
KEY_ZOOM_OUT|ZoomOut
KEY_ZOOM1|Zoom1
KEY_ZOOM2|Zoom2

<br></br>
*Other Keys*
____________
Key|Description
---|-----------
KEY_WHEEL_LEFT|WheelLeft
KEY_WHEEL_RIGHT|WheelRight
KEY_ADDDEL|Add/Del
KEY_PLUS100|Plus100
KEY_AD|AD
KEY_LINK|Link
KEY_TURBO|Turbo
KEY_CONVERGENCE|Convergence
KEY_DEVICE_CONNECT|DeviceConnect
KEY_11|Key11
KEY_12|Key12
KEY_FACTORY|KeyFactory
KEY_3SPEED|Key3SPEED
KEY_RSURF|KeyRSURF
KEY_FF_|FF_
KEY_REWIND_|REWIND_
KEY_ANGLE|Angle
KEY_RESERVED1|Reserved1
KEY_PROGRAM|Program
KEY_BOOKMARK|Bookmark
KEY_PRINT|Print
KEY_CLEAR|Clear
KEY_VCHIP|VChip
KEY_REPEAT|Repeat
KEY_DOOR|Door
KEY_OPEN|Open
KEY_DMA|DMA
KEY_MTS|MTS
KEY_DNIe|DNIe
KEY_SRS|SRS
KEY_CONVERT_AUDIO_MAINSUB|ConvertAudioMain/Sub
KEY_MDC|MDC
KEY_SEFFECT|SoundEffect
KEY_PERPECT_FOCUS|PERPECTFocus
KEY_CALLER_ID|CallerID
KEY_SCALE|Scale
KEY_MAGIC_BRIGHT|MagicBright
KEY_W_LINK|WLink
KEY_DTV_LINK|DTVLink
KEY_APP_LIST|ApplicationList
KEY_BACK_MHP|BackMHP
KEY_ALT_MHP|AlternateMHP
KEY_DNSe|DNSe
KEY_RSS|RSS
KEY_ENTERTAINMENT|Entertainment
KEY_ID_INPUT|IDInput
KEY_ID_SETUP|IDSetup
KEY_ANYVIEW|AnyView
KEY_MS|MS
KEY_MORE|
KEY_MIC|
KEY_NINE_SEPERATE|
KEY_AUTO_FORMAT|AutoFormat
KEY_DNET|DNET

<br></br>
*Auto Arc Keys*
_______________
Key|Description
---|-----------
KEY_AUTO_ARC_C_FORCE_AGING|
KEY_AUTO_ARC_CAPTION_ENG|
KEY_AUTO_ARC_USBJACK_INSPECT|
KEY_AUTO_ARC_RESET|
KEY_AUTO_ARC_LNA_ON|
KEY_AUTO_ARC_LNA_OFF|
KEY_AUTO_ARC_ANYNET_MODE_OK|
KEY_AUTO_ARC_ANYNET_AUTO_START|
KEY_AUTO_ARC_CAPTION_ON|
KEY_AUTO_ARC_CAPTION_OFF|
KEY_AUTO_ARC_PIP_DOUBLE|
KEY_AUTO_ARC_PIP_LARGE|
KEY_AUTO_ARC_PIP_LEFT_TOP|
KEY_AUTO_ARC_PIP_RIGHT_TOP|
KEY_AUTO_ARC_PIP_LEFT_BOTTOM|
KEY_AUTO_ARC_PIP_CH_CHANGE|
KEY_AUTO_ARC_AUTOCOLOR_SUCCESS|
KEY_AUTO_ARC_AUTOCOLOR_FAIL|
KEY_AUTO_ARC_JACK_IDENT|
KEY_AUTO_ARC_CAPTION_KOR|
KEY_AUTO_ARC_ANTENNA_AIR|
KEY_AUTO_ARC_ANTENNA_CABLE|
KEY_AUTO_ARC_ANTENNA_SATELLITE|

<br></br>
*Panel Keys*
____________
Key|Description
---|-----------
KEY_PANNEL_POWER|
KEY_PANNEL_CHUP|
KEY_PANNEL_VOLUP|
KEY_PANNEL_VOLDOW|
KEY_PANNEL_ENTER|
KEY_PANNEL_MENU|
KEY_PANNEL_SOURCE|
KEY_PANNEL_ENTER|

<br></br>
*Extended Keys*
_______________
Key|Description
---|-----------
KEY_EXT1|
KEY_EXT2|
KEY_EXT3|
KEY_EXT4|
KEY_EXT5|
KEY_EXT6|
KEY_EXT7|
KEY_EXT8|
KEY_EXT11|
KEY_EXT12|
KEY_EXT13|
KEY_EXT16|
KEY_EXT17|
KEY_EXT18|
KEY_EXT19|
KEY_EXT20|
KEY_EXT21|
KEY_EXT22|
KEY_EXT23|
KEY_EXT24|
KEY_EXT25|
KEY_EXT26|
KEY_EXT27|
KEY_EXT28|
KEY_EXT29|
KEY_EXT30|
KEY_EXT31|
KEY_EXT32|
KEY_EXT33|
KEY_EXT34|
KEY_EXT35|
KEY_EXT36|
KEY_EXT37|
KEY_EXT38|
KEY_EXT39|
KEY_EXT40|
KEY_EXT41|

<br></br>
<br></br>
Please note that some codes are different on the 2016+ TVs. For example,
`KEY_POWEROFF` is `KEY_POWER` on the newer TVs.
<br></br>

I also added all of the keys as methods. so you have the choice of using
the method for sending a key
<br></br>

```python
import samsungctl

config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    remote.command("KEY_VOLUP")

```
<br></br>

or you can also use this
<br></br>

```python
import samsungctl

config = samsungctl.Config(
    name='samsungctl',
    method='websocket',
    host='192.168.1.100'
)

with samsungctl.Remote(config) as remote:
    remote.KEY_VOLUP()

```
<br></br>
<br></br>
<br></br>

***References***
----------------

I did not reverse engineer the control protocol myself and samsungctl is not
the only implementation. Here is the list of things that inspired samsungctl.

- http://sc0ty.pl/2012/02/samsung-tv-network-remote-control-protocol/
- https://gist.github.com/danielfaust/998441
- https://github.com/Bntdumas/SamsungIPRemote
- https://github.com/kyleaa/homebridge-samsungtv2016
- https://github.com/eclair4151/SmartCrypto
