#!/usr/bin/python

import os
import sys
import socket
import time
from threading import Thread
import configparser

# ***** controller class *****

class ClockServer(Thread):

	def __init__(self):
		Thread.__init__(self)

		self._clients = {}
		self._is_started = False

	def register(self, cid, client):
		self._clients[cid] = client

	def unregister(self, cid):
		del self._clients[cid]

	def stop(self):
		self._is_started = False

	def run(self):
		self._is_started = True

		while self._is_started:

			# ***** decode time info *****
			crt_time = time.localtime() 

			crt_hour = crt_time.tm_hour % 12 
			crt_min = (crt_time.tm_min - crt_time.tm_min % 5) / 5
			crt_sec = (crt_time.tm_sec - crt_time.tm_sec % 5) / 5

			disp = 'second'
			if crt_time.tm_min % 5 == 0 and crt_time.tm_sec <= 2:
				disp = 'hour'
			elif crt_time.tm_min % 5 == 0 and crt_time.tm_sec <= 4:
				disp = 'minute'

			for k, c in self._clients.items():
				
				cid = int(k)
				crt_hour_bool = (crt_hour & (1 << (cid - 1))) >> (cid - 1)
				crt_min_bool = (crt_min & (1 << (cid - 1))) >> (cid - 1)
				crt_sec_bool = (crt_sec & (1 << (cid - 1))) >> (cid - 1)

				msg = 'none'
				if disp == 'hour' and crt_hour_bool == 1:
					msg = 'green'
				elif disp == 'minute' and crt_min_bool == 1:
					msg = 'blue'
				elif disp == 'second' and crt_sec_bool == 1:
					msg = 'red'

				print('>', k, msg)

				try:
					c.sendall(msg)
				except socket.error as exc:
					print('SOCKET ERROR :', exc)
					self.unregister(k)

			time.sleep(0.5)

		for k, c in self._clients.items():
			c.sendall('none')
			time.sleep(0.5)

			#c.sendall('stop')
			#time.sleep(0.5)

			c.close()

# ***************************
# ***************************

config = configparser.RawConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'clock.cfg'))

# ***** init socket *****
host = config.get('led_server', 'host')        # Get local machine name
port = config.getint('led_server', 'port')     # Reserve a port for your service.

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)         # Create a socket object
s.bind((host, port))        # Bind to the port

s.listen(5)                 # Now wait for client connection.

ctrl = ClockServer()
ctrl.start()

is_started = True
while is_started:

	try:
		print('> listen ', host, ',', port)
		c, addr = s.accept()     # Establish connection with client.

		c.sendall('hello')       # send hello message

		cid = c.recv(1024)       # receive cid from client

		if cid == 'stop':
			print('>', cid)
			is_started = False
			continue

		print('> register client', cid, 'from', addr)
		ctrl.register(cid, c)

	except socket.error as exc:
		print('> SOCKET ERROR :', exc)

c.close()
ctrl.stop()

