from flask import Flask,render_template,url_for
from dotenv import load_dotenv
import os,multiprocessing,subprocess,atexit,psutil

WIFI_DISABLE=False

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


#flask
app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

app.run(port=8080)



