## Protocol Details

I currently have only decoded the drone-to-PC part of the protocol. This file will be updated as I dig in to the protocol more.

#### Introduction

Two communication channels from the drone to the computer exist, one for status information and the other for video. The video feed is provided by a RTSP server running on the drone's camera module. The status information is sent over UDP broadcast and is a proprietary protocol, which may or many not be specific to the Potensic d85.

The drone creates its own wireless network for all communication with the computer. The subnet of this network is `192.168.99.0/24` and the drone's IP address is `192.168.99.1`. A DHCP server runs on the drone to give connecting devices an IP address.

#### Live Video / FPV

The video stream is a simple RTSP feed. It is trivial to connect to it via VLC or any other program. The feed is located at `rtsp://192.168.99.1:554/11`. The number 11 may be different depending on the drone, analysis of the mobile app shows that the app actually requests the URL from the drone rather than hard-coding it. However, the URL has been consistent for me, so it's worth a shot.

#### Status Channel

The drone sends status messages periodically, as well as every time a picture or video is taken. In the script and here I refer to each message as a "sentence". Sentences are sent via UDP broadcast on port `8001`.

There are 4 sentences I have seen so far. A "Drone Status Sentence" is sent periodically (about 2 per second). A "Camera Status Sentence" is sent whenever a picture is taken by the drone's camera, and a "Video Status Sentence" is sent every time the video recorder is started or stopped. A "Mode Update Sentence" is sent whenever the drone is put into an autonomous mode, such as "Follow Me" or "Orbit Point." This sentence appears to be redundant as the mode change is also visible in the "Drone Status Sentence."

Byte 13 appears to be the sentence type. Here is the type table (question mark indicates unconfirmed entry, usually because it appeared in a disassembly but has never been seen in action):

| ID      | Sentence Type                    |
| ------- | -------------------------------- |
| `00`    | Control Message (?)              |
| `01`    | Drone Status Sentence            |
| `02-03` | Set Parameter Sentence (?)       |
| `04-05` | Follow Mode Sentence             |
| `06-07` | Orbit Mode Sentence              |
| `08-09` | Guided Mode Sentence (?)         |
| `16`    | Alternate Guided Mode Sentence   |
| `22-23` | RTL Sentence (?)                 |
| `24`    | Photo Sentence (?)               |
| `25`    | Video Sentence (?)               |
| `26`    | WiFi Switch Channel Sentence (?) |
| `69`    | Video Sentence                   |
| `78`    | Camera Sentence                  |

The double entries (such as `02-03`) are on-off pairs; the first message is sent when a feature is enabled and the second message is sent when it is disabled.

All sentences begin with a header. The structure of this header is as follows:

| Address | C-style Data Type | Description                                                  |
| ------- | ----------------- | ------------------------------------------------------------ |
| `00-03` | `char[4]`         | Signature. All sentences start with the following 4 bytes: `5b 52 74 3e`. This can be used to identify the start of messages. |
| `04`    | `char`            | Sentence length. Does not include the most of the header, but does include the sentence type byte. |
| `07`    | `char`            | Packet ID. Counts from `0x00` to `0xff` and rolls over. Can be used to detect dropped packets. |
| `13`    | `char`            | Sentence type. Refer to the Sentence ID table above to decode this value. |

##### Drone Status Sentence

This is the most interesting sentence and contains most of the information pilots will care about, such as location, altitude, and GPS statistics. A typical sentence looks like this:

`5b 52 74 3e 26 00 01 ec d0 00 2c 00 aa 01 1a ef ca 03 e6 d2 0d c0 b5 17 00 00 00 00 00 00 00 00 05 00 4b 0c 08 52`

Here is the structure of this sentence.

| Address | C-style Data Type | Description                                                  |
| ------- | ----------------- | ------------------------------------------------------------ |
| `00-13` | `bytes`           | Header. See the header table to decode this section.         |
| `16-19` | `int`             | GPS latitude. Divide by `10000000` to convert to decimal degrees. |
| `20-23` | `int`             | GPS longitude. Divide by `10000000` to convert to decimal degrees. |
| `24-25` | `short`           | Altitude in meters, relative to takeoff point.               |
| `26-27` | `short`           | Distance from takeoff point in meters.                       |
| `28-29` | `short`           | Fence altitude. Not really sure what this is, I've never used the fencing capabilities on the drone. |
| `30-31` | `short`           | Fence distance. Again, not really sure how to use this.      |
| `32`    | `char`            | Fence radius. Again, not really sure how to use this.        |
| `33`    | `char`            | Flight mode. See the flight mode table below for more information. |
| `34`    | `char`            | Battery voltage. Divide by `10` to get the voltage in volts. |
| `35`    | `char`            | GPS fix count. Returns the number of satellites that GPS can see. |
| `36`    | `char`            | An unknown status variable (known as `status1` in the mobile app disassembly). |
| `37`    | `char`            | Controller status. Provides information on the connection between the drone and the controller (not the mobile device or laptop, the actual stick controller.) |

And here is the flight mode table (at least so far, there could be more modes):

| Flight Mode | Description                                                |
| ----------- | ---------------------------------------------------------- |
| `00`        | The drone is on the ground and the propellers are off.     |
| `01`        | The drone is flying without GPS assistance.                |
| `02`        | The drone is flying and using GPS to counteract wind, etc. |
| `03`        | The drone is returning to the takeoff point.               |
| `04`        | The drone is following the controller (follow-me mode).    |
| `05`        | The drone is orbiting.                                     |

##### Camera/Video Sentences

These sentences are sent when the Camera button is pressed on the stick controller. Pressing the button takes a photo and triggers sentence `78`, and holding the button starts or stops video recording and triggers sentence `69`. The structure of these sentences are as follows:

| Address  | C-style Data Type | Description                                                  |
| -------- | ----------------- | ------------------------------------------------------------ |
| `00-13`  | `bytes`           | Header. See the header table to decode this section.         |
| `12-end` | `const char*`     | Message. Contains either `SNAP_OK` (for photos) or `REC_OK` (for videos). |

If you realized that there is some overlap between the header and the message, you're right! These two sentences are abnormal in that the last two bytes of the header are overwritten by the payload. If you look at these sentences' entries in the sentence type table, you'll find that they are significantly higher than the rest of the IDs. This is because they are actually ASCII encodings of the letter in the payload that gets written to the ID location (`69` is ASCII `E` and `78` is ASCII `N`, both are the second letters of the respective sentences as the first two bytes of the payload overwrite the last two bytes of header.)