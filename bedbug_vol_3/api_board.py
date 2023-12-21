from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import os
import configparser
import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import font_manager, rc
import base64
import numpy as np
import io
import folium
import mplcursors
from datetime import datetime

# 현재 날짜 및 시간 가져오기
current_datetime = datetime.now()

# 원하는 형식으로 날짜 및 시간 문자열로 변환
formatted_datetime = current_datetime.strftime("%Y년%m월%d일 %H:%M:%S")


# 현재  실행파일의 절대 경로를 얻어옵니다.
path = os.path.abspath(__file__)

# 현재 실행파일이 있는 디렉토리를 얻어옵니다.
directory = os.path.dirname(path)

# 디렉토리 출력
print("현재 실행파일이 있는 디렉토리:", directory)
# --------------------------------------------------

# ---ini화일 불러오기------------------------------------
# INI 파일 경로
ini_file_path = os.path.join(directory, 'setup.ini')
# ConfigParser 객체 생성
config = configparser.ConfigParser()
# INI 파일 읽기
config.read(ini_file_path,encoding='utf-8')
# 섹션과 옵션 값 가져오기 value=빈대
news_search1 = config.get('setup', 'news-search') #search1 = 빈대
news_number = config.get('setup', 'news-number') #search1 = 빈대
api_url = config.get('setup', 'api_url') 
X_Naver_Client_Id = config.get('setup', 'X-Naver-Client-Id') 
X_Naver_Client_Secret = config.get('setup', 'X-Naver-Client-Secret') 
print("news 검색어는:",news_search1)
# ------------------------------------------------

# ------엑셀그래프그리기---------------------------
font_path = 'C:\Windows\Fonts\gulim.ttc'
font_manager.fontManager.addfont(font_path)
plt.rc('font', family='gulim')

# 파일 이름을 포함한 경로를 생성합니다.
excel_file_name = 'bedbug.xlsx'
print("excel_file_name:", excel_file_name)

# 엑셀 파일의 전체 경로를 생성합니다.
excel_file_path = os.path.join(directory, excel_file_name)
print("excel_file 디렉토리:", excel_file_path)
try:
    # 엑셀 파일을 읽어옵니다.
    df = pd.read_excel(excel_file_path)
    # DataFrame을 필요에 따라 처리
except FileNotFoundError:
    print(f"파일을 찾을 수 없습니다: {excel_file_path}")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")

df['시도명'] = df['시도명'].astype(str)
df = df.sort_values(by='총 누적 (C=A+B)', ascending=False)
fig, ax = plt.subplots()
colors = plt.cm.viridis(np.linspace(0, 1, len(df['시도명'][2:17])))
# 각 막대에 대해 색상을 지정하여 막대 그래프 생성
bedbug_plt = ax.bar(df['시도명'][2:17], df['총 누적 (C=A+B)'][2:17], color=colors)
ax.set_xlabel('시도명')  # x축 라벨 설정
ax.set_ylabel('총 누적 (C=A+B)')  # y축 라벨 설정
ax.tick_params(axis='x', rotation=45)  # x축 라벨 회전
fig.set_size_inches(10, 8) # 그래프 너비 조절
fig.tight_layout() # 중앙에 위치

# 그래프를 이미지로 저장
output = io.BytesIO()
fig.savefig(output, format="png")
bedbug_image_data = "data:image/png;base64," + base64.b64encode(output.getvalue()).decode('utf-8')

#원형그래프
labels = ['숙박', '쪽방촌', '학교_기숙사', '기타', '목욕탕_찜질방', '가정집','고시원', '외국인기숙사']
sizes = [2,2,2,4,6,10,12,18]
total = sum(sizes)

# 백분율 계산 함수
def calculate_percentage(value):
    return (value / total) * 100
percentages = [calculate_percentage(size) for size in sizes]
df_selected = df[labels]
# df_selected['총합'] = df_selected[labels[2:18]].sum(axis=1)
df_selected.loc[:, '총합'] = df_selected[labels[1:]].sum(axis=1)
# df_selected.loc[:, '총합'] = df_selected[labels[1:18]].sum(axis=1)

def generate_pie_chart(data):
    fig, ax = plt.subplots(figsize=(9, 8))

    ax.pie(percentages, labels=labels, autopct='%1.2f%%', startangle=90)
    ax.axis('equal') 

    # pie_chart_image_data = generate_pie_chart(df_selected)

    # 그래프를 이미지로 저장
    output = io.BytesIO()
    fig.savefig(output, format="png")
    return base64.b64encode(output.getvalue()).decode('utf-8') 


#fOLIUM 그래프

mymap = folium.Map(city=[37.5665, 126.9780], zoom_start=7)

# 각 도시의 누적값을 구함
city_totals = df.groupby('시도명')['총 누적 (C=A+B)'].sum().reset_index()

# 도시의 위치 정보 (위도, 경도)를 미리 알고 있다면 사용
city_locations = {
    '서울': (37.5665, 126.9780),
    '부산': (35.1796, 129.0756),
    '대구': (35.8714, 128.6014),
    '인천': (37.4563, 126.7052),
    '광주': (35.1595, 126.8526),
    '대전': (36.3504, 127.3845),
    '울산': (35.5467, 129.3150),
    '경기': (37.4138, 127.5188),
    '강원': (37.8228, 128.1555),
    '충북': (36.6357, 127.4919),
    '충남': (36.6588, 126.6723),
    '전남': (34.8194, 126.8930),
    '경북': (36.4919, 128.8889),
    # '제주': (33.4996, 126.5312),
}

citydata = [
    {'lat': 37.5665, 'lng': 126.9780, 'name': '서울', 'total': 92},
    {'lat': 35.1796, 'lng': 129.0756, 'name': '부산', 'total': 2},
    {'lat': 35.8714, 'lng': 128.6014, 'name': '대구', 'total': 7},
    {'lat': 37.4563, 'lng': 126.7052, 'name': '인천', 'total': 11},
    {'lat': 35.1595, 'lng': 126.8526, 'name': '광주', 'total': 1},
    {'lat': 36.3504, 'lng': 127.3845, 'name': '대전', 'total': 3},
    {'lat': 35.5467, 'lng': 129.3150, 'name': '울산', 'total': 1},
    {'lat': 37.4138, 'lng': 127.5188, 'name': '경기', 'total': 42},
    {'lat': 37.8228, 'lng': 128.1555, 'name': '강원', 'total': 4},
    {'lat': 36.6357, 'lng': 127.4919, 'name': '충북', 'total': 6},
    {'lat': 36.6588, 'lng': 126.6723, 'name': '충남', 'total': 11},
    {'lat': 34.8194, 'lng': 126.8930, 'name': '전남', 'total': 4},
    {'lat': 36.4919, 'lng': 128.8889, 'name': '경북', 'total': 1},
]

for index, row in city_totals.iterrows():
    city = row['시도명']
    total = row['총 누적 (C=A+B)']
    lat, lng = city_locations.get(city, (0, 0))  # 도시의 위치 정보 가져오기, 없으면 (0, 0)으로 설정

    if lat != 0 and lng != 0:  # 위치 정보가 있는 경우에만 마커 추가
        folium.CircleMarker(
            location=[lat, lng],
            radius=total / 10,  # 동그라미 크기 조절
            color='blue',  # 동그라미 색상
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            popup=f"{city}: {total} 마리"  # 팝업에 표시할 정보
        ).add_to(mymap)



# Folium 지도를 HTML로 저장
        
# 현재 스크립트 파일의 경로
script_dir = os.path.dirname(os.path.abspath(__file__))

# 'templates' 폴더 경로
templates_dir = os.path.join(script_dir, 'templates')

# 'index.html' 파일 경로
index_html_path = os.path.join(templates_dir, 'index.html')

folium_map_html = 'index_html_path'
mymap.save(folium_map_html)

# 막대그래프 설정
fig, ax = plt.subplots()
bedbug_plt = ax.bar(df['시도명'], df['총 누적 (C=A+B)'])
ax.set_xlabel('시도명')  # x축 라벨 설정
ax.set_ylabel('총 누적 (C=A+B)')  # y축 라벨 설정
# ax.set_title('막대 그래프')  # 그래프 제목 설정
ax.tick_params(axis='x', rotation=45)  # x축 라벨 회전

# 그래프 너비 조절
fig.set_size_inches(10, 6)
# 중앙에 위치
fig.tight_layout()

# 그래프를 이미지로 저장
output = io.BytesIO()
FigureCanvas(fig).print_png(output)

# 이미지를 바이트 스트림으로 변환
image_data = "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()


# ---------------news api 다루기-----------------------
app = Flask(__name__, template_folder='templates')

def get_naver_news(api_key, query, display=news_number):
    base_url = api_url #
    headers = {
        "X-Naver-Client-Id": X_Naver_Client_Id,
        "X-Naver-Client-Secret": X_Naver_Client_Secret,
    }

    params = {
        "query": query,
        "display": display,
    }

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print(f"Error: {response.status_code}")
        return None

def clean_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove specific tags: <b> and </b>
    for tag in soup.find_all(['b']):
        tag.unwrap()

    return soup.get_text()

# api index에 표현 
api_key = 'YOUR_NAVER_API_KEY'
query = news_search1
result = get_naver_news(api_key, query)

if result:
    news_list = []
    for news in result:
        news_info = {
            'title': clean_html_tags(news.get('title', '')),
            'link': news.get('link', ''),
            'description': clean_html_tags(news.get('description', ''))
        }
        news_list.append(news_info)



# ---------------챗봇 -----------------------
@app.route('/toggle_chatbot', methods=['POST'])
def toggle_chatbot():
    global chatbot_open

    # 챗봇 상태를 토글
    chatbot_open = not chatbot_open
    # 챗봇의 필요한 작업을 수행
    return jsonify({'chatbot_status': 'open' if chatbot_open else 'close'})

# -----------------------------------------------------

@app.route('/')
def index():

    meta_data = {
        'title': '빈대알리미',
        'description': '빈대맵과 빈대에 관한 대한민국의 지역 별 현황 및 뉴스 등을 제공합니다.',
    }

    news_title =news_search1+ "  "+ "NEWS"
    news_time = formatted_datetime
    pie_chart_image_data = generate_pie_chart(df_selected)
    return render_template('index.html', news_list=news_list, news_title=news_title, meta_data=meta_data, image_data=image_data, folium_map_path=folium_map_html, pie_chart_image_data=pie_chart_image_data,news_time =news_time)
        # return render_template('index.html', news_list=news_list,news_title=news_title,meta_data=meta_data, image_data=image_data, folium_map_path=folium_map_html)

if __name__ == '__main__':
    app.run(debug=True)
