# droidserve

`droidserve` is a Python (3.5+) tool to fetch .cia, .tik and .cetk files to the FBI Homebrew software installed on a 3DS.

It's a rewrite of @Steveice10's [servefiles.py](https://github.com/Steveice10/FBI/blob/master/servefiles/servefiles.py), adapted to run from Android, and from which interactive mode and Python 2 support have been removed.

-----

## Requirements

To run, `droidserve` requires:

 * Python 3.5+;
 * Internet connectivity.

This tool has been tested and confirmed to work via the open-source [Termux](https://f-droid.org/app/com.termux) app.
To install Python, issue `apt install python`.

Note that **Termux requires Android >= 5.0.0**.

-----

## Usage

`droidserve` requires two mandatory arguments and supports two optional arguments as well. The following command will display a brief usage message:

    python droidserve.py -h

It will result in:

    usage: droidserve.py [-h] [--host HOST] [--port PORT] target path
    
    Serve .cia, .tik, and .cetk files to FBI.
    
    positional arguments:
      target       IP address of the target 3DS
      path         file or directory whose contwnts to serve
    
    optional arguments:
      -h, --help   show this help message and exit
      --host HOST  IP address of the sender
      --port PORT  port of the sender

The `target` argument is mandatory, while the 3DS's port is hardcoded to `5000`.
The `path` argument can either be a single `.cia`, `.tik` or `.cetk`, or a directory. In the latter case, `droidserve` will scan it and serve all the `.cia`, `.tik`, and `.cetk` files in it, if any.

If the `--host` argument isn't supplied, `droidserve` will attempt to guess it automatically. Likewise, `--port` will default to `8080`.
