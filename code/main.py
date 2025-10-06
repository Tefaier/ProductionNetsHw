import argparse
import sys
import time
import threading
import socketserver
from ctypes.wintypes import tagMSG

from dnslib import *

import server
from server import UDPRequestHandler, DomainName


def main():
    parser = argparse.ArgumentParser(description='Start a DNS implemented in Python.')
    parser.add_argument('--host', default='127.0.0.1', type=str, help='The host to listen on')
    parser.add_argument('--port', default=53, type=int, help='The port to listen on')
    parser.add_argument('--from', default='example.com', type=str, help='Name which to redirect', dest="from_arg")
    parser.add_argument('--to', default="127.0.0.1", type=str, help='The ipv4 where to redirect')

    args = parser.parse_args()

    D = DomainName(f"{args.from_arg}.")
    redirect_to = args.to

    server.domain = D
    server.records = {
        D: [A(redirect_to), AAAA((0,) * 16)],
    }

    print("Starting nameserver...")

    servers = [socketserver.ThreadingUDPServer((args.host, args.port), UDPRequestHandler)]

    for s in servers:
        thread = threading.Thread(target=s.serve_forever)  # that thread will start one more thread for each request
        thread.daemon = True  # exit the server thread when the main thread terminates
        thread.start()
        print(f"UDP server loop running in thread: {thread.name}")

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nKeyboard interruption detected")
        pass
    finally:
        print("\nServers shutdown started")
        for s in servers:
            s.shutdown()
        print("\nServers shutdown finished")

if __name__ == '__main__':
    main()
