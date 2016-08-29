#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QMessageBox,QPushButton
from Lark_ui import Ui_Dialog
import sys
import socket
import configparser
import threading
import os
import time
import struct
import subprocess
import signal
import random
import logging

tcp_count = 0                     # for 开机 TCP 连接次数判断
wol_count = 0                     # 远程唤醒判断
mac_count = 0                     # check mac 地址
keep_count = 0                    # tcp keep alive
tcp_connected = 0                 # tcp connect or not 
windows_status = 0                # windows status
windows_power_off = 0             # check windows after 关机 成功计数
windows_power_fail = 0            # check windows after fail
kw_judge = 0                         # 解决关机TCP 与keepalive检测冲突问题
num = 0


_logger = logging.getLogger()
_logger.addHandler(logging.FileHandler("log", mode='w'))
_logger.setLevel(logging.NOTSET)


class Larkclient(QtWidgets.QDialog):
    _signal = QtCore.pyqtSignal(str)                               # 定义信号  for log show
    def __init__(self):
        super(Larkclient, self).__init__()
        self.setFixedSize(382, 299)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint & QtCore.Qt.WindowMinimizeButtonHint)
        self.new = Ui_Dialog()
        self.new.setupUi(self)
        self.new.C_Bt.clicked.connect(self.C_Bt_clicked)       # Connect Button action
        self.new.R_Bt.clicked.connect(self.R_Bt_clicked)       # Rmote Control action
        self.new.W_Bt.clicked.connect(self.W_Bt_clicked)       # Windows Control Button action
        self._signal.connect(self.Log_show)                    # 信号连接到函数
        self.config_get()
        self.new.R_Bt.setEnabled(False)
        self.new.W_Bt.setEnabled(False)
        self.re_ctrl = None
        #self.stressing_test()

# 读取config文件
    def config_get(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.ip = config.get("baseconf","Ip")
        self.port = config.get("baseconf","Port")
        self.mac = config.get("baseconf","Mac")
        self.file_name = config.get("baseconf","file_name")
        self.pc_name = config.get("baseconf","pc_name")
        self.pc_sec = config.get("baseconf","pc_sec")

# 压力测试方法
    def stressing_test(self):
        global num
        global error
        if True:
            choice_action = random.choice(['Connect','Remote','Windown'])
            test_count = "    " + str(num) + ": " + choice_action
            self._signal.emit(test_count)
            if choice_action == 'Connect':
                if self.new.C_Bt.isEnabled():
                    self.C_Bt_clicked()
                    self._signal.emit('connect usefull')
                else:
                    self._signal.emit('connect no use')
            if choice_action == 'Remote':
                if self.new.R_Bt.isEnabled():
                    self._signal.emit('remote usefull')
                    self.R_Bt_clicked()
                else:
                    self._signal.emit('remote no use')
            if choice_action == 'Windown':
                if self.new.W_Bt.isEnabled():
                    Yes_no_choice = random.choice(['Yes','No'])
                    if Yes_no_choice == 'Yes':
                        self.W_Bt_Yes()
                       #only for test mac
                        Mac_change_choice = random.choice(['Yes','No'])
                        if Mac_change_choice == 'Yes':
                            self._signal.emit('WWWWWWWWWWWWWWWWWW')
                            self.mac = 'wrong mac addr' 
                            config = configparser.ConfigParser()
                            config.read("config.ini")
                            config.set("baseconf","Mac",self.mac)
                            fh = open("config.ini",'w')
                            config.write(fh)
                            fh.close()
                        else:
                           self._signal.emit('RRRRRRRRRRRRRRRRRRRRRRRRRRRR')
                        # test for mac end
 
                    else:
                        self.W_Bt_No()
                    string = "    " + Yes_no_choice + 'windows poweroff usefull'
                    self._signal.emit(string)
                else:
                    self._signal.emit('windows poweroff no use')
            num = num + 1
        s_t_timer = threading.Timer(5,self.stressing_test)
        s_t_timer.start()


# 开机按钮操作
    def C_Bt_clicked(self):  # Connect Button push
        self._signal.emit("按下 “开机” 键")
        self.new.C_Bt.setStyleSheet("background-color: yellow;")
        self.new.C_Bt.setEnabled(False)
        self.C_Bt_for_connect()

    def C_Bt_for_connect(self):
        global tcp_count
        global wol_count
        if tcp_count < 3:
            string = "第"+str(tcp_count+1) + "次" + "连接远程 windows " +"("+self.ip + ":"+ self.port +")"
            self._signal.emit(string)

            if self.tcp_connect():                   #connect tcp success
                self._signal.emit("连接成功")
                tcp_count = 0
                C_bt_succ = threading.Timer(1,self.C_bt_tcpconnect_success)
                C_bt_succ.start()
            else:
                tcp_count = tcp_count + 1
                self._signal.emit("连接失败")
                C_bt_fail = threading.Timer(2,self.C_Bt_for_connect)
                C_bt_fail.start()
        else:
            if wol_count == 0:
                self._signal.emit("连接 windows 失败，开启远程唤醒")
                self.new.C_Bt.setStyleSheet("background-color: red;")
                self.new.W_Bt.setEnabled(False)

                self.wol = threading.Thread(target=self.wake_on_lan, args=())      # threading to open socket
                self.wol.start()
                wol_count = 1
                tcp_count = 0
            else:
                pass

    def wol_check_tcpconnect(self):
        global tcp_count
        global wol_count
        if tcp_count == 0:
            string = "远程唤醒，windows 状态确认中。。。。。。"
            self._signal.emit(string)
        else:
            pass
        if tcp_count <20:
            if self.tcp_connect():
                wol_tcp_succ = threading.Timer(1,self.C_bt_tcpconnect_success)
                wol_tcp_succ.start()
                wol_count = 0
                tcp_count  = 0
            else:
                tcp_count = tcp_count + 1
                wol_tcp_fail = threading.Timer(5,self.wol_check_tcpconnect)
                wol_tcp_fail.start()
        else:
            self._signal.emit("远程唤醒 windows 失败，请检查网络或尝试手动开启 windows")
            self.new.C_Bt.setStyleSheet("{background-color: rgba(0, 125, 0, 0);}")
            self.new.C_Bt.setEnabled(True)
            wol_count = 0
            tcp_count  = 0

    def C_bt_tcpconnect_success(self):
        self.tcp_disconnect()
        self._signal.emit("可以远程控制 Windows") 
        self.new.C_Bt.setStyleSheet("background-color: green;")
        self.new.C_Bt.setEnabled(False)
        self.new.R_Bt.setEnabled(True)
        self.new.W_Bt.setEnabled(True)

        open_keepalive = threading.Timer(1, self.keeepalive_tcpconnect)               # 开启连接状态检测
        open_keepalive.start()

    def wake_on_lan(self):
        macaddress = self.mac
        string = "远程 windows 物理地址:" + macaddress
        self._signal.emit(string)
        if len(macaddress) == 12:
            pass
        elif len(macaddress) == 12 + 5:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, '')
        else:
            self._signal.emit("物理地址错误 %s",macaddress) 
        print('Mac address:',macaddress)
        data = ''.join(['FFFFFFFFFFFF', macaddress * 16])
        send_data = b'' 
        for i in range(0, len(data), 2):
            byte_dat = struct.pack('B', int(data[i: i + 2], 16))
            send_data = send_data + byte_dat
        #print('magic package: %s',send_data)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except OSError as e:
             self._signal.emit("creat broadcast error")
        try:
            timer2 = threading.Timer(5, self.wol_check_tcpconnect)                # wake up windows checktimer
            timer2.start()
            sock.sendto(send_data, ('192.168.136.255',9))
            sock.close()
        except OSError as e:
            wol_error = "wol_error:" + str(e.errno)
            self._signal.emit(wol_error)
            self._signal.emit("远程唤醒操作失败，请检查配置文件信息，远程电脑的网络电源后重启远程桌面程序")
        #self._signal.emit("唤醒结束")
        

# TCP操作
    def tcp_connect(self):
        port = int(self.port)
        #try:
         #   self.Clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          #  self.Clisock.connect((self.ip, port))
           # return 1
        #except socket.error:
         #   return 0
        self.Clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Clisock.settimeout(2)
        try:
            self.Clisock.connect((self.ip, port))
            self.Clisock.settimeout(None)
            #self._signal.emit("TCP 连接成功")
            return 1
        except socket.error:
            self._signal.emit("TCP 连接失败")
            return 0

    def tcp_disconnect(self):
        if self.Clisock:
            #self._signal.emit("TCP 链接中")
            self.Clisock.close()
        else:
            pass
        #self._signal.emit("TCP 连接断开")

    def get_mac_addr(self, mac_data_string):
        global mac_count
        if len(mac_data_string) == 17:
            mac_count = 2
            if self.mac != mac_data_string:
                self.mac = mac_data_string 
                config = configparser.ConfigParser()
                config.read("config.ini")
                config.set("baseconf","Mac",self.mac)
                fh = open("config.ini",'w')
                config.write(fh)
                fh.close()
                output = "Mac:" + self.mac
                self._signal.emit(output)
                self._signal.emit("Mac地址设置成功")
            else:
                self._signal.emit("Mac地址无需更新")
        else:
            if mac_count < 2:
                self._signal.emit("收到异常Mac地址")
                mac_count = mac_count + 1
                if mac_count == 2:
                    self._signal.emit("更新Mac地址失败，请尝试手动更新或重启软件")
                else:
                    pass
            else:
                pass

    def keeepalive_tcpconnect(self):
        global windows_status
        global keep_count
        global kw_judge
        global mac_count
        if windows_status == 1:                      # Windows 进入关机状态不进行 keep alive 检测 
            kw_judge = 1
            self._signal.emit("远程关闭 Windows 操作中")
        else:
            if self.tcp_connect():
                keep_count = 0
                # add for mac check
                if mac_count < 2:
                    self.Clisock.settimeout(2)
                    try:
                        self.Clisock.send('getmac'.encode())
                        self._signal.emit("发送：getmac")
                        get=self.Clisock.recv(20).decode()
                        self.Clisock.settimeout(None)
                        get_mac = "收到：" + get
                        self._signal.emit(get_mac)
                        self.get_mac_addr(get)
                    except OSError as e:
                        self._signal.emit("获取Mac地址数据失败")
                else:
                    pass
                    
                self.tcp_disconnect()
                self._signal.emit("Windows 状态正常")
                keepalive_succ = threading.Timer(5, self.keeepalive_tcpconnect)  # 如果状态正常  5秒后再次确认
                keepalive_succ.start()
            else:
                keep_count = keep_count + 1
                if keep_count < 3:
                    self._signal.emit("远程 Windows 网络状态异常")
                    keepalive_fail = threading.Timer(5, self.keeepalive_tcpconnect)  # 如果状态异常  5秒后再次确认
                    keepalive_fail.start()
                else:
                    self._signal.emit("Windows 网络断开，请检查网络或点击 “启动远程电脑” 尝试重连")
                    self.new.C_Bt.setStyleSheet("{background-color: rgba(0, 125, 0, 0);}")
                    self.new.C_Bt.setEnabled(True)
                    self.new.R_Bt.setEnabled(False)
                    self.new.W_Bt.setEnabled(False)
                    keep_count = 0
                    self.re_ctrl_kill()

# 远程桌面按钮操作
    def R_Bt_clicked(self):  # Connect Button push
        self._signal.emit("按下远程控制 Windows 按键")
        #re_cmd = "xfreerdp -p "+self.pc_sec +" --plugin rdpdr --data "+self.file_name+" -- -u "+ self.pc_name +" "+ self.ip
        re_cmd = "xfreerdp -f -p " + self.pc_sec +" --plugin rdpdr --data disk:" + self.file_name + " -- -u "+ self.pc_name +" "+self.ip
        self.re_ctrl = subprocess.Popen(re_cmd, shell = True)
       
    def re_ctrl_kill(self):
        if self.re_ctrl== None:
            #self._signal.emit("未进行远程桌面操作")
            pass
        else:
            try:
                os.kill(self.re_ctrl.pid, signal.SIGKILL)
                os.kill(self.re_ctrl.pid + 1, signal.SIGKILL)
                #self._signal.emit("网络异常，远程控制 Windows 终止")
            except OSError as e:
                self._signal.emit("网络异常，远程桌面操作已结束")
                
# 关机按钮操作
    def W_Bt_clicked(self):
        global windows_status
        global kw_judge
        #eply = QMessageBox.information(self,
        #                                "关闭确认",
        #                                "是否关闭远程电脑?",
        #                               QMessageBox.Yes | QMessageBox.No)
        #if reply == QMessageBox.Yes:
        #    self.W_Bt_Yes()
        #else:
        #    self.W_Bt_No()
        
        self.QBox = QMessageBox()
        self.QBox.setWindowTitle("关机确认")
        self.QBox.setText("是否关闭远程电脑？")
        
        self.Yes = QPushButton()
        self.Yes.setText("确定")
        self.No = QPushButton()
        self.No.setText("取消")
        self.Yes.clicked.connect(self.W_Bt_Yes)       
        self.No.clicked.connect(self.W_Bt_No)
        
        self.QBox.addButton(self.Yes,QMessageBox.ActionRole)
        self.QBox.addButton(self.No,QMessageBox.ActionRole)
        self.QBox.exec()
        
        
        
    
    def W_Bt_Yes(self):
        global windows_status
        global kw_judge
        self._signal.emit("确认，关闭远程 Windows")
        if self.tcp_connect():                                            # 建立TCP连接
                self._signal.emit("远程关闭 windows，建立TCP连接成功")
                send_poweroffcmd = threading.Timer(1, self.Windows_off)         
                send_poweroffcmd.start()
                windows_status = 1
        else:
                self._signal.emit("远程关闭 windows，建立TCP连接失败，请检查网络，重试关机或手动关机")
                windows_status = 0
                if kw_judge == 1:
                    self.keeepalive_tcpconnect()
                    kw_judge = 0
                else:
                    pass
                
    def W_Bt_No(self):
        self._signal.emit("取消，关闭远程 Windows")

    def Windows_off(self):  # Shut down windows push
        global windows_status
        global kw_judge
        self.Clisock.settimeout(2)
        try:
            self.Clisock.send('exit'.encode())
            self._signal.emit("发送：exit")
            get=self.Clisock.recv(20).decode()
            self.Clisock.settimeout(None)
        except OSError as e:
            recv_error ="数据收发异常：" + str(e.errno) + "请检查网络，请检查网络，重试关机或手动关机"
            self._signal.emit(recv_error)
            if kw_judge == 1:
                kw_judge = 0
                windows_status = 0
                self.keeepalive_tcpconnect()
            else:
                pass
        if get.find('start exit') == 0:
            self._signal.emit("收到 Windows 关机确认，远程 Windows 关闭中")
            self.tcp_disconnect()
            self.new.C_Bt.setStyleSheet("{background-color: rgba(0, 125, 0, 0);}")
            self.new.C_Bt.setEnabled(False)
            self.new.R_Bt.setEnabled(False)
            self.new.W_Bt.setEnabled(False)
            tcp_reconnect = threading.Timer(10, self.win_close_check)              # tcp re connect timer
            tcp_reconnect.start()
        else:
            self._signal.emit("远程 Windows 关闭 失败")
            windows_status = 0 

    def win_close_check(self):
        global windows_power_off
        global windows_power_fail
        global wol_count
        global windows_status
        global mac_count
        self._signal.emit("Windows 关机确认中。。。。。。。。。。。")
        if self.tcp_connect():                   #connect tcp success
            self._signal.emit("连接成功")
            if windows_power_fail == 2:
                self._signal.emit("远程 Windows 未关闭, 请检查网络，重试关机或手动关机")
                windows_power_off = 0
                windows_power_fail = 0
                windows_status = 0
                mac_count = 0
                self.new.W_Bt.setEnabled(True)
            else:
                windows_power_fail = windows_power_fail + 1
                windows_power_off = 0
                self._signal.emit("TCP 仍然可连接，远程 Windows 未关闭")
                self.tcp_disconnect()
                tcp_reconnect = threading.Timer(5, self.win_close_check)
                tcp_reconnect.start()
        else:
            self._signal.emit("连接失败")
            if windows_power_off == 2:
                windows_power_off = 0
                windows_power_fail = 0
                windows_status = 0
                mac_count = 0
                self.new.C_Bt.setStyleSheet("{background-color: rgba(0, 125, 0, 0);}")
                self.new.C_Bt.setEnabled(True)
                self.new.R_Bt.setEnabled(False)
                self.new.W_Bt.setEnabled(False)
                string = "远程 Windows 关闭成功"
                self._signal.emit("远程 Windows 关闭成功")
            else:
                windows_power_off = windows_power_off + 1
                string = "远程关闭 Windows 第" + str(windows_power_off)+"次 TCP 连接未成功"  
                self._signal.emit(string)
                tcp_reconnect = threading.Timer(2, self.win_close_check)
                tcp_reconnect.start()

# 状态窗口显示
    def Log_show(self,str):                             # show the log in Qtext
        time_str = time.strftime('%H:%M:%S', time.localtime(time.time()))
        str = time_str + ' '+str
        _logger.info(str)
        self.new.textEdit.append(str)

if __name__=="__main__":
    # app = QtWidgets.QApplication(sys.argv)
    # mywindow = Larkclient()
    # mywindow.exec_() 
    app = QtWidgets.QApplication(sys.argv)
    import singleton
    myshow = Larkclient()
    myshow.show()
    os._exit(app.exec_())
