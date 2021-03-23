#!/usr/bin/python

import os
import sys
import socket
import time
from threading import Thread
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'clock.cfg'))

cid = config.getint('led_client', 'cid')
host = config.get('led_server', 'host')
port = config.getint('led_server', 'port')

# ***** controller class *****

class ClockClient(Thread):

	def __init__(self, host, port, cid):
		Thread.__init__(self)

		self._host = host
		self._port = port
		self._cid = cid
		self._is_started = False

	def stop(self):
		self._is_started = False

	def connect(self):
		# ***** connect to server *****
		s = socket.socket()         # Create a socket object
		s.settimeout(5)             # timeout = 5s

		while True:
			try:
				print '> connect to :', self._host, ',', self._port

				s.connect((self._host, self._port))

				# ***** wait for hello message *****
				msg = s.recv(1024)
				print '>', msg

				if msg != 'hello':
					s.close
					sys.exit()

				# ***** answer with cid *****
				s.send(str(self._cid))

				break

			except socket.error as exc:
				print '> SOCKET ERROR : ', exc
		
			time.sleep(5)

		return s

	def run(self):

		s = self.connect()

		cnt = 0

		self._is_started = True
		while self._is_started:

			cnt = cnt + 1
			try:
				msg = s.recv(1024)

				if msg == '':
					print 'SOCKET ERROR : socket closed'
					s.close()

					s = self.connect()
					continue

			except socket.error as exc:
				print 'SOCKET ERROR : ', exc
				s.close()

				s = self.connect()
				continue

			# ***** stop command *****
			if msg == 'stop':
				self.stop()
				continue

			# ***** other = led command *****
			os.popen('rgb %s' % (msg)) 
			#print '> led :', msg

		s.close()                     # Close the socket when done

# ***************************
# ***************************

ctrl = ClockClient( host, port, cid )
ctrl.start()

