# -*- coding: utf-8 -*-
# author:           inspurer(月小水长)
# pc_type           lenovo
# create_date:      2018/12/15
# file_name:        client.py
# description:      月小水长，热血未凉

from socket import *
from threading import Thread
import wx
import json
import wx.lib.agw.customtreectrl as CT

serverPort = 6789
serverIp = "10.10.21.222"

class QICQ(wx.Frame):

    def __init__(self):
        global serverIp,serverPort

        wx.Frame.__init__(self,parent=None,title="SocketQICQ",size=(600,400))

        panel=wx.Panel(self)

        panel.SetBackgroundColour((0, 153, 255))

        #python3.5.1 style的设置对wx.TreeCtrl()不起作用，改用ET
        self.userListTree = CT.CustomTreeCtrl(parent=panel,pos=(10,10),size=(280,300),
                                          style=wx.TR_FULL_ROW_HIGHLIGHT)
        self.rootID = self.userListTree.AddRoot("已登录用户")
        self.userListTree.SetBackgroundColour((224,255,255))

        self.userListTree.AppendItem(self.rootID,"第一个子节点")
        self.userListTree.AppendItem(self.rootID,"第二个子节点")
        self.userListTree.ExpandAll()

        self.userList = []

        self.info = wx.Button(parent=panel,pos=(100,315),size=(80,40),label="说明")
        self.info.SetBackgroundColour((224,255,255))

        inputTip = wx.TextCtrl(parent=panel,pos=(300,10),size=(130,20),value="请输入你要发送的信息",
                               style=wx.TE_READONLY)
        inputTip.SetForegroundColour((0,153,255))
        inputTip.SetBackgroundColour((224,255,255))
        self.input = wx.TextCtrl(parent=panel,pos=(300,30),size=(275,50))
        self.input.SetForegroundColour((0,153,255))
        self.input.SetBackgroundColour((224,255,255))

        self.send = wx.Button(parent=panel,pos=(300,100),size=(275,50),label="发送")
        self.send.SetBackgroundColour((224,255,255))

        separation = wx.TextCtrl(parent=panel,pos=(290,170),size=(300,2))
        separation.SetBackgroundColour((224, 255, 255))

        receivedTip = wx.TextCtrl(parent=panel,pos=(300,190),size=(135,20),value="发送/接收到的消息列表",
                               style=wx.TE_READONLY)
        receivedTip.SetForegroundColour((0,153,255))
        receivedTip.SetBackgroundColour((224,255,255))
        self.messageList = wx.TextCtrl(parent=panel,size=(275,120),pos=(300,210),
                   style=(wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY))

        self.messageList.SetBackgroundColour((224, 255, 255))
        #前景色，也就是字体颜色
        self.messageList.SetForegroundColour((0, 153, 255))

        self.sendMessage = ""

        childThraed = Thread(target=self.socketHander)
        childThraed.setDaemon(True)
        childThraed.start()

        self.Bind(wx.EVT_BUTTON,self.OnInfoClicked,self.info)
        self.Bind(wx.EVT_BUTTON,self.OnSendClicked,self.send)

    def OnInfoClicked(self,event):
        wx.MessageDialog(self, u'''\r\n\r\n\r\n\t\t1、互联的环境必须是在同一个局域网\r\n
        2、必须先在左边选择发送对象且发送消息不为空才能发送消息\r\n
        3、选择根目录{已登录用户}是群发消息，选择单个是私发消息\r\n
        4、刚登录时最后一个ip是你自己的ip\r\n''', u"警告", wx.OK).ShowModal()

    def OnSendClicked(self,event):
        self.sendMessage = self.input.Value
        #print(self.sendMessage)
        if len(self.sendMessage) == 0:
            wx.MessageDialog(self, u"请先输入待发送的消息", u"警告", wx.OK).ShowModal()
            return None
        selected = self.userListTree.GetSelection()
        selected = self.userListTree.GetItemText(selected)
        #print(selected)
        if not selected:
            wx.MessageDialog(self, u"请先选择用户或组", u"警告", wx.OK).ShowModal()
            return None

        #表示选择的是根节点，需要转发群消息
        if selected == "已登录用户":
            self.sendMessage = {
                "type":"2",
                "sourceIP":self.ip,
                "destinationIP":selected,
                "content":self.sendMessage
            }

        else:
            self.sendMessage = {
                "type":"1",
                "sourceIP":self.ip,
                "destinationIP":selected,
                "content":self.sendMessage
            }


    def socketHander(self):
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((serverIp, serverPort))
        self.clientSocket.settimeout(2)
        self.ip,self.port = self.clientSocket.getsockname()
        print("self ip",self.ip)
        while True:
            #发送消息
            if len(self.sendMessage) == 0:
                pass

            else:
                self.clientSocket.send(json.dumps(self.sendMessage).encode("utf-8"))
                self.messageList.AppendText("消息["+self.sendMessage.get("content")+"]发送成功\r\n")
                self.input.SetLabelText("")
                print("发送成功")
                self.sendMessage = ""

            try:
                # 接收消息
                receivedMessage = self.clientSocket.recv(1024)
                receivedMessage = receivedMessage.decode("utf-8")
                receivedMessage = json.loads(receivedMessage)
                print(receivedMessage)
                type = receivedMessage.get("type")

                # 客户端接收服务端发来的转发消息
                if type == "1":
                    print("客户端收到消息")
                    sourceIp = receivedMessage.get("sourceIP")
                    content = receivedMessage.get("content")
                    if sourceIp == self.ip:
                        pass
                    else:
                        self.messageList.AppendText("来自:["+sourceIp+"]的消息:["+content+"]\r\n")

                elif type == "2":
                    # 客户端接收服务端发来的刷新列表请求
                    self.userList = receivedMessage.get("content")
                    self.setUserList()
            except:
                print("等待数据...")
                pass
        pass

    def setUserList(self):
        self.userListTree.DeleteChildren(self.rootID)
        for user in self.userList:
            # if user == self.ip:
            #     continue
            self.userListTree.AppendItem(self.rootID,user)
        pass

    def OnClosed(self,event):
        endMessage ={
            "type":"3",
            "content":"bye"
        }
        self.clientSocket.send(json.dumps(endMessage).encode("utf-8"))
        self.Destroy()


if __name__ == '__main__':
    global serverIp
    serverIp = input("请输入服务器ip")
    app = wx.App()
    frame = QICQ()
    frame.Bind(wx.EVT_CLOSE,frame.OnClosed)
    frame.Show()
    app.MainLoop()
    app.OnExit()