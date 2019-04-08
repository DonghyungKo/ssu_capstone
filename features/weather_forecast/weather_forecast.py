import requests
from bs4 import BeautifulSoup

class WeatherForecast(object):
    def __init__(self):
        self.body = requests.get('https://search.naver.com/search.naver?sm=top_hty&fbm=0&ie=utf8&query=%EC%98%A4%EB%8A%98+%EB%82%A0%EC%94%A8').content
        self.soup = BeautifulSoup(self.body, 'html.parser')
        self.today_temp = self.soup.select('#main_pack > div.sc.cs_weather._weather > div:nth-child(2) > div.weather_box > div.weather_area._mainArea > div.today_area._mainTabContent > div.main_info > div > p > span.todaytemp')
    #def tell_weather():

    #def recommend_clothes():

if __name__=='__main__':
    weather_forcast = WeatherForecast()
    print(weather_forcast.soup)
    print(weather_forcast.today_temp)
