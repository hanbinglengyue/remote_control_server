# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from PyQt5 import QtWidgets,QtCore,QtGui
import sys
import socket
import os
import threading
import time
import configparser
import uuid
from Server_ui import Ui_Dialog
import subprocess
from subprocess import Popen,PIPE

Icon_count = 0
first_connect = 0
Mac_addr = 0
class mywindow(QtWidgets.QDialog):
    _signal=QtCore.pyqtSignal(str)                    #定义信号
    def __init__(self):
        super(mywindow, self).__init__()
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.new = Ui_Dialog()

        self.setFixedSize(400,300)

        self.new.setupUi(self)

        self._signal.connect(self.L_Data_show)         #信号连接到函数
        self.config_get()

        # 托盘显示
        self.trayIcon = QtWidgets.QSystemTrayIcon(self)
        self.icon = QtGui.QIcon('icon.png')
        self.trayIcon.setIcon(self.icon)
        self.trayIcon.show()
        self.trayIcon.activated.connect(self.trayIcon_click)

    def closeEvent(self, event):                        # 重写关闭按钮操作
        self.hide()
        event.ignore()

    def trayIcon_click(self, reason):                   #  最小化托盘操作
        global Icon_count
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.showNormal()
        else:
            self.hide()

    def config_get(self):
        global Mac_addr
        config = configparser.ConfigParser()
        config.read("win_config.ini")

        ip = config.get("baseconf","Ip")
        port = config.get("baseconf","Port")
        mac = config.get("baseconf","Mac")

        #localIp = socket.gethostbyname(socket.gethostname())
        #if(ip != localIp ):
        #    config.set("baseconf","Ip",localIp)
        #    fh = open("win_config.ini",'w')
        #    config.write(fh)
        #    fh.close()
        #else:
        #    pass

        node = uuid.getnode()
        mac = uuid.UUID(int = node).hex[-12:].upper()
        true_mac = "-".join([mac[e:e+2] for e in range(0,11,2)])

        if(mac != true_mac):
            config.set("baseconf","Mac",true_mac)
            fh = open("win_config.ini",'w')
            config.write(fh)
            fh.close()
        else:
            pass

        mac = config.get("baseconf","Mac")
        string = "本机地址："+ip+" "+"TCP端口："+port
        self._signal.emit(string)
        mac_string = "MAC:"+ mac
        Mac_addr = mac
        self._signal.emit(mac_string)

        self.Server_open(ip,port)

    def Server_open(self,ip,port): 
        port = int(port)
        t = threading.Thread(target=self.tcplink, args=(ip, port))
        t.start()

    def tcplink(self, Host, Port):
        bind_Host = "0.0.0.0"
        Add = (bind_Host, Port)
        try:
            sersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sersock.bind(Add)
            sersock.listen(5)
        except OSError as e:
            bind_error = "绑定异常"  + str(e.errno)
            self._signal.emit(bind_error)

            string = 'netstat -aon|findstr '+ str(Port) 
            output = os.popen(string).read()
            out_put = output.split()
            pid = out_put[4]
            kill_pid = 'taskkill /f /pid '+ str(pid)
            os.system(kill_pid)
            sersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sersock.bind(Add)
            sersock.listen(5)

        self._signal.emit("等待连接。。。。。。") 
        while True:
            try:
                self.connection, client_address = sersock.accept()
                string = "已连接：" + str(self.connection.getpeername())
                self._signal.emit(string)
            
                s = threading.Thread(target=self.thread_receive, args=())
                s.start()
            except OSError as e:
                recv_error = "Socket 收发失败：" + e.errno
                self._signal.emit(recv_error)
                self.connection.close()

    def thread_receive(self):
        while True:
            try:
                get_data = self.connection.recv(128).decode()
                if get_data == '':
                    self.connection.close()
                    self._signal.emit("连接断开")
                    self._signal.emit("等待连接。。。。。。")
                    break
                else:
                    self.cmd_parse(get_data)
            except OSError as e:
                dis_error = "连接异常断开：" + e.errno
                self._signal.emit(dis_error)
                self._signal.emit("等待连接。。。。。。")
                break

    def senddata(self, string):
        try:
            self.connection.send(string.encode())
            string = "发送：" + string 
            self._signal.emit(string)
        except OSError as e:
            send_error = "发送：" + string + "失败：" + e.errno
            self._signal.emit(send_error)


    def cmd_parse(self, string):                      # parse the receive data from client
        global Mac_addr
        output = "接收：" + string
        self._signal.emit(output)
        # if string == 'login':
        #     self.senddata("login OK")
        # if string == 'TCPcheck':
        #     self.senddata("OK")
        if string == 'getmac':
            self.senddata(Mac_addr)
            self._signal.emit("发送mac地址")
        if string == 'exit':
            self.senddata("start exit")
            self._signal.emit("接收：exit")

            os.system('shutdown -s -t 2')         #shut down windows

        if string == 'noexit':
            self.senddata("cancel exit")
            os.system('shutdown -a')               #cancel shut down windows
        else:
            pass

    def L_Data_show(self, str):                     # log show
        time_str = time.strftime('%H:%M:%S', time.localtime(time.time()))
        str=time_str+' '+str
        self.new.L_Date.append(str)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myshow = mywindow()
    #myshow.showMinimized()     # 最小化窗口，会有状态栏
    myshow.hide()          # 隐藏窗口，且不会有状态栏
    os._exit(app.exec_())
