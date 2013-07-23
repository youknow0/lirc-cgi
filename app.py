#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  www.py
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
from lirc import Lirc
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def list_devices():
	lirc = Lirc()
	dev = lirc.get_devices()

	return render_template('index.html', devices=dev)

@app.route('/devices/<dev_id>/')
def list_commands(dev_id):
	lirc = Lirc()
	dev = lirc.get_device(dev_id)
	commands = sorted(dev.get_commands(), key=lambda cmd: cmd.name)

	return render_template('device.html', dev=dev, commands=commands)

@app.route('/devices/<dev_id>/<cmd_id>')
def exec_command(dev_id, cmd_id):
	lirc = Lirc()
	cmd = lirc.get_command(dev_id, cmd_id)
	lirc.execute(cmd)

	return render_template('command.html')


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
