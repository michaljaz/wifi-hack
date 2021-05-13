from flask import Flask,render_template
from dotenv import load_dotenv
import os,multiprocessing,subprocess,atexit


if os.geteuid() != 0:
	print("This script requires sudo privs!")
	exit()


#kill all wifi processes
os.system("sudo airmon-ng check kill")


#restore wifi on exit
@atexit.register
def goodbye():
	print("Goodbye!")
	os.system("sudo service NetworkManager restart")


#load environment vars
load_dotenv()
wlan_name=os.getenv('WLAN_NAME')


#run aircrack in background
def runInBackground():
	os.system("sudo airmon-ng start "+wlan_name)

p=multiprocessing.Process(target=runInBackground)
p.start()


#flask
app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

app.run(port=8080)



