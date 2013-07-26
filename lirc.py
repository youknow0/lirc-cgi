#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lirc.py
#  
#  Copyright 2013 Nico Boehr <nico@zoff>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import subprocess
from flask import g

class Lirc:

	def get_devices(self):
		# request a list of all devices from lirc
		output = subprocess.check_output(["irsend", "LIST", "", ""], stderr=subprocess.STDOUT)

		lines = output.split("\n")

		# this is the dict of devices we will be returning
		# the key is the device id
		devices = {}
		for line in lines:
			device_detail = line.partition(": ")

			if device_detail[2] != "":
				dev_id = device_detail[2]
				dev_name = self._get_device_name_by_id(dev_id)

				# construct new device
				devices[dev_id] = self._create_device(dev_id, dev_name)

		return devices

	def execute(self, cmd):
		cmd_id = cmd.cmd_id
		dev_id = cmd.get_device().dev_id

		subprocess.check_call(["irsend", "SEND_ONCE", dev_id, cmd_id])

	def _create_device(self, dev_id, dev_name):
		# construct new device
		device = Device(dev_id, dev_name)

		# request a list of commands from lirc
		cmd_output = subprocess.check_output(["irsend", "LIST", dev_id, ""], stderr=subprocess.STDOUT)

		cmd_lines = cmd_output.split("\n")

		for cmd_line in cmd_lines:
			cmd_detail = cmd_line.split(" ")

			if len(cmd_detail) >= 3:
				cmd_id = cmd_detail[2]
				cmd_name = self._get_command_name_by_id(dev_id, cmd_id)

				cmd = Command(cmd_id, cmd_name)

				# add the command to the device
				device.add_command(cmd)

		return device

	def _get_device_name_by_id(self, dev_id):
		name = g.query_db('SELECT name FROM devices WHERE dev_id=?', [dev_id], one=True)

		if name == None:
			return dev_id

		return name[0]

	def _get_command_name_by_id(self, dev_id, cmd_id):
		name = g.query_db('SELECT name FROM commands WHERE dev_id=? AND cmd_id = ?', [dev_id, cmd_id], one=True)

		if name == None:
			return cmd_id

		return name[0]

	def get_device(self, dev_id):
		dev_name = self._get_device_name_by_id(dev_id)
		return self._create_device(dev_id, dev_name)

	def get_command(self, dev_id, cmd_id):
		dev = self.get_device(dev_id)

		return dev.commands[cmd_id]

class Device:

	def __init__(self, dev_id, name):
		self.dev_id = dev_id
		self.name = name
		self.commands = dict()

	def add_command(self, cmd):
		cmd.set_device(self)
		self.commands[cmd.cmd_id] = cmd

	def get_commands(self):
		return self.commands.values()

	def set_name(self, name):
		cur = g.db.execute(
			'INSERT OR REPLACE INTO devices(name, dev_id) VALUES(?, ?)',
			(name, self.dev_id))

		g.db.commit()

		self.name = name

	def __repr__(self):
		my_repr = "Lirc Device id:" + self.dev_id + "\n"
		my_repr += "Commands:\n"

		for cmd in self.commands.values():
			my_repr += "  " + repr(cmd)

		return my_repr

class Command:

	def __init__(self, cmd_id, name):
		self.cmd_id = cmd_id
		self.name = name

	def set_device(self, dev):
		self.device = dev

	def get_device(self):
		return self.device

	def set_name(self, name):
		if self.device == None:
			return
		
		cur = g.db.execute(
			'INSERT OR REPLACE INTO commands(name, dev_id, cmd_id) VALUES(?, ?, ?)',
			(name, self.device.dev_id, self.cmd_id))

		g.db.commit()

		self.name = name

	def __repr__(self):
		my_repr = "Command id:" + self.cmd_id + "\n"

		return my_repr

