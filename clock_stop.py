#!/usr/bin/python

import os
import sys
import socket
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'clock.cfg'))

host = config.get('led_server', 'host')
port = config.getint('led_server', 'port')

s = socket.socket()         # Create a socket object

print '> connect to :', host, ',', port
s.connect((host, port))

# ***** wait for hello message *****
msg = s.recv(1024)
print '>', msg

if msg != 'hello':
	s.close
	sys.exit()

# ***** answer with cid *****
s.send('stop')
s.close
