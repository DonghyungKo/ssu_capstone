from class_objects import *
import time

def main(self.):

    kakao = KakaoSpeech()
    soong = SoongSiri()
    error_cnt = 0

    while True:
        speaker = kakao.speech_to_text()
        print(speaker)

        answer = soong.recognize_speech(speaker)
        print(answer)

        # 음성 재생은 none을 반환
        if answer == '잘 모르겠어요':
            if error_cnt <= 2:
                kakao.text_to_speech('다시 한번 말씀해주시겠어요?')
                error_cnt += 1
                continue
            else:
                kakao.text_to_speech('죄송해요 제가 더 공부할게요')
                break

        # str은 한 문장짜리 답변
        if type(answer) == str:
            kakao.text_to_speech(answer)
            return

        # 답변이 복잡할 때, list로 여러개 담음
        elif type(answer) == list:
            for text in answer:
                kakao.text_to_speech(text)
            return

        # 답변이 tts가 아닌 audio file 재생인 경우
        else :
            #soong.youtube_audio.stop_audio()
            return
    return

if __name__ == '__main__':
    main()