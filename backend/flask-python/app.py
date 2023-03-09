from flask import Flask,request,jsonify
from flask_cors import CORS , cross_origin
from testserver import emulated
import socket
import json
import time
from threading import Thread
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/getstatus',methods = ['POST'])
@cross_origin(support_credentials=True)
def login():
        #testing edits on container based on local files
        #server only uses new app.py
        #when flask app is rerun when container restarts
        HOST = 'host.docker.internal'
        PORT = 5002
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'Hello World')
            data = s.recv(1024)
        f = open('data.json')
        data = json.load(f)
        json_str = json.dumps(data)
        return json_str, 200
@app.route('/getDummyProfile',methods = ['POST'])
@cross_origin(support_credentials=True)
def dummy():
        #testing edits on container based on local files
        #server only uses new app.py
        #when flask app is rerun when container restarts
        content = request.json
        channel = int(content['channel'])
        mix = int(content['mix'])
        print(channel)
        print(mix)
        validPrefix = ['get']
        validInfix = ['MIXER:Current/InCh/Label/Name',
                  'MIXER:Current/InCh/ToMix/Level',
                  'MIXER:Current/InCh/ToMix/Pan',
                  'MIXER:Current/InCh/ToMix/On']
        lables =  ['Name','Level','Pan','On']
        types = ['str','int','int','bool']
        jsonFormat  = {
    "filename": "CL5.json",
    "version": "0.1",
    "user": "",
    "mixes": []}
        config = ['0.0.0.0',5001,mix,channel]
        HOST = '127.0.0.1'
        PORT = 5001
        thread = Thread(target=emulated.echoServer, args=([config]))
        thread.start()
        time.sleep(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            mixChannelDictionary =[]
            for i in range(1,mix+1):
                channelValueList = []
                for j in range(1,channel+1):
                    entryList = []
                    for k in range(4):

                        command = validPrefix[0] + ' ' + validInfix[k] + ' ' + str(j) + ' ' + str(i)
                        s.sendall(command.encode())
                        
                        response = s.recv(1024).decode()[-1]
                    
                        strErr = "Sorry, no numbers" + command + config[0]+str(config[1])+str(config[2])+str(config[3])+response
                        print(strErr)
                        if types[k] == 'str':
                            entryList.append(str(response))
                        elif types[k] == 'int':
                            entryList.append(int(response))
                        elif types[k] == 'bool':
                            entryList.append(bool(response))
                    channelValueList.append({lables[x]: entryList[x] for x in range(len(lables))})   
                mixChannelDictionary.append({str(x):channelValueList[x] for x in range(len(channelValueList))})
            
            jsonFormat['mixes'].append(mixChannelDictionary)
        json_str = json.dumps(jsonFormat)
        return json_str, 200
'''try:
   if request.method == 'POST':
        try:
            channel = request.form.get('channel')
            mix = request.form.get('mix')
            command = request.form.get('command')
            PORT = request.form.get('PORT')
            HOST = request.form.get('HOST')
            prefix = 'get MIXER:Current/InCh/'
            LabelInfix= 'Label/Name'
            ToMixInfix =['ToMix/','On','Level','Pan']
            postfix = ' {} {}'.format(channel,mix)

            if command is '1111':

                import socket
                commandList = []
                str = prefix+LabelInfix+postfix
                commandList.append(str)
                for i in range(1,4):
                    tempstr=prefix+ToMixInfix[0]+ToMixInfix[i]+postfix
                    commandList.append(tempstr)
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    for i in commandList:
                        s.sendall(i.encode('utf-8'))
                        data = s.recv(1024)
                        print(f"Received {data!r}")
        except Exception as e:

            result = {'a': str(e)}
            return result, 201
        '''