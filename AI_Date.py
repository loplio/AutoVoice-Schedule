from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk, Image
import requests
import json
import speech_recognition as sr
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QCalendarWidget
from PyQt5.QtCore import QDate, Qt
import re
import datetime as dt

url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
REST_API_KEY = "34c37e7d8540ec5f7697a00c28d78ab9"
header = {
    "Content-Type": "application/octet-stream",
    "Authorization": "KakaoAK " + f"{REST_API_KEY}"
}


def ShowCalendar(info):
    app = QApplication(sys.argv)
    ex = MyApp(info)
    app.exec_()


class TkLoop:
    def __init__(self):
        self.VoiceSupport = AutoVoice()

        self.root = Tk()
        self.root.title("Image Collect")
        self.root.geometry("420x340+1000+100")
        self.root.resizable(False, False)

        self.frame = Frame(self.root)
        self.frame.pack()
        self.Imageframe = Frame(self.root)
        self.Imageframe.pack()
        self.NowImage = Image.new('RGBA', (200, 200), 'white')
        self.tk_image = ImageTk.PhotoImage(self.NowImage)
        self.label = Label(self.root, image=self.tk_image)
        self.label.pack()

        button1 = Button(self.frame, text='달력', command=lambda: ShowCalendar(self.VoiceSupport.RecVoice))
        button1.pack()
        button2 = Button(self.frame, text='음성인식', command=self.VoiceSupport.VoiceRecognition)
        button2.pack()

        self.root.bind('<Escape>', self.stop)
        self.root.bind('q', self.stop)
        self.root.mainloop()

    def stop(self, event=None):
        self.root.destroy()


class AutoVoice:
    def __init__(self):
        self.RecVoice = None

    def VoiceRecognition(self):
        with sr.Microphone(sample_rate=16000) as source:
            print("Say something!")
            r = sr.Recognizer()
            audio = r.listen(source)

        res = requests.post(url, headers=header, data=audio.get_raw_data())
        result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}') + 1]
        result = json.loads(result_json_string)
        self.RecVoice = result['value']

        CalRegexInfo = re.compile(r'^(\d{0,4}년)? *(\d{1,2}월)? *(\d{1,2}일)?')
        if self.RecVoice is not None:
            if bool(CalRegexInfo.search(self.RecVoice).group()):
                ymd = CalRegexInfo.search(self.RecVoice).group().split()
            else:
                ymd = []
                day = dt.datetime.now().day
                print(f'day니? {day}')
            year = dt.datetime.now().year
            month = dt.datetime.now().month
            for n in ymd:
                if '년' in n:
                    year = int(re.compile(r'\d+').search(n).group())
                elif '월' in n:
                    month = int(re.compile(r'\d+').search(n).group())
                elif '일' in n:
                    day = int(re.compile(r'\d+').search(n).group())
        try:
            dt.date(year, month, day)
        except Exception as e:
            print('날짜 설정 오류!', e)
            self.RecVoice = None
        print(result)
        print(result['value'])


class MyApp(QWidget):
    with open('Calendar_File.json', 'r', encoding='utf-8') as f:
        Qinfo = json.load(f)

    def __init__(self, info):
        super().__init__()
        self.BasicInfo = None
        self.DateInfo = None
        self.parsingInfo(info)
        self.initUI()

    @staticmethod
    def parsingInfo(info):
        CalRegexInfo = re.compile(r'^(\d{0,4}년)? *(\d{1,2}월)? *(\d{1,2}일)?')
        if info is not None:
            bufferInfo = {}
            if bool(CalRegexInfo.search(info).group()):
                ymd = CalRegexInfo.search(info).group().split()
            else:
                ymd = []

            for n in ymd:
                if '년' in n:
                    bufferInfo['년'] = int(re.compile(r'\d+').search(n).group())
                elif '월' in n:
                    bufferInfo['월'] = int(re.compile(r'\d+').search(n).group())
                elif '일' in n:
                    bufferInfo['일'] = int(re.compile(r'\d+').search(n).group())

            if '일' in bufferInfo:
                ContentCount = info.find('일')
            elif '월' in bufferInfo:
                ContentCount = info.find('월')
            elif '년' in bufferInfo:
                ContentCount = info.find('년')
            else:
                ContentCount = -1

            if '일' not in bufferInfo:
                bufferInfo['일'] = dt.datetime.now().day
            if '월' not in bufferInfo:
                bufferInfo['월'] = dt.datetime.now().month
            if '년' not in bufferInfo:
                bufferInfo['년'] = dt.datetime.now().year

            bufferInfo['Content'] = info[ContentCount+1:]
            print(f'ContentCount는 {ContentCount}에 있다')
            print(str(bufferInfo))
            bufferInfo['time'] = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            MyApp.Qinfo.append(bufferInfo)
            with open('Calendar_File.json', 'w', encoding='utf-8') as f:
                json.dump(MyApp.Qinfo, f, indent='\t')

    def initUI(self):
        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.clicked[QDate].connect(self.showDate)
        #
        self.BasicInfo = QLabel(self)
        date = cal.selectedDate()
        self.BasicInfo.setText(date.toString())
        #
        self.DateInfo = QLabel(self)
        self.DateInfo.setText(str('비어있네용~'))
        for info in MyApp.Qinfo:
            if int(info['년']) == date.year() and int(info['월']) == date.month() and int(info['일']) == date.day():
                self.DateInfo.setText(str(info))

        self.DateInfo.setAlignment(Qt.AlignCenter)
        font1 = self.DateInfo.font()
        font1.setPointSize(20)
        self.DateInfo.setFont(font1)
        #
        vbox = QVBoxLayout()
        vbox.addWidget(cal)
        vbox.addWidget(self.BasicInfo)
        vbox.addWidget(self.DateInfo)
        #
        self.setLayout(vbox)
        #
        self.setWindowTitle('QCalendarWidget')
        self.setGeometry(300, 300, 400, 300)
        self.show()

    def showDate(self, date):
        ContentList = []
        self.BasicInfo.setText(date.toString())
        self.DateInfo.setText('비어있네용~')
        for info in MyApp.Qinfo:
            if info['년'] == date.year() and info['월'] == date.month() and info['일'] == date.day():
                ContentList.append(info['Content'])
        if ContentList:
            self.DateInfo.setText('\n'.join(ContentList))

if __name__ == '__main__':
    Program_Loop = TkLoop()

# 메인 윈도우 기능
# 1. 녹화 내용을 보여 주는 텍스트
# 2. 녹화 내용 취소 기능
# 3. 타임 라인(2주 전후?)
# 4. 스케줄 읽어 주는 버튼(음성 인식 후 해당 날짜 스케줄을 출력 또는 읽어줌)

# 캘린더 윈도우 기능
# 1. 스케줄 읽어 주는 기능
