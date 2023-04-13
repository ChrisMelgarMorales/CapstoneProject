# echo-server.py

import socket
import json
import os
import time

'''This functions takes a token list, and checks if tokens are in the correct format'''


def validateTokens(tokens, config):
    MIXES = config[2]
    CHANNELS = config[3]
    # define valid paths
    validPrefix = ['get', 'set']
    validInfix = ['MIXER:Current/InCh/Label/Name',
                  'MIXER:Current/InCh/ToMix/Level',
                  'MIXER:Current/InCh/ToMix/Pan',
                  'MIXER:Current/InCh/ToMix/On']

    # Check if tokens are invalid compared to expected values
    isValidPrefix = tokens[0] in validPrefix
    isValidInfix = tokens[1] in validInfix
    isValidChannel = int(tokens[2]) <= CHANNELS
    isValidMixes = int(tokens[3]) <= MIXES
    isValidLength = len(tokens) == 4
    if not (isValidPrefix and isValidInfix and isValidChannel and isValidMixes and isValidLength):
        err = tokens[0]+tokens[1]+tokens[2]+tokens[3]
        raise Exception(err)

    # get index of infix
    index = -1
    for i in range(len(validInfix)):
        if tokens[1] in validInfix[i]:
            index = i
            break
    # return list containing command, infix index, Mix and channel
    return [0, i, tokens[3], tokens[2]]


'''This function takes a loaded json file in python format, and find the entry required,
baased on the command given'''


def getData(data, command):
    labels = ["Name", "Level", "Pan", 'On']
    # Get value from json based on command
    configData = data['mixes'][0][command[2]][command[3]][labels[command[1]]]
    return str(configData)


'''This function takes a command given by a connect client,
and return the entry from a json file, to replicate a Yamaha CL5'''


def echoServer(config):
    print("Thread Running")
    # Define arguments for socket based on parameters
    HOST = config[0]
    PORT = config[1]

    # Get path for dummy file
    f = open("testserver/dummy.json")

    # open socket for server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print("Bound")
        s.listen()
        print("Listening")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            CL5 = json.load(f)
            while True:
                data = conn.recv(1024).decode()

                # Validate and execute command
                try:
                    # end function when recieving exit as tcp message
                    if data == 'exit':
                        break

                    # process tcp message and return response from dummy.json
                    command = validateTokens(data.split(), config)
                    response = 'OK ' + data + ' ' + getData(CL5, command)
                    conn.sendall(response.encode())

                except socket.error as e:
                    print("terminating emulators")
                    break
        s.shutdown(socket.SHUT_RDWR)
        s.close()
'''#Code needs to be able to run either command and either save or load the data from and to the json
                #json must be saved after server is done running.
                print(data)
                if len(data.split()) > 0 and data.split()[0] == 'get':
                    try:
                        command = validateTokens(data.split())
                        print(command)
                        if command == []:
                            break
                        response  = 'OK ' + data + ' ' + getData(CL5,command)
                    except Exception as e:
                        print(e)
                        response = "FAILED TO PROCESS"
                    finally:
                        time.sleep(.1)
                        conn.sendall(response.encode())
                elif len(data.split()) > 0 and data.split()[0] == 'set':
                    # No need to validate tokens for set commands
                    # The commands cannot change, they are hardcoded
                    response = 'OK ' + data + ' LOADED'
                    conn.sendall(response.encode())
                else:
                    break
                '''


