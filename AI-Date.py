# import speech_recognition as sr
# import pyaudio
#
# recognizer = sr.Recognizer()
#
# with sr.AudioFile('고용노동과법 실습.wav') as source:
#     audio = recognizer.record(source, duration=120)
# text = recognizer.recognize_google(audio_data=audio, language='ko')
# print(text)
# mic = sr.Microphone(sample_rate=16000)
#
# with mic as source:
#     recognizer.adjust_for_ambient_noise(source)
#     print("무엇을 도와드릴깝쇼? <^ㅗ^)")
#     print("음성을 청취합니다. ".format(recognizer.energy_threshold))
#     audio = recognizer.listen(source)
#
# try:
#     data = recognizer.recognize_google(audio, language="ko")
# except:
#     print("이해하지 못했어요")
#
# print(data)


# vText = r.recognize_google(audio_data=audio, language='ko-KR')
# print(vText)
import requests
import json
import speech_recognition as sr
import pyaudio

url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
REST_API_KEY = "34c37e7d8540ec5f7697a00c28d78ab9"
header = {
    "Content-Type": "application/octet-stream",
    "Authorization": "KakaoAK " + f"{REST_API_KEY}"
}

r = sr.Recognizer()
with sr.Microphone(sample_rate=16000) as source:
    print("Say something!")
    audio = r.listen(source)
res = requests.post(url, headers=header, data=audio.get_raw_data())
print(res.text)

result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
result = json.loads(result_json_string)
print(result)
print(result['value'])
print("hello")