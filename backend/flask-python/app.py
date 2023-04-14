from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from testserver import emulated
import socket
import json
import time
import datetime
from threading import Thread
app = Flask(__name__)
CORS(app)
TERMINATE = 'exit'


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/getstatus', methods=['POST'])
@cross_origin(support_credentials=True)
def login():
    # testing edits on container based on local files
    # server only uses new app.py
    # when flask app is rerun when container restarts
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

''' Gets data from API json, and calls configHelper with isDummy bool set to false
    to get actual data from Yamaha CL5
'''
@app.route('/getYamahaProfile', methods=['POST'])
@cross_origin(support_credentials=True)
def getYamahaProfile():
    # Grab arguments from api call
    content = request.json
    channel = int(content['channel'])
    PORT = int(content['PORT'])
    mix = int(content['mix'])
    HOST = content['HOST']

    return configHelper(channel,PORT,mix,HOST,False), 200

''' Gets data from API json, and calls configHelper with isDummy bool set to true
    to create a fake yamaha console to get dummy data from.
'''
@app.route('/getDummyProfile', methods=['POST'])
@cross_origin(support_credentials=True)
def getDummyProfile():
    # Grab arguments from api call
    content = request.json
    channel = int(content['channel'])
    PORT = int(content['PORT'])
    mix = int(content['mix'])
    HOST = content['HOST']

    return configHelper(channel,PORT,mix,HOST,True), 200

@app.route('/setDummyProfile', methods=['POST'])
@cross_origin(support_credentials=True)
def setDummyProfile():
    # Grab arguments from api call
    content = request.json
    channel = int(content['channel'])
    PORT = int(content['PORT'])
    mix = int(content['mix'])
    HOST = content['HOST']
    file = content['file']

    return setConfigHelper(channel,PORT,mix,HOST,file,True), 200

def configHelper(channel,PORT,mix,HOST,isDummy):
    # Define prefixes and infixes to generate commands
    validPrefix = ['get']
    validInfix = ['MIXER:Current/InCh/Label/Name',
                  'MIXER:Current/InCh/ToMix/Level',
                  'MIXER:Current/InCh/ToMix/Pan',
                  'MIXER:Current/InCh/ToMix/On']

    # Define 1 to 1 relation between labels and types
    labels = ['Name', 'Level', 'Pan', 'On']
    types = ['str', 'int', 'int', 'bool']

    # Define Base Layout for JSON data response
    jsonFormat = {
        "filename": "CL5.json",
        "version": "0.1",
        "timestamp": 'temp',
        "user": "",
        "mixes": []}
    if isDummy:
        # Define config for CL5 emulator, and start thread
        config = ['0.0.0.0', PORT, mix, channel]
        thread = Thread(target=emulated.echoServer, args=([config]))
        thread.start()

        # Wait for thread to spin up
        time.sleep(1)

    # Open Socket to emulator thread
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # For all mixes
        for i in range(1, mix+1):
            # Temp dictionary to hold mix data
            mix_dict = {}
            for j in range(1, channel+1):
                # Temp dictionary to hold channel data
                channel_dict = {}

                # For each Parameter to read
                for k in range(len(labels)):

                    # generate tcp message based on indexes of i,j,k
                    command = validPrefix[0] + ' ' + \
                        validInfix[k] + ' ' + str(j) + ' ' + str(i)

                    # Send message and wait for response
                    s.sendall(command.encode())
                    response = s.recv(1024).decode().split()[-1]

                    # Add value of message to channel json data based on type and label
                    if types[k] == 'str':
                        channel_dict[labels[k]] = str(response)
                    elif types[k] == 'int':
                        channel_dict[labels[k]] = int(response)
                    elif types[k] == 'bool' and response.lower() is 'true':
                        channel_dict[labels[k]] = True
                    else:
                        channel_dict[labels[k]] = False
                # append channel data to mixes
                mix_dict[str(j)] = channel_dict
            # append mix data to json
            jsonFormat["mixes"].append({str(i): mix_dict})
        if isDummy:
            # Send signal to emulator to kill itself
            s.send(TERMINATE.encode())
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            # wait for thread to finish dying
            thread.join()
        else:
            s.shutdown(socket.SHUT_RDWR)
            s.close()
    # append datatime to json
    now = datetime.datetime.now()
    jsonFormat["timestamp"] = str(now)

    # return json to api
    json_str = json.dumps(jsonFormat)
    return json_str

def setConfigHelper(channel,PORT,mix,HOST,file,isDummy):
    # Define prefixes and infixes to generate commands
    validPrefix = ['set']
    validInfix = ['MIXER:Current/InCh/Label/Name',
                  'MIXER:Current/InCh/ToMix/Level',
                  'MIXER:Current/InCh/ToMix/Pan',
                  'MIXER:Current/InCh/ToMix/On']

    # Define 1 to 1 relation between labels and types
    labels = ['Name', 'Level', 'Pan', 'On']
    types = ['str', 'int', 'int', 'bool']

    # Define Base Layout for JSON data response
    jsonFormat = {
        "filename": "CL5.json",
        "version": "0.1",
        "timestamp": 'temp',
        "user": "",
        "mixes": []}
    
    load_data = json.loads(file)

    if isDummy:
        # Define config for CL5 emulator, and start thread
        config = ['0.0.0.0', PORT, mix, channel]
        thread = Thread(target=emulated.echoServer, args=([config]))
        thread.start()

        # Wait for thread to spin up
        time.sleep(1)

    # Open Socket to emulator thread
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        for m in load_data['mixes'][0]:
            for c in load_data['mixes'][0][mix]:
                for i, x in enumerate(labels):
                    if x == 'On':
                        command = validPrefix[0] + ' ' + validInfix[i] + ' ' + c + ' ' + m + ' ' + str(int(load_data['mixes'][0][mix][channel][x]))
                    else:
                        command = validPrefix[0] + ' ' + validInfix[i] + ' ' + c + ' ' + m + ' ' + str(load_data['mixes'][0][mix][channel][x])
                    s.sendall(command.encode())
                    response = s.recv(1024).decode().split()[-1]

        if isDummy:
            # Send signal to emulator to kill itself
            s.send(TERMINATE.encode())
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            # wait for thread to finish dying
            thread.join()
        else:
            s.shutdown(socket.SHUT_RDWR)
            s.close()

    # return json to api
    json_str = json.dumps(jsonFormat)
    return json_str
