import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import json

from utility import save_json, load_json
import time


class SSUNoticeCrawler(object):
    def __init__(self):
        # 기존에 저장된 파일 불러오기
        try:
            self.data_dic = load_json('../data/ssu_notice.json')
            print('기존에 저장된 공지사항에 이어서 데이터 수집을 진행합니다.')
        except:
            self.data_dic = defaultdict(lambda : [])
            print('저장된 공지사항이 없습니다. 새롭게 데이터를 수집합니다.')

        self.title_ls = [dic['title'] for dic in self.data_dic['전체']]

        # 크롤링 소스
        self.req = requests.get('http://www.ssu.ac.kr/web/kor/plaza_d_01').content
        self.soup = BeautifulSoup(self.req, 'html.parser')

        # table rows(tr) 따기
        self.trs = list(self._get_trs())
        return


    def crawl_data(self):
        # tr을 타고 게시글 크롤링
        for tr in self.trs:
            title = self._get_title(tr)
            date = self._get_date(tr)
            hlink = self._get_hlink(tr)

            category = self._get_category(title)
            text = self._get_text(hlink)

            # 각각의 데이터를 dictionary 형태로 저장
            temp_dic = {
                'title' : title,
                'category' : category,
                'date' : date,
                'hlink' : hlink,
                'text' : text
            }

            self.data_dic['전체'].append(temp_dic)
            self.data_dic[category].append(temp_dic)
        return



    # 공지사항 table rows를 긁어오는 함수
    def _get_trs(self):
        tr_css = '#p_p_id_EXT_MIRRORBBS_ > div > div > div.contents > table.bbs-list > tbody > tr'
        trs = self.soup.select(tr_css)

        for tr in trs:
            title = self._get_title(tr)

            if not title in self.title_ls:
                yield tr
        return

    # 제목 수집하는 함수
    def _get_title(self, tr):
        return tr.a.text.strip()

    # 날짜 추출하는 함수
    def _get_date(self, tr):
        return re.findall('[0-9]{4}\.[0-9]{2}\.[0-9]{2}', tr.text).pop()

    # 링크 추출하는 함수
    def _get_hlink(self, tr):
        return tr.a.get('href')

    # 제목에서 분류(카테고리)를 추출하는 함수
    def _get_category(self, title):
        cat = re.findall('\\[.+?\\]', title)
        if cat:
            return cat[0].replace('[', '').replace(']', '')
        else:
            return '기타'

    # 링크를 타고 들어가서 본문 내용 수집하는 함수
    def _get_text(self, hlink):
        # 본문 구조가 다른 경우가 존재
        text_soup = BeautifulSoup(requests.get(hlink).content, 'html.parser')
        text_css1 = '#p_p_id_EXT_MIRRORBBS_ > div > div > div.contents > table.bbs-body > tbody > tr > td > div > div'
        text_css2 = '#p_p_id_EXT_MIRRORBBS_ > div > div > div.contents > table.bbs-body > tbody > tr > td > div'

        # 본문의 div 태그 아래에, 문장별로 div태그가 줄줄이 달린 경우
        if text_soup.select(text_css1):
            text =  '\n'.join([txt.text.replace('\xa0','') for txt in text_soup.select(text_css1)])
        # 본문의 div 태크 하나만 있는 경우
        else:
            text = text_soup.select(text_css2).pop().text.replace('\xa0','')
        return text


    def save_data(self):
        save_json(self.data_dic, '../data/ssu_notice.json')
        print('수집 결과를 저장합니다.')
        return

if __name__ == '__main__':
    # 크롤러 객체 생성
    ssunotice_crawler = SSUNoticeCrawler()

    # 크롤링 수행
    ssunotice_crawler.crawl_data()

    # 결과 저장
    ssunotice_crawler.save_data()
