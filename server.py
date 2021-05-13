from flask import Flask,render_template
from time import sleep
import os,multiprocessing,subprocess
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

wlan_name=os.getenv('WLAN_NAME')

if os.geteuid() != 0:
	print("This script requires sudo privs!")
	exit()

@app.route('/')
def index():
	return render_template("index.html")

def runApp():
	print('Running app in background')
	app.run(port=8080)

if __name__ == '__main__':
	p=multiprocessing.Process(target=runApp)
	p.start()

os.system("sudo airmon-ng start "+wlan_name)
