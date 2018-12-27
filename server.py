# -*- coding: utf-8 -*-
# author:           inspurer(月小水长)
# pc_type           lenovo
# create_date:      2018/12/15
# file_name:        server.py
# description:      月小水长，热血未凉

from socket import *
from threading import Thread
import time
import json

serverIp = "10.10.21.222"
serverPort = 6789
connectionSocketList = []
def updateConnectionList():
    global connectionSocketList
    connectionSocketIPList = []
    for item in connectionSocketList:
        ip, port = item.getpeername()
        connectionSocketIPList.append(ip)
        print(ip)
    return {
        "type": "2",
        "content": connectionSocketIPList
    }

# 规定消息格式为json,dict格式 {"type":"1","sourceIP":"127.0.0.1","destinationIP":"127.0.0.1","content":"hello"}
def socketHander(connectionSocket):
    global connectionSocketList
    connectionSocketList.append(connectionSocket)
    connectionSocket.settimeout(2)
    for socket in connectionSocketList:
        socket.send(json.dumps(updateConnectionList()).encode("utf-8"))
    while True:
        try:
            # 接收消息
            receivedMessage = connectionSocket.recv(1024)
            if not receivedMessage:
                time.sleep(1)
                continue
            receivedMessage = receivedMessage.decode("utf-8")
            receivedMessage = json.loads(receivedMessage)
            print(receivedMessage)

            type = receivedMessage.get("type")

            # 服务器转发单人聊天消息
            if type == "1":
                dip = receivedMessage.get("destinationIP")
                for socket in connectionSocketList:
                    sip,sport = socket.getpeername()
                    print("sip",sip)
                    if sip == dip:
                        message = {
                            "type": "1",
                            "sourceIP": receivedMessage.get("sourceIP"),
                            "content": receivedMessage.get("content")
                        }
                        socket.send(json.dumps(message).encode("utf-8"))

            # 服务器转发群消息
            elif type == "2":
                # 遍历groupList
                message = {
                    "type": "1",
                    "sourceIP": receivedMessage.get("sourceIP"),
                    "content": receivedMessage.get("content")
                }
                for socket in connectionSocketList:
                    socket.send(json.dumps(message).encode("utf-8"))



            # 客户端想要断开连接
            elif type == "3":
                connectionSocketList.remove(connectionSocket)
                #通知所有人xxx已下线
                for socket in connectionSocketList:
                    socket.send(json.dumps(updateConnectionList()).encode("utf-8"))

            elif type == "4":
                dip = receivedMessage.get("destinationIP")
                for socket in connectionSocketList:
                    sip, sport = socket.getpeername()
                    print("sip", sip)
                    if sip == dip:
                        message = {
                            "type": "3",
                            "sourceIP": receivedMessage.get("sourceIP"),
                            "filename": receivedMessage.get("filename"),
                            "content": receivedMessage.get("content")
                        }
                        socket.send(json.dumps(message).encode("utf-8"))

            elif type == "5":
                message = {
                    "type": "3",
                    "sourceIP": receivedMessage.get("sourceIP"),
                    "filename": receivedMessage.get("filename"),
                    "content": receivedMessage.get("content")
                }
                for socket in connectionSocketList:
                    socket.send(json.dumps(message).encode("utf-8"))



        except:
            pass


if __name__ == "__main__":
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind((serverIp,serverPort))
    serverSocket.listen(100)
    while True:
        connectionSocket,addr = serverSocket.accept()
        print(connectionSocket.getpeername()) #('127.0.0.1', 1958)
        Thread(target=socketHander,args=(connectionSocket,)).start()