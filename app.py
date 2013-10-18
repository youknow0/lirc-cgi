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
import sqlite3
from flask import Flask, render_template, g, request, redirect, url_for, jsonify
from contextlib import closing
from lirc import Lirc

# configuration
DATABASE = 'flaskr.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.query_db = query_db
	g.db = connect_db()
	g.db.row_factory = sqlite3.Row

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

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

@app.route('/api/0.1/exec/<dev_id>/<cmd_id>')
def exec_command(dev_id, cmd_id):
	lirc = Lirc()
	cmd = lirc.get_command(dev_id, cmd_id)
	lirc.execute(cmd)

	jsonResponse = jsonify(success=True)
	jsonResponse.headers["Access-Control-Allow-Origin"] = "*"
	
	return jsonResponse

@app.route('/options')
def options():
	return render_template('options.html')

@app.route('/options/devicenames')
def set_device_names():
	lirc = Lirc()
	dev = lirc.get_devices()

	return render_template('options_devicenames.html', devices=dev)

@app.route('/options/commandnames')
def set_command_names_choose_device():
	lirc = Lirc()
	dev = lirc.get_devices()

	return render_template('options_commandnames_choosedevice.html', devices=dev.values())

@app.route('/options/commandnames/<dev_id>')
def set_command_names(dev_id):
	lirc = Lirc()
	dev = lirc.get_device(dev_id)

	return render_template('options_commandnames.html', commands=dev.get_commands(), dev_id=dev_id)

@app.route('/options/devicenames', methods=['POST'])
def save_device_names():
	lirc = Lirc()
	devices = lirc.get_devices()

	for dev in devices.values():

		my_name = request.form[dev.dev_id + '_name']

		if my_name != None:
			result = dev.set_name(my_name)
			app.logger.warning('device id has value: %s, name: %s, (b:%s), (d: %s)', dev.dev_id, my_name, result, dev)

	return redirect(url_for('set_device_names'))

@app.route('/options/commandnames/<dev_id>', methods=['POST'])
def save_command_names(dev_id):
	lirc = Lirc()
	dev = lirc.get_device(dev_id)

	for cmd in dev.get_commands():

		my_name = request.form[cmd.cmd_id + '_name']

		if my_name != None:
			result = cmd.set_name(my_name)

	return redirect(url_for('set_command_names', dev_id=dev_id))

def _cmd_to_dict(cmd):
	json_cmd = {}
	json_cmd['cmd_id'] = cmd.cmd_id
	json_cmd['name'] = cmd.name
	json_cmd['dev_id'] = cmd.get_device().dev_id
	
	return json_cmd

def _dev_to_dict(dev):
	json_dev = {}
	json_dev['id'] = dev.dev_id
	json_dev['name'] = dev.name
	json_cmds = {}
	cmds = dev.get_commands()
	
	for cmd in cmds:
		json_cmds[cmd.cmd_id] = _cmd_to_dict(cmd)
		
	json_dev['commands'] = json_cmds
	
	return json_dev
	
@app.route('/api/0.1/devices')
def api_get_devices():
	lirc = Lirc()
	devices = lirc.get_devices()
	
	payload = {}
	for dev in devices.values():
		payload[dev.dev_id] = _dev_to_dict(dev)
		
	response = {}
	response['success'] = True
	response['payload'] = payload
	
	jsonResponse = jsonify(response)
	jsonResponse.headers["Access-Control-Allow-Origin"] = "*"
	
	return jsonResponse

if __name__ == '__main__':
	#app.debug = True
	app.run(host='0.0.0.0')


