from flask import Flask
from flask_socketio import SocketIO
import base64
import os
from io import BytesIO
from PIL import Image
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", always_connect=True)
port = int(os.environ.get("PORT", 5000))

pathDetect=os.path.join(os.path.dirname(__file__), "yolov5/detect.py")
pathBest=os.path.join(os.path.dirname(__file__), "yolov5/best.pt")
pathTest=os.path.join(os.path.dirname(__file__), "yolov5/test")

@app.route("/")
def index():
    return "Hola desde el server de FungiDeTECtor!"

@socketio.on('setImages')
def setImages(res):
    cleanImages('yolov5/test/')
    for data in res:
        data = data.split(',')[1]
        im = Image.open(BytesIO(base64.b64decode(data)))
        ruta = 'yolov5/test/test' + str(getLastNum('yolov5/test/')) + '.png'
        im.save(ruta, 'PNG')
    getImages()

def recognition():
    process = subprocess.Popen("python "+pathDetect +" --weights "+pathBest+ " --source "+pathTest, shell=True)
    process.wait()

def getImages():
    recognition()
    os.chmod("yolov5/runs/detect/exp"+getLasFolder('yolov5/runs/detect')+'/', 755)
    pathResults = os.path.join(os.path.dirname(__file__), "yolov5/runs/detect/exp"+getLasFolder('yolov5/runs/detect')+'/')
    resultsList=[]
    for filename in os.listdir(pathResults):
        with open(pathResults+filename, "rb") as f:
            im_b64 = base64.b64encode(f.read())
            data=im_b64.decode('utf-8')
            jsoData = {
                "img": data,
            }
            resultsList.append(jsoData)
    socketio.emit('getImages',resultsList, broadcast=True)

def getLastNum(path):
    num=0
    for filename in os.listdir(path):
        with open(path+filename, "rb") as f:
            num+=1
    if num==1:
        return ''
    return str(num+1)

def getLasFolder(path):
    num=0
    with os.scandir(path) as ficheros:
        for fichero in ficheros:
            if fichero.is_dir():
                num += 1
    if num==1:
        return ''
    return str(num)

def cleanImages(path):
    for filename in os.listdir(path):
        os.remove(path + filename)

if __name__ == "__main__":
    #socketio.run()
    socketio.run(app, host='0.0.0.0', debug=True, port=port)