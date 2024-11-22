import argparse
import shlex
import socket
import subprocess
import sys
import textwrap
import threading

class NetHack:
    def __init__(self):
        self.manual()

    def manual(self):
        parser = argparse.ArgumentParser(
            description="Network Hacking Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(
                """
                Examples:
                (1) ./nethack2.py -t <ip> -p <port> -l -s
                \t\t-> Listen on <ip>:<port> and open shell.
                (2) ./nethack2.py -t <ip> -p <port> -l -e <command>
                \t\t-> Listen on <ip>:<port> and execute command.
                (3) ./nethack2.py -t <ip> -p <port> -l -u <filename>
                \t\t-> Listen on <ip>:<port> and upload <filename>.
                (4) ./nethack2.py -t <ip> -p <port>
                \t\t-> Connect on <ip>:<port>.
                (5) <data> | ./nethack2.py -t <ip> -p <port>
                \t\t-> Send data to <ip>:<port>. 
                """
            )
        )
        parser.add_argument(
            "-t", "--target",
            action="store", type=str,
            help="IP Address"
        )
        parser.add_argument(
            "-p", "--port",
            action="store", type=int,
            help="Port Number"
        )
        parser.add_argument(
            "-l", "--listen",
            action="store_true",
            help="Listen" 
        )
        parser.add_argument(
            "-s", "--shell",
            action="store_true",
            help="Open shell"
        )
        parser.add_argument(
            "-e", "--execute",
            action="store", type=str,
            help="Execute command"
        )
        parser.add_argument(
            "-u", "--upload",
            action="store", type=str,
            metavar="FILE",
            help="Upload file"
        )
        self.args = parser.parse_args()

def main():
    if __name__ == "__main__":
        nethack = NetHack()
        nethack.manual()

main()