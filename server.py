from flask import Flask,render_template
import multiprocessing
from time import sleep

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

def runApp():
	print('Running app in background')
	app.run(port=8080)

if __name__ == '__main__':
	p=multiprocessing.Process(target=runApp)
	p.start()
sleep(2)
print('test')
