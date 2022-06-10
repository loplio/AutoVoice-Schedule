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
from playsound import playsound

url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
REST_API_KEY = "34c37e7d8540ec5f7697a00c28d78ab9"
header = {
    "Content-Type": "application/octet-stream",
    "Authorization": "KakaoAK " + f"{REST_API_KEY}"
}
url_syn = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"
header_syn = {
    "Content-Type": "application/xml",
    "Authorization": "KakaoAK " + f"{REST_API_KEY}"
}

DayOfTheWeek = ['월', '화', '수', '목', '금', '토', '일']
with open('Calendar_File.json', 'r', encoding='utf-8') as f:
    QInfo = json.load(f)


def ShowCalendar(info):
    app = QApplication(sys.argv)
    ex = MyApp(info)
    app.exec_()


class TkLoop:
    setDate = {'year': dt.datetime.now().year, 'month': dt.datetime.now().month, 'day': dt.datetime.now().day}
    message = None
    publicContent = None

    def __init__(self):
        self.VoiceSupport = AutoVoice()
        self.content = None
        self.textInfo = None

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

        BlankLabel = Label(self.frame, text=' 녹음', width=5)
        BlankLabel.grid(column=2, row=0)
        DateLabel = Label(self.frame, textvariable=self.date_var)
        DateLabel.grid(column=0, row=2, columnspan=5)
        self.ScrolledText1 = scrolledtext.ScrolledText(self.frame, width=50, height=3, font=("Consolas", 10))
        self.ScrolledText1.grid(column=0, row=3, columnspan=5)
        self.ScrolledText2 = scrolledtext.ScrolledText(self.frame, width=50, height=7, font=("Consolas", 10))
        self.ScrolledText2.grid(column=0, row=4, columnspan=5)
        self.updateTimeLine()
        self.EntryText = Entry(self.frame, width=40)
        self.EntryText.bind('<Return>', self.getInputInfo)
        self.EntryText.grid(column=0, row=1, columnspan=4)
        EntryButton = Button(self.frame, text='입력', width=10, command=self.getInputInfo)
        EntryButton.grid(column=4, row=1)
        button1 = Button(self.frame, text='달력', command=lambda: ShowCalendar(self.VoiceSupport.RecVoice))
        button1.grid(column=0, row=0)
        button2 = Button(self.frame, text='음성인식', command=lambda: self.updateContent('Voice'))
        button2.grid(column=1, row=0)
        button3 = Button(self.frame, text='저장', width=10, command=lambda: [MyApp.AppendInfo(self.VoiceSupport.RecVoice),
                                                                           self.insertStateContent('Save Success.')])
        button3.grid(column=3, row=0)
        button4 = Button(self.frame, text='삭제', width=10,
                         command=lambda: [self.insertStateContent('Delete Success.'),
                                          self.VoiceSupport.RemoveRecVoice()])
        button4.grid(column=4, row=0)

        self.root.bind('<Escape>', self.stop)
        self.root.mainloop()

    def updateTimeLine(self):
        self.ScrolledText2.delete('1.0', END)
        self.ScrolledText2.insert(END, f'<    로그 시간    >                      #timeline ' + '\n')
        for info in QInfo:
            if info['year'] == TkLoop.setDate['year'] and info['month'] == TkLoop.setDate['month'] and info['day'] == \
                    TkLoop.setDate['day']:
                self.ScrolledText2.insert(END, f'[{info["time"][:-3]}] {info["Content"]}' + '\n')

    def getInputInfo(self, event=None):
        self.textInfo = self.EntryText.get().strip()
        self.updateContent('Text')

    def updateContent(self, method):
        TkLoop.message = None

        if method == 'Voice':
            self.content = self.VoiceSupport.VoiceRecognition()
        elif method == 'Text':
            self.content = self.VoiceSupport.TextRecognition(self.textInfo)

        if TkLoop.publicContent:
            self.insertStateContent(TkLoop.publicContent)

        if TkLoop.message:
            self.ScrolledText1.insert(END, f'Err: {TkLoop.message}' + '\n')
        else:
            if self.content:
                self.ScrolledText1.insert(END, 'Voice: ' + self.content + '\n')
                if self.VoiceSupport.RecVoice:
                    if self.VoiceSupport.RecVoice['Content']:
                        self.ScrolledText1.insert(END, 'Content: ' + self.VoiceSupport.RecVoice['Content'] + '\n')
                    else:
                        self.ScrolledText1.insert(END, 'The content is empty.' + '\n')
                else:
                    self.ScrolledText1.insert(END, 'Date setting error' + '\n')
            if self.VoiceSupport.RecVoice:
                TkLoop.setDate["year"] = self.VoiceSupport.RecVoice["year"]
                TkLoop.setDate["month"] = self.VoiceSupport.RecVoice["month"]
                TkLoop.setDate["day"] = self.VoiceSupport.RecVoice["day"]
                self.date_var.set(f'{TkLoop.setDate["year"]}년 {TkLoop.setDate["month"]}월 {TkLoop.setDate["day"]}일')

        self.ScrolledText1.see('end')

        self.updateTimeLine()

    def insertStateContent(self, stateInfo):
        if 'Save Success.' in stateInfo:
            if self.VoiceSupport.RecVoice:
                self.ScrolledText1.insert(END, f'{stateInfo}\n')
                self.updateTimeLine()
            else:
                self.ScrolledText1.insert(END, f'There is nothing to save\n')
        elif 'Delete Success.' in stateInfo:
            if self.VoiceSupport.RecVoice:
                self.ScrolledText1.insert(END, f'{stateInfo}\n')
            else:
                self.ScrolledText1.insert(END, f'There is nothing to delete\n')
        elif 'All Deleted.' in stateInfo:
            self.ScrolledText1.insert(END, f'{stateInfo}\n')
        elif 'Delete Complete.' in stateInfo:
            self.ScrolledText1.insert(END, f'{stateInfo}\n')

        self.ScrolledText1.see('end')

    def stop(self, event=None):
        self.root.destroy()

class AutoVoice:

    def __init__(self):
        self.RecVoice = None

    def soundPlay(self):
        try:
            playsound("temp.mp3")
        except Exception as err:
            self.soundPlay()

    def TextRecognition(self, result):
        print(result)
        return self.Recognition({'value': result})

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

        return self.Recognition(result)

    def Recognition(self, result):
        fullcontent = result['value']

        CalRegexInfo = re.compile(r'(^(\d{0,4}년\b)? *(\d{1,2}월\b)? *(\d{1,2}일\b)?)?'
                                  rf'(^(이번 ?주 {DayOfTheWeek}요일\b)|^(다음 ?주 {DayOfTheWeek}요일)\b)?')
        DelRegexInfo = re.compile(r'((^\d+|이)번 ?(일정)?|전부) ?삭제$')
        if fullcontent:
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
            tailcontent = fullcontent[ContentCount + 1:].strip()
            if tailcontent.startswith('일정 알려줘'):
                ContentCount += 7
                for info in QInfo:
                    if info['year'] == year and info['month'] == month and info['day'] == day and info['Content']:
                        read_text = info['Content']
                        print('read_text : ' + read_text)
                        data = f'<speak>{read_text}</speak>'
                        res_syn = requests.post(url_syn, headers=header_syn, data=data.encode('utf-8'))
                        with open('temp.mp3', 'wb') as f:
                            f.write(res_syn.content)
                        self.soundPlay()
            elif bool(DelRegexInfo.match(tailcontent)):
                if bool(re.compile('\d+').match(tailcontent)):
                    delNum = int(re.compile('\d+').search(tailcontent).group()) - 1
                else:
                    if tailcontent.startswith('전부'):
                        print("all_DEL")
                        TkLoop.publicContent = 'All Deleted.'
                        while True:
                            for i, info in enumerate(QInfo):
                                if info['year'] == year and info['month'] == month and info['day'] == day:
                                    MyApp.RemoveInfo(i)
                                    break
                                elif len(QInfo) - 1 == i:
                                    return
                        print("all_DEL Error")
                    delNum = 2 - 1
                TkLoop.publicContent = f'{delNum+1}. Delete Complete.'
                if delNum >= 0:
                    for i, info in enumerate(QInfo):
                        if info['year'] == year and info['month'] == month and info['day'] == day:
                            if delNum == 0:
                                MyApp.RemoveInfo(i)
                                return
                            delNum -= 1
                return

            tailcontent = fullcontent[ContentCount + 1:].strip()
            time = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

        try:
            dt.date(year, month, day)
            self.RecVoice = {'year': year, 'month': month, 'day': day, 'time': time, 'Content': tailcontent}
        except Exception as e:
            print('날짜 설정 오류!', e)
            self.RecVoice = None
        return fullcontent
        print(result)
        print(result['value'])

    def RemoveRecVoice(self):
        self.RecVoice = None


class MyApp(QWidget):
    def __init__(self, info):
        super().__init__()
        self.BasicInfo = None
        self.DateInfo = None
        self.initUI()

    @staticmethod
    def AppendInfo(info):
        print('AppendInfo: ' + str(info))
        if info:
            QInfo.append(info)
            with open('Calendar_File.json', 'w', encoding='utf-8') as f:
                json.dump(QInfo, f, indent='\t')

    @staticmethod
    def RemoveInfo(n):
        del QInfo[n]
        with open('Calendar_File.json', 'w', encoding='utf-8') as f:
            json.dump(QInfo, f, indent='\t')

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
        for info in QInfo:
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
        for info in QInfo:
            if info['year'] == date.year() and info['month'] == date.month() and info['day'] == date.day():
                ContentList.append(info['Content'])
        if ContentList:
            self.DateInfo.setText('\n'.join(ContentList))


if __name__ == '__main__':
    Program_Loop = TkLoop()

# 메인 윈도우 기능
# 1. 해당 날짜에 적은 내용 추가할 수 있는 버튼, 날짜 별 로그(voice, content 로그) 그리고 해당 날짜 적혀 있는 내용 보여 주기(타임 라인에) - 3시간
# 2. 타임 라인(2주 전후?/time 추가), 추가 - 다음주 일정 알려줘, 이번주 일정 알려줘, 이번달 일정 알려줘, (특정 일자) 일정 알려줘 - 3시간
# 3. 타임 라인과 음성 인식 정보란 분리. - 3시간
# 4. 스케줄 읽어 주는 버튼(음성 인식 후 해당 날짜 스케줄을 출력 또는 읽어줌)

# 캘린더 윈도우 기능
# 1. 스케줄 읽어 주는 기능
