# coding: utf-8 -*-

import argparse
import os
import signal
import socket
import struct
#import subprocess   # See line 44
import sys
import threading
import time

from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import quote

##########
# Gracefully handles CTRL-C aborts
def exit_gracefully(signal, frame):
    print("\nAborting as per user request.")
    
    if sock:
        sock.close()
        server.shutdown()
    
    exit(1)

##########

class MyServer(TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

# Determines the host's IP by querying Google's DNS
def determine_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]
    s.close()
    
    return host

# Experimental method to determine the host's IP if the access point has no Internet access
# Already implemented, should there be a way to prevent the 3DS from disconnecting if the AP doesn't have Internet access
#def fallback_host_ip():
    #try:
        #(out, err) = subprocess.Popen("ip r l", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()
    #except IndexError:
        #host = ""
    
    #if not err:
        #host = out.decode("utf-8").split(" ")[-2]
    
    #return host

# Prepares a list of URL(s) from accepted link(s)
# Returns a '\m'-separated string and an ASCII encoding of it
def prepare_data(ip, port, path):
    accepted_extensions = (".cia", ".tik", ".cetk")
    url_prefix = "{0}:{1!s}/".format(ip, port)
    file_list = []
    
    if os.path.isfile(path):
        if path.endswith(accepted_extensions):
            file_list.append("{0}{1}".format(url_prefix, quote(path)))
            dir = os.path.dirname(path)
        else:
            print("{0}: Unsupported file extension.".format(path))
            exit(1)
    else:
        file_list = ["{0}{1}".format(url_prefix, quote(file)) for file in os.listdir(path) if file.endswith(accepted_extensions)]
        dir = path
    
    if not file_list:
        print("No files to serve.")
        exit(1)
    
    return "\n".join(file_list), "\n".join(file_list).encode("ascii")
    

##########
# Commandline argument parser section

ap = argparse.ArgumentParser(description = "Serve .cia, .tik or .cetk files to FBI.")

ap.add_argument("target_ip", type = str, help = "IP address of the 3DS")
ap.add_argument("path", type = str, help = "file or folder to serve")
ap.add_argument("-i", "--host_ip", type = str, required = False, help = "IP of the sender")
ap.add_argument("-p", "--host_port", type = int, required = False, default = 8080, help = "port of the sender")

args = ap.parse_args()

##########
# Handler to avoid printing a bunch of junk if the user aborts with CTRL-C

signal.signal(signal.SIGINT, exit_gracefully)

##########

if not args.host_ip:
    args.host_ip = determine_host_ip()
    
    #if not args.host_ip:
        #args.host_ip = fallback_host_ip()
    
    if not args.host_ip:
        print("Fatal: no connection.")
        exit(1)

if not os.path.exists(args.path):
    print("{0}: No such file or directory.".format(args.path))
    exit(1)

print("Preparing data...\n")
(payload, payload_bytes) = prepare_data(args.host_ip, args.host_port, args.path)

print("URL(s):\n{0}\n".format(payload))

print("Opening HTTP server on port {0!s}...".format(args.host_port))
server = MyServer(("", args.host_port), SimpleHTTPRequestHandler)
thread = threading.Thread(target = server.serve_forever)
thread.start()

try:
    print("Sending URL(s) to {0} on port 5000...".format(args.target_ip))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.target_ip, 5000))
    sock.sendall(struct.pack("!L", len(payload_bytes)) + payload_bytes)
    
    while len(sock.recv(1)) < 1:
        time.sleep(0.05)
    
    sock.close()
except Exception as e:
    print("Error: {0!s}".format(e))
    
    server.shutdown()
    exit(1)

print("Sending complete: shutting down HTTP server...")
server.shutdown()
