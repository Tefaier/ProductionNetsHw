import argparse
import threading
import socketserver

from dnslib import *
import sys

import server
from server import UDPRequestHandler, DomainName


def main():
    parser = argparse.ArgumentParser(description='Start a DNS implemented in Python.')
    parser.add_argument('--host', default='127.0.0.1', type=str, help='The host to listen on')
    parser.add_argument('--port', default=53, type=int, help='The port to listen on')
    parser.add_argument('--config_path', type=str, help='Configuration path', dest="path")

    args = parser.parse_args()

    records = {}
    with open(args.path, "r") as file:
        for (i, line) in enumerate(file.readlines()):
            split = line.split(" ")
            if len(split) != 2:
                continue
            domain, redirect = line.split(" ")
            redirect = redirect.strip().replace("\n", "")
            if i == 0 and domain == "upstream":
                server.upstream_dns = redirect
                continue
            records[f"{domain}."] = [A(redirect)]

    server.records = records

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
