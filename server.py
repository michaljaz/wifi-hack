from flask import Flask,render_template,jsonify,make_response
from dotenv import load_dotenv
import time
import os,multiprocessing,subprocess,atexit,psutil
import csv

WIFI_DISABLE=False
PORT=8080

#check privs
if os.geteuid() != 0:
	print("This script requires sudo privs!")
	exit()


#load environment vars
load_dotenv()
wlan_name=os.getenv('WLAN_NAME')
monitor_name=os.getenv('MONITOR_NAME')


#check wifi interface
addresses = psutil.net_if_addrs()
stats = psutil.net_if_stats()

available_networks = []
for intface, addr_list in addresses.items():
    if any(getattr(addr, 'address').startswith("169.254") for addr in addr_list):
        continue
    elif intface in stats and getattr(stats[intface], "isup"):
        available_networks.append(intface)

if not wlan_name in available_networks:
	print(wlan_name+" interface not found!")
	exit()


#kill all wifi processes
if WIFI_DISABLE:
	os.system("sudo airmon-ng check kill")


#restore wifi on exit
@atexit.register
def goodbye():
	os.remove("log-01.csv")
	os.system("airmon-ng stop "+monitor_name)
	if WIFI_DISABLE:
		os.system("sudo service NetworkManager restart")
	print("\nGoodbye!")


#run aircrack
os.system("sudo airmon-ng start "+wlan_name)

def runAircrack():
	os.system("sudo airodump-ng -w log --output-format csv "+monitor_name+" > /dev/null 2>&1")	
multiprocessing.Process(target=runAircrack).start()

#adb connector
def connectAdb():
	while True:
		os.system("adb reverse tcp:"+str(PORT)+" tcp:"+str(PORT))
		time.sleep(10)
multiprocessing.Process(target=connectAdb).start()


#flask
app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/probes/')
def probes():
	return render_template("probes.html")

@app.route('/ownap/')
def ownap():
	return render_template("ownap.html")

@app.route('/nearwifis/')
def nearwifis():
	return render_template("nearwifis.html")

@app.route('/api/data/')
def data():
	with open('log-01.csv', 'r') as file:
		reader = csv.reader(file)
		db=[]
		for row in reader:
			xd=[]
			for col in row:
				xd.append(col)
			db.append(xd)
		return make_response(jsonify(db), 200)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.run(port=PORT)



