## Purpose

droidserve is a Python (3.5+) tool to fetch .cia, .tik and .cetk files to the FBI Homebrew software installed on a 3DS.

It's basically a rewrite of @Steveice10's [servefiles.py](https://github.com/Steveice10/FBI/blob/master/servefiles/servefiles.py), adapted to run from Android, and from which interactive mode and Python 2 support have been removed.

-----

## Requirements

To run this script, you need:

 * Python 3.5+;
 * Internet connectivity (local networks won't work).

The author tested the tool via the open-source [Termux](https://f-droid.org/app/com.termux) app, on which Python had been installed by means of `apt install python`, so this is the recommended setting.

Note that **Termux requires Android >= 5.0**.

-----

## Usage

droidserve requires two mandatory arguments and supports two optional arguments as well, as visible by issuing:

    python droidserve.py -h

which will yield:

    usage: droidserve.py [-h] [-i HOST_IP] [-p HOST_PORT] target_ip path
    
    Serve .cia, .tik or .cetk files to FBI.
    
    positional arguments:
      target_ip             IP address of the 3DS
      path                  file or folder to serve
    
    optional arguments:
      -h, --help            show this help message and exit
      -i HOST_IP, --host_ip HOST_IP
                            IP of the sender
      -p HOST_PORT, --host_port HOST_PORT
                            port of the sender
