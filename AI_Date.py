import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import scrolledtext
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

DayOfTheWeek = ['월', '화', '수', '목', '금', '토', '일']

def ShowCalendar(info):
    app = QApplication(sys.argv)
    ex = MyApp(info)
    app.exec_()


class TkLoop:
    setDate = {'year': dt.datetime.now().year, 'month': dt.datetime.now().month, 'day': dt.datetime.now().day}
    message = None

    def __init__(self):
        self.VoiceSupport = AutoVoice()
        self.content = None

        self.root = Tk()
        self.root.title("Image Collect")
        self.root.geometry("420x340+1000+100")
        self.root.resizable(False, False)

        self.date_var = tkinter.StringVar()
        self.date_var.set(f'{TkLoop.setDate["year"]}년 {TkLoop.setDate["month"]}월 {TkLoop.setDate["day"]}일')

        self.frame = Frame(self.root)
        self.frame.pack()
        # self.Imageframe = Frame(self.root)
        # self.Imageframe.pack()
        self.NowImage = Image.open('image1.jpg')
        self.tk_image = ImageTk.PhotoImage(self.NowImage.resize((420, 200)))
        imglabel = Label(self.root, image=self.tk_image)
        imglabel.pack()

        blanklabel = Label(self.frame, text=' 녹음', width=5)
        blanklabel.grid(column=2, row=0)
        datelabel = Label(self.frame, textvariable=self.date_var)
        datelabel.grid(column=0, row=1, columnspan=5)
        text1 = scrolledtext.ScrolledText(self.frame, width=50, height=10, font=("Consolas", 10))
        text1.grid(column=0, row=2, columnspan=5)
        button1 = Button(self.frame, text='달력', command=lambda: ShowCalendar(self.VoiceSupport.RecVoice))
        button1.grid(column=0, row=0)
        button2 = Button(self.frame, text='음성인식', command=lambda: self.updateContent(text1))
        button2.grid(column=1, row=0)
        button3 = Button(self.frame, text='저장', width=10, command=lambda: [MyApp.AppendInfo(self.VoiceSupport.RecVoice),
                                                                           self.insertStateContent(text1,
                                                                                                   'Save Success.')])
        button3.grid(column=3, row=0)
        button4 = Button(self.frame, text='삭제', width=10,
                         command=lambda: [self.insertStateContent(text1, 'Delete Success.'),
                                          self.VoiceSupport.RemoveRecVoice()])
        button4.grid(column=4, row=0)

        self.root.bind('<Escape>', self.stop)
        self.root.bind('q', self.stop)
        self.root.mainloop()

    def updateContent(self, text1):
        TkLoop.message = None
        self.content = self.VoiceSupport.VoiceRecognition()
        if TkLoop.message:
            text1.insert(END, f'Err: {TkLoop.message}' + '\n')
        else:
            if self.content:
                text1.insert(END, 'Voice: ' + self.content + '\n')
                if self.VoiceSupport.RecVoice:
                    if self.VoiceSupport.RecVoice['Content']:
                        text1.insert(END, 'Content: ' + self.VoiceSupport.RecVoice['Content'] + '\n')
                    else:
                        text1.insert(END, 'The content is empty.' + '\n')
                else:
                    text1.insert(END, 'Date setting error' + '\n')

            if self.VoiceSupport.RecVoice:
                TkLoop.setDate["year"] = self.VoiceSupport.RecVoice["year"]
                TkLoop.setDate["month"] = self.VoiceSupport.RecVoice["month"]
                TkLoop.setDate["day"] = self.VoiceSupport.RecVoice["day"]
                self.date_var.set(f'{TkLoop.setDate["year"]}년 {TkLoop.setDate["month"]}월 {TkLoop.setDate["day"]}일')

    def insertStateContent(self, text1, stateInfo):
        if 'Save Success.' in stateInfo:
            if self.VoiceSupport.RecVoice:
                text1.insert(END, f'{stateInfo}\n')
            else:
                text1.insert(END, f'There is nothing to save\n')
        elif 'Delete Success.' in stateInfo:
            if self.VoiceSupport.RecVoice:
                text1.insert(END, f'{stateInfo}\n')
            else:
                text1.insert(END, f'There is nothing to delete\n')

    def stop(self, event=None):
        self.root.destroy()


class AutoVoice:

    def __init__(self):
        self.RecVoice = None

    def VoiceRecognition(self):
        try:
            with sr.Microphone(sample_rate=16000) as source:
                print("Say something!")
                r = sr.Recognizer()
                audio = r.listen(source, timeout=3)

            res = requests.post(url, headers=header, data=audio.get_raw_data())
            result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}') + 1]
            result = json.loads(result_json_string)

        except Exception as err:
            TkLoop.message = err
            return

        fullcontent = result['value']

        CalRegexInfo = re.compile(r'(^(\d{0,4}년\b)? *(\d{1,2}월\b)? *(\d{1,2}일\b)?)?'
                                  rf'(^(이번 ?주 {DayOfTheWeek}요일\b)|^(다음 ?주 {DayOfTheWeek}요일)\b)?')
        if fullcontent is not None:
            date_info = CalRegexInfo.search(fullcontent).group()
            if re.compile(r'\d').search(date_info) or not date_info:
                if bool(date_info):
                    ymd = date_info.split()
                    ContentCount = fullcontent.find('일')
                else:
                    ymd = []
                    day = TkLoop.setDate['day']
                    ContentCount = -1

                year = TkLoop.setDate['year']
                month = TkLoop.setDate['month']
                for n in ymd:
                    if '년' in n:
                        year = int(re.compile(r'\d+').search(n).group())
                    elif '월' in n:
                        month = int(re.compile(r'\d+').search(n).group())
                    elif '일' in n:
                        day = int(re.compile(r'\d+').search(n).group())
            else:
                str_day = date_info[date_info.find('요') - 1]
                day_delta = DayOfTheWeek.index(str_day) - dt.datetime.today().weekday()
                
                if '이번' in date_info:
                    day_info = dt.datetime.today() + dt.timedelta(days=day_delta)
                elif '다음' in date_info:
                    day_info = dt.datetime.today() + dt.timedelta(days=day_delta + 7)

                year = day_info.year
                month = day_info.month
                day = day_info.day
                ContentCount = fullcontent.find('요일') + 1

            content = fullcontent[ContentCount + 1:].lstrip()
            time = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        try:
            dt.date(year, month, day)
            self.RecVoice = {'year': year, 'month': month, 'day': day, 'time': time, 'Content': content}
        except Exception as e:
            print('날짜 설정 오류!', e)
            self.RecVoice = None
        return fullcontent
        print(result)
        print(result['value'])

    def RemoveRecVoice(self):
        self.RecVoice = None


class MyApp(QWidget):
    with open('Calendar_File.json', 'r', encoding='utf-8') as f:
        Qinfo = json.load(f)

    def __init__(self, info):
        super().__init__()
        self.BasicInfo = None
        self.DateInfo = None
        self.initUI()

    @staticmethod
    def AppendInfo(info):
        print('AppendInfo: ' + str(info))
        if info:
            MyApp.Qinfo.append(info)
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
            if info['year'] == date.year() and info['month'] == date.month() and info['day'] == date.day():
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
        self.setWindowTitle('Calendar')
        self.setGeometry(300, 300, 400, 300)
        self.show()

    def showDate(self, date):
        ContentList = []
        self.BasicInfo.setText(date.toString())
        self.DateInfo.setText('비어있네요~')
        for info in MyApp.Qinfo:
            if info['year'] == date.year() and info['month'] == date.month() and info['day'] == date.day():
                ContentList.append(info['Content'])
        if ContentList:
            self.DateInfo.setText('\n'.join(ContentList))


if __name__ == '__main__':
    Program_Loop = TkLoop()

# 메인 윈도우 기능
# 1. 녹화 내용을 보여 주는 텍스트
# 2. 녹화 내용 취소 기능
# 3. 타임 라인(2주 전후?) - 다음주 일정 알려줘, 이번주 일정 알려줘, 이번달 일정 알려줘, (특정 일자) 일정 알려줘
# 4. 스케줄 읽어 주는 버튼(음성 인식 후 해당 날짜 스케줄을 출력 또는 읽어줌)

# 캘린더 윈도우 기능
# 1. 스케줄 읽어 주는 기능
