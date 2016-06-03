from psutil import *
from flask import Flask, render_template, url_for, request, jsonify, Response
import json

app = Flask(__name__)

def get_cpu_usage():
	return cpu_percent(interval=1)

def get_memory_details():
	return  virtual_memory().percent

def network_usage():
	return {'sent' :net_io_counters(pernic=False).bytes_sent, 'recv' :net_io_counters(pernic=False).bytes_recv}

def get_disk_usage():
	return disk_usage('/').percent

@app.route('/')
def home():
	data = {'cpu' : get_cpu_usage(), 'memory' : get_memory_details(), 'network' :network_usage(), 'disk' : get_disk_usage()}
	return json.dumps(data)

if __name__ == "__main__":
	app.debug = True
	app.run('', port=3000, threaded=True)