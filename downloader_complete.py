# -*- coding: utf-8 -*-
# 导入程序运行必须模块
import sys
import json
import time

import DownloadPerformance
import pandas as pd
import os
import requests
import numpy as np
# PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中
from PyQt5.QtWidgets import QApplication, QMainWindow
# 导入designer工具生成的login模块
from downloader_new_new import Ui_Form
import otosense_download_raw_gui
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
import error_judge


def get_token(url, id, secret):
    base_url = url
    client_id = id
    client_secret = secret
    data = {'grant_type': 'client_credentials'}
    access_token_response = requests.post(base_url + 'oauth/token', data=data, verify=True, allow_redirects=False,
                                          auth=(client_id, client_secret))
    tokens = json.loads(access_token_response.text)
    print("token", tokens['access_token'])
    # get motor ID
    api_call_headers = {'Authorization': 'Bearer ' + tokens['access_token'], 'Accept-Encoding': 'gzip, deflate, br'}
    api_call_response = requests.get(base_url + 'motors', headers=api_call_headers, verify=True)
    # motor_list = json.loads(api_call_response.text)
    # motor_id = motor_list["motors"][3]["motorId"]
    # print("motor_id",motor_id)
    return tokens['access_token']


def list_to_csv(vibx, vibz, flux, tempe, tempm, csv_name, vibx_en, vibz_en, flux_en, tempe_en, tempm_en, file_path,
                vibxFFT, vibzFFT, fluxFFT, vibxFFT_en, vibzFFT_en, fluxFFT_en):
    # if os.path.exists(file_path+"\\"+csv_name):
    #     print("file already exists")
    # else:
    df = pd.DataFrame()
    if (vibx_en):
        df["vibx"] = pd.Series(vibx)
    if (vibz_en):
        df["vibz"] = pd.Series(vibz)
    if (flux_en):
        df["flux"] = pd.Series(flux)
    if (tempe_en):
        df["tempe"] = pd.Series(tempe)
    if (tempm_en):
        df["tempm"] = pd.Series(tempm)
    if (vibxFFT_en):
        df["vibxFFT"] = pd.Series(vibxFFT)
    if (vibzFFT_en):
        df["vibzFFT"] = pd.Series(vibzFFT)
    if (fluxFFT_en):
        df["fluxFFT"] = pd.Series(fluxFFT)
    df.to_csv(file_path + "\\" + csv_name, index=None)


def json_to_list(file_path, vibx_en, vibz_en, flux_en, tempe_en, tempm_en, path_folder, vibxFFT_en, vibzFFT_en,
                 fluxFFT_en):
    json_file_list = os.listdir(file_path)
    json_file_list = [i for i in json_file_list if i[-1] == 'n']
    csv_file = [m[:-5] + ".csv" for m in json_file_list]
    vibx = 0
    vibz = 0
    flux = 0
    tempe = 0
    tempm = 0
    vibxFFT = 0
    vibzFFT = 0
    fluxFFT = 0
    for i in range(len(json_file_list)):
        with open(file_path + "\\" + json_file_list[i]) as json_data:
            data = json.load(json_data)
            if vibx_en:
                vibx = data['vibx']
            if vibz_en:
                vibz = data['vibz']
            if flux_en:
                flux = data['flux']
            if tempe_en:
                tempe = data['tempe']
            if tempm_en:
                tempm = data['tempm']
            if vibxFFT_en:
                vibxFFT = data['vibxFFT']
            if vibzFFT_en:
                vibzFFT = data['vibzFFT']
            if fluxFFT_en:
                fluxFFT = data['fluxFFT']

        try:
            list_to_csv(vibx, vibz, flux, tempe, tempm, csv_file[i], vibx_en, vibz_en, flux_en, tempe_en, tempm_en,
                        path_folder, vibxFFT, vibzFFT, fluxFFT, vibxFFT_en, vibzFFT_en, fluxFFT_en)
        except:
            print("csv not created")


def delete_json(file_path):
    json_file_list = os.listdir(file_path)
    for i in json_file_list:
        if i[-4:] == "json":
            os.remove(file_path + "\\" + i)


def check_blank(userID, userpassword, motor_ID, start_date, end_date, path_folder, URL, vibx_en, vibz_en, flux_en,
                tempe_en, tempm_en,
                vibxfft_en, vibzfft_en, fluxfft_en, condition_en, performance_en, operations_en):
    if (userID == "" or userpassword == "" or motor_ID == "" or start_date == ""
            or end_date == "" or path_folder == "" or URL == ""):
        return 1
    if (len(start_date) != 8 or len(end_date) != 8):
        return 2
    if (int(start_date) > int(end_date)):
        return 3
    if not os.path.exists(path_folder):
        return 4
    if (URL[-1] != '/'):
        return 5
    if vibx_en == 0 and vibz_en == 0 and flux_en == 0 and tempe_en == 0 and tempm_en == 0 \
            and vibxfft_en == 0 and vibzfft_en == 0 and fluxfft_en == 0 and condition_en == 0 and performance_en == 0 \
            and operations_en == 0:
        return 7
    return 6


class MyMainForm(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        # 添加登录按钮信号和槽。注意display函数不加小括号()
        self.Run.clicked.connect(self.display)
        # 添加退出按钮信号和槽。调用close函数
        self.Run_2.clicked.connect(self.close)
        self.toolButton.clicked.connect(self.choose)
        self.load_parameter.clicked.connect(self.para_click)

    def display(self):

        self.thread = RunThread()
        self.thread.start()

    def para_click(self):
        para = self.load_para()
        if para[0] != 1:
            self.URL_line.setText(para[0])
            self.AST_line.setText(para[1])
            self.ID_line.setText(para[2])
            self.PIN_line.setText(para[3])
            self.Path_line.setText(para[4])

    def choose(self):
        openfile_name = QFileDialog.getExistingDirectory(None, 'choose file', 'C:/')
        self.Path_line.setText(openfile_name)

    def load_para(self):
        desktop_dir = os.path.expanduser('~/Desktop')
        if os.path.exists(desktop_dir + '\parameter.csv'):
            array = np.loadtxt(desktop_dir + '\parameter.csv', dtype=str, delimiter=',')
            return array
        else:
            self.textBrowser.setText("Parameter can not be loaded")
            self.textBrowser.repaint()
            return [1]


class RunThread(QThread, MyMainForm):
    trigger = pyqtSignal()

    def __init__(self):
        super(RunThread, self).__init__(None)

    def __del__(self):
        self.wait()

    def save_parameter(self):
        userID = self.ID_line.text()
        userpassword = self.PIN_line.text()
        motor_ID = self.AST_line.text()
        path_folder = self.Path_line.text()
        URL = self.URL_line.text()
        array = np.array([URL, motor_ID, userID, userpassword, path_folder])
        desktop_dir = os.path.expanduser('~/Desktop')
        np.savetxt(desktop_dir + '\parameter.csv', array, delimiter=',', fmt='%s')

    def error_handle(self, num):
        if num == 1:
            self.textBrowser.setText("Please fill all the item")
            self.textBrowser.repaint()
            self.Run.setChecked(False)
        if num == 2:
            self.textBrowser.setText("The format of date should be YYYYMMDD")
            self.textBrowser.repaint()
            self.Run.setChecked(False)
        if num == 3:
            self.textBrowser.setText("The start date is greater than end date")
            self.textBrowser.repaint()
            self.Run.setChecked(False)
        if num == 4:
            self.textBrowser.setText("The folder path does not exist")
            self.textBrowser.repaint()
            self.Run.setChecked(False)
        if num == 5:
            self.textBrowser.setText("Please check the URL item")
            self.textBrowser.repaint()
            self.Run.setChecked(False)
        if num == 7:
            self.textBrowser.setText("None of the output parameter is selected")
            self.textBrowser.repaint()
            self.Run.setChecked(False)

    def run(self):
        userID = self.ID_line.text()
        userpassword = self.PIN_line.text()
        motor_ID = self.AST_line.text()
        path_folder = self.Path_line.text()
        URL = self.URL_line.text()

        vibx_en = self.vibx.checkState()
        vibz_en = self.vibz.checkState()
        flux_en = self.flux.checkState()
        tempe_en = self.tempe.checkState()
        tempm_en = self.tempm.checkState()
        vibxfft_en = self.vibxFFT.checkState()
        vibzfft_en = self.vibzFFT.checkState()
        fluxfft_en = self.flux_FFT.checkState()
        condition_en = self.conditions.checkState()
        performance_en = self.performance.checkState()
        operations_en = self.operations.checkState()

        start = self.start_date_time.date()
        start_date = start.toString("yyyyMMdd")
        start_time = self.start_date_time.dateTime()
        start_time = start_time.toString("HH:mm")
        end = self.end_date_time.date()
        end_date = end.toString("yyyyMMdd")
        end_time = self.end_date_time.dateTime()
        end_time = end_time.toString("HH:mm")

        check = check_blank(self.userID, userpassword, motor_ID, start_date, end_date, path_folder, URL, vibx_en,
                            vibz_en,
                            flux_en, tempe_en, tempm_en,
                            vibxfft_en, vibzfft_en, fluxfft_en, condition_en, performance_en, operations_en)
        self.error_handle(check)
        token = 0
        result = 1
        perform_result = 1
        response = '1'
        # self.textBrowser.setText("Data Processing...")
        self.Run.setChecked(False)  # 重置按钮状态

        if check == 6:
            try:
                self.textBrowser.clear()
                self.textBrowser.repaint()  # 要repaint才会立刻执行
                token = get_token(URL, userID, userpassword)
            except:
                self.textBrowser.setText("ID or Pass is wrong")
                self.Run.setChecked(False)  # 重置按钮状态
            if token:
                URL_data = URL + "data/"
                try:
                    if (
                            vibx_en or vibz_en or vibxfft_en or vibzfft_en or flux_en or fluxfft_en or tempm_en or tempe_en):

                        result = otosense_download_raw_gui.data_download(ast_Code=token, service_end_point=URL_data,
                                                                         start=start_date,
                                                                         end=end_date, fold_path=path_folder,
                                                                         ID=motor_ID, name="raw",
                                                                         start_hour=start_time[:2],
                                                                         start_minute=start_time[3:],
                                                                         end_hour=end_time[:2], end_minute=end_time[3:],
                                                                         vibx=vibx_en, vibz=vibz_en,
                                                                         flux=flux_en, tempe=tempe_en, tempm=tempm_en,
                                                                         vibxFFT=vibxfft_en,
                                                                         vibzFFT=vibzfft_en, fluxFFT=fluxfft_en)

                    else:
                        result = 1
                        # print("result",result)

                except:
                    self.textBrowser.setText("motor_ID or URL item is wrong")
                    self.textBrowser.repaint()
                    self.Run.setChecked(False)  # 重置按钮状态

                if result:
                    self.save_parameter()
                    time.sleep(15)
                    if (
                            vibx_en or vibz_en or vibxfft_en or vibzfft_en or flux_en or fluxfft_en or tempm_en or tempe_en):
                        json_to_list(path_folder, vibx_en, vibz_en, flux_en, tempe_en, tempm_en, path_folder,
                                     vibxfft_en, vibzfft_en, fluxfft_en)

                    try:
                        if (condition_en or performance_en or operations_en):
                            perform_result = DownloadPerformance.performance_download(ast_Code=token,
                                                                                      service_end_point=URL_data,
                                                                                      start=start_date,
                                                                                      end=end_date,
                                                                                      fold_path=path_folder,
                                                                                      ID=motor_ID, name="performance",
                                                                                      condition_en=condition_en,
                                                                                      performance_en=performance_en,
                                                                                      operation_en=operations_en)
                    except:
                        print("no performance data")

                    print("request　count", error_judge.request_count)
                    print("*" * 100)
                    delete_json(path_folder)
                    if perform_result:
                        if error_judge.error_judgement == 900:
                            self.textBrowser.setText("To Many Requests, Error Response 429")
                            self.textBrowser.repaint()
                            self.Run.setChecked(False)
                        else:
                            self.textBrowser.setText("data generated")
                            self.textBrowser.repaint()
                            self.Run.setChecked(False)

                    else:
                        if error_judge.error_judgement == 100:
                            self.textBrowser.setText("no performance data in this time range")
                            self.textBrowser.repaint()
                            self.Run.setChecked(False)
                        if error_judge.error_judgement == 900:
                            self.textBrowser.setText("To Many Requests, Error Response 429")
                            self.textBrowser.repaint()
                            self.Run.setChecked(False)
                else:
                    if error_judge.error_judgement == 900:
                        self.textBrowser.setText("To Many Requests, Error Response 429")
                        self.textBrowser.repaint()
                        self.Run.setChecked(False)  # 重置按钮状态

                    if error_judge.error_judgement == 100:
                        self.textBrowser.setText("NO DATA in this time range")
                        self.textBrowser.repaint()
                        self.Run.setChecked(False)  # 重置按钮状态
                    else:
                        self.textBrowser.setText("To Many Requests, Error Response 429")
                        self.textBrowser.repaint()
                        self.Run.setChecked(False)  # 重置按钮状态


if __name__ == "__main__":
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化
    myWin = MyMainForm()
    # 将窗口控件显示在屏幕上
    myWin.show()
    # 程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
