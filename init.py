async_mode = None

if async_mode is None:
	try:
		import eventlet
		async_mode = "eventlet"
	except ImportError:
		pass

	if async_mode is None:
		try:
			from gevent import monkey
			async_mode = 'gevent'
		except ImportError:
			pass

	if async_mode is None:
		async_mode = 'threading'

	print "async_mode is ", async_mode

if async_mode == 'eventlet':
	import eventlet
	eventlet.monkey_patch()
elif async_mode == 'gevent':
	from gevent import monkey
	monkey.patch_all()

from flask import Flask, render_template, url_for, request, jsonify, Response, copy_current_request_context
import random, time, json, urllib2, requests

import ast

from flask_socketio import SocketIO, send, emit

from threading import Thread

CONNECTED_HOSTS = ['localhost'] #, '192.168.144.136', '192.168.144.140', '192.168.144.224']
CLIENT_PORT = '3000'

THRESHOLDS = {'cpu' : 10, 'memory' : 80, 'network_sent' : 1000000000, 'network_recv' : 1000000000 }

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)

def monitor_in_background():
	print "DaemonThread : Started monitoring in background"
	global socketio
	while True:
		data = collect_hosts_data()
		for host in data:
			host = ast.literal_eval(json.dumps(host))
			if host['cpu'] > THRESHOLDS['cpu']:
				print "CPU usage alert from ", host['ip']

			if host['memory'] > THRESHOLDS['memory']:
				print "Memory usage alert from ", host['ip']

			if host['network']['recv'] > THRESHOLDS['network_recv']:
				print "Network Received usage alert from ", host['ip']
				THRESHOLDS['network_recv'] += 10000000	#increase in 10Mb on threashold

			if host['network']['sent'] > THRESHOLDS['network_sent']:
				print "Network Sent usage alert from ", host.ip
				THRESHOLDS['network_sent'] += 10000000	#increase in 10Mb on threashold
			
		#socketio.emit('channel_compare_resources_resp', json.dumps(data))
		time.sleep(1)



def collect_hosts_data():
	array = []
	if True:
		for ip in CONNECTED_HOSTS:
			url = "http://" + ip + ":" + CLIENT_PORT + "/"
			try:
				data = requests.get(url, timeout=2)
				data =  data.json()
				data['ip'] = ip
				array.append(data)
			except:
				print "Unable to connect to ", ip
		return array
		#return Response(json.dumps(array), mimetype='application/json')

def collect_single_host_data(client_ip):
	data = None
	url = "http://" + client_ip + ":" + CLIENT_PORT + "/"
	try:
		data = requests.get(url)
		data =  data.json()
	except:
		print "Unable to connect to ", ip
	return data
	#return Response(json.dumps(array), mimetype='application/json')


#Renders the home page of the application server.
@app.route('/')
@app.route('/home')
def home():
	#print url_for('static', filename='../js/statistics.js')
	return render_template('home.html', title="Home")


@app.route('/host/')
@app.route('/host/<host_id>')
def host_info(host_id=None):
	if host_id != None:
		print "Rendering graph template with id : ", host_id
		return render_template('host_info.html', title="Host Info", host_id=host_id)
	else:
		print "Rendering to display all container ids"
		return render_template('host_info.html', title="Container Info")

@app.route('/compare_resources')
def compare_resources():
	return render_template('compare_resources.html')


""" THIS NEEDS TO BE REPLACED BY SOCKETIO METHOD"""
""" Rest api that serves the json data for various ajax requests """
@app.route('/jsondata/')
@app.route('/jsondata/<int:pc_id>')
def json_data(pc_id=None):
	print "Request received"
	if pc_id == None:
		array = collect_hosts_data()
		return Response(json.dumps(array), mimetype='application/json')
	else:
		pc_ip = CONNECTED_HOSTS[pc_id]
		url = "http://" + pc_ip + ":" + CLIENT_PORT + "/"
		data = requests.get(url)
		data = data.json()
		return Response(json.dumps(data), mimetype='application/json')

@app.route('/jsondata_containers')
def json_data_containers():
	data = requests.get(SERVER_ADDRESS + '/containers/json?all=1')
	data = data.json()
	data = Response(json.dumps(data),  mimetype='application/json')
	emit('container_ids', data, broadcast=True)
	return data

@app.route('/container_stats_one/<container_id>')
def container_stats_one(container_id=None):
	if container_id != None:
		resp = requests.get(SERVER_ADDRESS + '/containers/' + container_id + '/stats?stream=false')
		data = resp.json()
		return Response(json.dumps(data), mimetype='application/json')
	else:
		return jsonify('{}')

@app.route('/container_stats_stream/<container_id>')
def container_stats_stream(container_id=None):
	if container_id != None:
		resp = requests.get(SERVER_ADDRESS + '/containers/' + container_id + '/stats?stream=true')
		data = resp.json()
		return Response(json.dumps(data), mimetype='application/json')
	else:
		return jsonify('{}')


@socketio.on('channel_compare_resources_init_req')
def channel_compare_resources_init():
	global socketio
	print "Client requested for Comparision data intialisation"
	data = collect_hosts_data()
	socketio.emit('channel_compare_resources_init_resp', json.dumps(data))


@socketio.on('channel_compare_resources_req')
def channel_compare_resources():
	global socketio
	print "Client requested for Comparision data"
	data = collect_hosts_data()
	socketio.emit('channel_compare_resources_resp', json.dumps(data))


@socketio.on('channel_hosts_list_req')
def channel_hosts_list(c_req):
	global socketio
	print "Client requested for the list of connected hosts"
	data = collect_hosts_data()
	socketio.emit('channel_hosts_list_resp', json.dumps(data))

@socketio.on('channel_hosts_list_req_1')
def channel_hosts_list(c_req):
	global socketio
	print "Client requested for the list of connected hosts"
	data = collect_hosts_data()
	socketio.emit('channel_hosts_list_resp_1', json.dumps(data))

@socketio.on('channel_host_info_req')
def channel_host_info(host_id):
	global socketio
	print "Client requested data of ip: ", host_id
	data = collect_single_host_data(host_id)
	print "Sending data ", data
	socketio.emit('channel_host_info_resp', json.dumps(data))

if __name__ == "__main__":

	thread = Thread(target=monitor_in_background)
	thread.daemon = True
	thread.start()

	socketio.run(app, '', port=5001, debug=True)






