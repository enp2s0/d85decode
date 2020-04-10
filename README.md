## d85decode

`d85decode` is a simple script to parse and display data from a Potensic d85 drone.

#### Usage

`python3 main.py` will start the program. Use `-h` or `--help` to see the command line options:

```
usage: main.py [-h] [--ip IP] [--port PORT] [--recvbuf RECVBUF]

Decode and display data from a Potensic d85 drone.

optional arguments:
  -h, --help         show this help message and exit
  --ip IP            IPv4 address to listen on (default: 0.0.0.0)
  --port PORT        port to listen on (default: 8001)
  --recvbuf RECVBUF  size of UDP receive buffer (default: 4096)
```

#### Example Output

This is the output of a drone just before launch. The leading number is the packet ID. `lat` and `lon` are GPS coordinates. `alt` and `dist` are the height and distance relative to the takeoff point. `fm` is the "flight mode" of the drone, and `bat` is the current battery voltage.

```
Ready, waiting for data...
215 | lat: -77.6678616, lon: 32.7787690, alt:   0m, dist:    0m, fm:          grounded, bat: 7.7V
216 | lat: -77.6678606, lon: 32.7787707, alt:   0m, dist:    0m, fm:          grounded, bat: 7.7V
217 | lat: -77.6678594, lon: 32.7787728, alt:   0m, dist:    0m, fm:          grounded, bat: 7.7V
```

#### Drone Protocol

See PROTOCOL.md for details on the communications structure and the protocol itself.

#### License

This software is released under the MIT license.

```
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the  "Software"), to deal in the Software without restriction, including  without limitation the rights to use, copy, modify, merge, publish,  distribute, sublicense, and/or sell copies of the Software, and to  permit persons to whom the Software is furnished to do so, subject to  the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.```
```

