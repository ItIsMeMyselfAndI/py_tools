import argparse
import shlex
import socket
import subprocess
import socket
import sys
import textwrap
import threading

class NetHack:
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def createHelper(self):
		parser = argparse.ArgumentParser(
			description="[Network Hacking Tool]",
			formatter_class=argparse.RawDescriptionHelpFormatter,
			epilog=textwrap.dedent(
				"""\
				Example:
				\t(0) nethack.py -t <ip> -p <port> -l -s\t\t\t\t\t#Create server on <ip>:<port> and enable command shell
				\t(1) nethack.py -t <ip> -p <port> -l -e=\"echo 'hello, world!!'\"\t\t#Create server on <ip>:<port> and execute one comman
				\t(2) nethack.py -t <ip> -p <port> -l -u=OUTPUT_FILE\t\t\t#Create server on <ip>:<port> and upload a file <OUPUT_FILE>
				\t(3) nethack.py -t <ip> -p <port>\t\t\t\t\t#Connect to server on <ip>:<port>
				\t(4) nethack.py -t <ip> -p <port> -i\t\t\t#Connect to server and enable standard input.
			"""\
			)
		)
		parser.add_argument(
			"-t", "--target", action='store',
			type=str, help="IP address."
		)
		parser.add_argument(
			"-p", "--port", action='store',
			type=int, help="Port number."
		)
		parser.add_argument(
			"-l", "--listen", action='store_true', 
			help="Listen for upcomming connections (up to 5)."
		)
		parser.add_argument(
			"-s", "--shell", action='store_true',
			help="Provide command shell for the clients"
		)
		parser.add_argument(
			"-e", "--execute", action='store',
			type=str, help="Execute the command and get the output."
		)
		parser.add_argument(
			"-u", "--upload", action='store', metavar='OUTPUT_FILE',
			type=str, help="Upload file to the server."
		)
		parser.add_argument(
			"-i", "--stdinput", action='store_true',
			help="Enable standard input."
		)
		self.args = parser.parse_args()

	def server(self):
		self.socket.bind((self.args.target, self.args.port))
		print(f"[*] Started server on {self.args.target}:{self.args.port}.")
		self.socket.listen(5)
		print(f"[*] Waiting for connections...")
		while True:
			client, connection = self.socket.accept()
			print(f"[*] Accepted connection on {connection[0]}:{connection[1]}.")
			client_thread = threading.Thread(
				target=self.client_handler, 
				args=(client, connection)
			)
			client_thread.start()
		self.socket.close()

	def client_handler(self, client, connection):
		if self.args.shell:
			client.send("SHELL".encode())
			print(f"[*] Sent SHELL signal to {connection[0]}.")
			self._shell(client)
		elif self.args.execute:
			client.send("EXECUTE".encode())
			print(f"[*] Sent EXECUTE signal to {connection[0]}.")
			output = self._execute()
			client.send(output.encode())
		elif self.args.upload:
			client.send("UPLOAD".encode())
			print(f"[*] Sent UPLOAD signal to {connection[0]}.")
			self._upload(client, connection)
		client.close()

	def _shell(self, client):
		while True:
			cmd = self._recv_response(client)
			output = self._execute(cmd)
			client.send(output.encode())

	def _execute(self, cmd=None):
		if cmd == None:
			cmd = self.args.execute
		output = subprocess.check_output(
			shlex.split(cmd), 
			stderr=subprocess.STDOUT
		)
		return output.decode().strip()

	def _upload(self, client, connection):
		content = self._recv_response(client)
		with open(self.args.upload, 'w') as file:
			file.write(content)
		print(f"[*] Uploaded \"{self.args.upload}\" by {connection[0]}.")
		client.send(f"Uploaded \"{self.args.upload}\" to the server.".encode())

	def client(self):
		self.socket.connect((self.args.target, self.args.port))
		print("[*] You are connected.")
		if self.args.stdinput:
			std_input = sys.stdin.read()
			self.socket.send(std_input.encode())
			response = self._recv_response(self.socket)
			print(response)
		else:
			signal = self.socket.recv(4096).decode()
			print(f"[*] Recieved \"{signal}\" signal from server.")
			if signal == "SHELL":
				while True:
					cmd = input("Net@Hack #> ")
					cmd += '\n'
					self.socket.send(cmd.encode())
					output = self._recv_response(self.socket)
					print(textwrap.indent(output, prefix="  "))
			elif signal == "EXECUTE":
				output = self._recv_response(self.socket)
				print(textwrap.indent(output, prefix="  "))
			elif signal == "UPLOAD":
				content = sys.stdin.read()
				self.socket.send(content.encode())
				response = self.socket.recv(4096)
				print(f"[*] {response.decode()}")

	def _recv_response(self, s):
		buffer = b""
		buffer_len = len(buffer)
		while buffer_len % 4096 == 0:
			buffer += s.recv(4096)
			buffer_len = len(buffer)
		data = buffer.decode()
		return data 
		
	def run(self):
		self.createHelper()
		if self.args.listen:
			self.server()	
		else:
			self.client()



if __name__ == "__main__":
	nethack = NetHack()
	nethack.run()


