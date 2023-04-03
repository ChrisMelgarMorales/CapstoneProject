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


@app.route('/getDummyProfile', methods=['POST'])
@cross_origin(support_credentials=True)
def dummy():
    # Grab arguments from api call
    content = request.json
    channel = int(content['channel'])
    PORT = int(content['PORT'])
    mix = int(content['mix'])
    HOST = content['HOST']
    PORT = 5001
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

        # Send signal to emulator to kill itself
        s.sendall(TERMINATE.encode())

    # wait for thread to finish dying
    thread.join()
    # append datatime to json
    now = datetime.datetime.now()
    jsonFormat["timestamp"] = str(now)

    # return json to api
    json_str = json.dumps(jsonFormat)
    return json_str, 200
