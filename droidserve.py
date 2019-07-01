""" Serve .cia, .tik, and .cetk files to FBI. """
import argparse
import http.server
import os
import socket
import socketserver
import struct
import sys
import threading
import time
import urllib.request


class MyServer(socketserver.TCPServer):
    """ Class to serve files to FBI. """
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


def exit_fatal(msg):
    """ Print a message to stderr and exit with code 1. """
    print("{0}".format(msg), file=sys.stderr)
    exit(1)


def local_ip():
    """ Obtain the local IP address. """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: # pylint: disable=invalid-name
        # https://stackoverflow.com/a/166589
        s.connect(("8.8.8.8", 80))

        return s.getsockname()[0] # local IP


def is_valid_file(fname):
    """ Check if fname is a .cia, .tik, or .cetk file. """
    return fname.endswith((".cia", ".tik", ".cetk"))


def assemble_urls(host, port, path, directory):
    """ Assemble URLs to path or to its contents. """
    urls = []

    if directory:
        for fname in os.listdir(path):
            if is_valid_file(fname):
                urls.append("{0}:{1}/{2}".format(host, port, urllib.request.quote(os.path.basename(
                    fname))))
    else:
        urls.append("{0}:{1}/{2}".format(host, port, urllib.request.quote(os.path.basename(path))))

    return urls


def serve_payload(directory, target, payload):
    """ Serve payload to target. """
    os.chdir(directory)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # pylint: disable=invalid-name
        s.connect((target, 5000))
        s.sendall(struct.pack("!L", len(payload)) + payload)

        while not s.recv(1):
            time.sleep(0.05)


def main(target, path, host, port):
    """ Core function. """
    if not host:
        try:
            host = local_ip()
        except OSError as e: # pylint: disable=invalid-name
            exit_fatal("Fatal: {0}.".format(e.strerror.lower()))

    payload_urls = assemble_urls(host, port, path, os.path.isdir(path))
    if not payload_urls:
        exit_fatal("Fatal: no file to send.")

    payload = "\n".join(payload_urls).encode("ascii")

    print("URLs:")
    for url in payload_urls:
        print("    {0}".format(url))
    print()

    with MyServer((host, port), http.server.SimpleHTTPRequestHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()

        try:
            serve_payload(os.path.dirname(path), target, payload)
        except ConnectionRefusedError:
            exit_fatal("Fatal: 3DS not ready.")
        except OSError as e: # pylint: disable=invalid-name
            exit_fatal("Fatal: {0}.".format(e.strerror.lower()))
        finally:
            server.shutdown()


if __name__ == "__main__":
    AP = argparse.ArgumentParser(
        description="Serve .cia, .tik, and .cetk files to FBI."
    )

    AP.add_argument(
        "target",
        type=str,
        help="IP address of the target 3DS"
    )
    AP.add_argument(
        "path",
        type=str,
        help="file or directory whose contwnts to serve"
    )
    AP.add_argument(
        "--host",
        type=str,
        help="IP address of the sender"
    )
    AP.add_argument(
        "--port",
        default=8080,
        type=int,
        help="port of the sender"
    )

    ARGS = AP.parse_args()

    main(ARGS.target, ARGS.path, ARGS.host, ARGS.port)
