from class_objects import *
import time

def main():
    stt = SpeechToText()
    soong = SoongSiri()
    tts = TextToSpeech()

    error_cnt = 0

    while True:
        speaker = stt.speech_to_text()
        print(speaker)

        answer = soong.recognize_speech(speaker)

        # 음성 재생은 none을 반환
        if answer == '잘 모르겠어요':
            if error_cnt == 2:
                print('죄송해요 제가 더 공부할게요')

            tts.text_to_speech('다시 한번 말씀해주시겠어요?')
            error_cnt += 1
            continue

        if type(answer) == str:
            tts.text_to_speech(answer)
            return

        # 답변이 복잡할 때, list로 여러개 담음
        elif type(answer) == list:
            for text in answer:
                tts.text_to_speech(text)
            return
    # 파일 삭제
    os.system('rm stt.wav speech.mp3')
    return

if __name__ == '__main__':
    main()
