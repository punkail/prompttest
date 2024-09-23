import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO
import re
import requests
from bs4 import BeautifulSoup

# 페이지 설정: 여백 없이 꽉 찬 레이아웃 사용
st.set_page_config(layout="wide")

# OpenAI API Key 설정
openai.api_key = st.secrets["API_KEY"]

# 페이지 제목 설정
st.title("생성툴 프롬프트 테스트")

# URL에서 본문 텍스트 추출 함수
def extract_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 타이틀 추출
    title = soup.select_one('.tit_head')
    title_text = title.get_text(strip=True) if title else "제목을 찾을 수 없습니다."
    
    # 본문 텍스트 추출
    body = soup.select_one('.group_body')
    body_text = body.get_text(separator=' ', strip=True) if body else "본문을 찾을 수 없습니다."

    return title_text, body_text

# 세션 상태 초기화
if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'result1' not in st.session_state:
    st.session_state['result1'] = ""

if 'result2' not in st.session_state:
    st.session_state['result2'] = ""

if 'audio1' not in st.session_state:
    st.session_state['audio1'] = None

if 'audio2' not in st.session_state:
    st.session_state['audio2'] = None

# 공통 함수: 히스토리에 저장
def save_to_history(prompt1, prompt2, result1, result2):
    st.session_state['history'].append({
        '프롬프트1': prompt1,
        '프롬프트2': prompt2,
        '요약 결과1': result1,
        '요약 결과2': result2
    })

# TTS 생성 함수
def generate_tts(text, lang='ko'):
    tts = gTTS(text=text, lang=lang)
    return tts

# 추천타이틀과 소제목 앞에 * 표시 추가 및 소제목 끝에 ? 추가
def add_bullet_points_with_question_mark(text):
    bullet_text = text.replace("추천타이틀", "* 추천타이틀").replace("소제목 및 요약", "* 소제목 및 요약")
    bullet_text = re.sub(r'(소제목\s?\d*)', r'\1?', bullet_text)  # 소제목 끝에 ? 추가
    return bullet_text

# 본문 텍스트의 글자 수 계산 함수
def calculate_text_length(text):
    length = len(re.sub(r'\s', '', text))  # 공백을 제외한 글자 수 계산
    return f"({length}자)"

# 본문 URL 입력과 기본 URL 설정
st.header("본문 URL 입력")
input_url = st.text_input("URL을 입력하세요", "https://v.daum.net/v/25eh6vtsZk")
if input_url:
    try:
        title, body_text = extract_content(input_url)
        st.success(f"제목: {title}")
    except Exception as e:
        st.error(f"URL에서 내용을 가져오는 중 오류가 발생했습니다: {e}")

# 기본 본문 텍스트 설정
default_main_text = body_text if input_url else """
하반기 출시를 앞둔 신형 현대 팰리세이드의 디자인 변화에 관심이 모아지고 있다. 최근 숏카 채널에 포착된 테스트 차량을 통해 디자인의 일부 모습이 드러났다.
"""

# 기본 프롬프트 텍스트 설정
뉴스형_프롬프트 = """
#역할
{Q}: 관심 내용을 질문하는 뉴스 앵커 (나이와 성별 제한 없음)
{A}: 주요 뉴스 내용을 전달하는 리포터 또는 패널 (나이와 성별 제한 없음)

#상황
주어진 content를 바탕으로 뉴스를 요약하고 발표하는 형식의 대화 진행

#입력 값
전달하는 content의 의미를 유지해서 요약하기

#단계별 지시사항
최대 300자로 내용을 요약합니다.
요약이 완료되면 세부 구성에 맞춰서 재편집합니다.

#세부 구성
요약된 내용을 함축하는 뉴스 타이틀을 5종류 만듭니다.
문단 규칙에 따라 소제목과 내용을 생성합니다.
규칙1: 소제목과 내용으로 구성된 문단 총 7개를 만듭니다.
규칙2: 특히 마지막 7번째 문단은 1~6문단을 요약하고 마무리하는 뉴스 발표 내용으로 구성하세요.

##타이틀
전체 내용을 담은 뉴스 타이틀로, 글자 수는 최대 20자로 제한합니다.
주제에 맞는 적절한 키워드를 담아 시청자의 관심을 끌 수 있어야 합니다.

###문장 규칙
문장 스타일은 요약형으로 만듭니다.
예시를 참고해 주세요.

####example (여행 컨셉) 
ex1. 숨겨진 여름 휴양지 소개
ex2. 이탈리아 여행의 매력

####example (자동차 컨셉) 
ex1. 최신 전기차 트렌드
ex2. 연비 좋은 SUV 추천

####example (맛집 컨셉) 
ex1. 서울에서 꼭 가야 할 맛집
ex2. 한식 맛집 TOP 5 선정

##소제목
글자 수는 최대 20자로 제한합니다.
{Q}가 {A}에게 각 문단의 내용에 대해 질문합니다.

###문장 규칙
문장 스타일은 질문형으로 만들고, 문장의 끝은 ‘-인가요?’로 끝납니다.
주제에 맞게 자연스러운 질문을 만들어 주세요.

####example (여행 컨셉) 
ex1. 이 여행지의 특징은 무엇인가요?
ex2. 추천하는 여행 시기는 언제인가요?

####example (자동차 컨셉) 
ex1. 이 차의 주요 기능은 무엇인가요?
ex2. 연비는 얼마나 좋은가요?

####example (맛집 컨셉) 
ex1. 이 식당의 대표 메뉴는 무엇인가요?
ex2. 분위기는 어떤가요?

##내용
글자 수 최소 20자, 최대 50자로 입력할 수 있습니다.
{A}가 {Q}에게 각 문단의 내용을 요약해서 답변합니다.

###문장 규칙 {A}
질문에 대한 답변을 간결하게 전달하며, 문장의 끝을 ‘-입니다.’로 끝냅니다.
주제에 맞는 자연스러운 대답을 구성하세요.

####example (여행 컨셉) 
ex1. 이곳은 맑은 바다와 하얀 모래 해변으로 유명합니다.
ex2. 가장 적절한 여행 시기는 5월부터 9월까지입니다.

####example (자동차 컨셉) 
ex1. 이 차는 최신 자율주행 기술을 탑재하고 있습니다.
ex2. 연비는 리터당 18km로 매우 효율적입니다.

####example (맛집 컨셉) 
ex1. 대표 메뉴는 불고기와 전통 비빔밥입니다.
ex2. 분위기는 따뜻하고 가족 친화적입니다.

##제약사항
content의 내용에 있지 않은 내용은 절대 포함할 수 없습니다.
비속어는 반드시 제거합니다.
주제에 맞는 정확한 정보만 포함해야 합니다.
"""


친구대화형_프롬프트 = """
#역할
- {Q} : 친구에게 질문하는 걸 좋아하는 상냥하고 귀여운 19살의 여대생 (mbti는 ENFJ)
- {A} : 친구와 대화하고 정보 전달을 좋아하는 친절한 19살의 여대생 (mbti는 ESTJ)

#상황
- content 내용에 대해 친구와 메시지를 주고받으며 대화하기

#입력 값
- 전달하는 content의 의미를 유지해서 요약하기

#단계별 지시사항
1. 최대 300자로 내용을 요약합니다.
2. 요약이 완료되면 세부 구성에 맞춰서 재편집합니다.

#세부 구성
- 요약된 내용을 함축하는 타이틀을 5종류 만듭니다.
- 문단 규칙에 지켜서 소제목과 내용을 생성합니다.
- 규칙1. 소제목과 내용으로 구성된 문단 총 5개를 만듭니다.
- 규칙2. 특히 마지막 5번째 문단은 1~4문단을 정리하는 대화 내용으로 구성하세요.

##타이틀
- 전체 내용을 담은 내용으로 글자수 최대 20자까지 사용할 수 있습니다.
- 청자의 시선을 끌 수 있는 키워드를 담고 있어야 합니다.

###문장 규칙
- 문장 스타일은 요약형으로 만듭니다.
- 예시를 참고해 주세요.

####example
ex1. 애플 충격적인 신제품 출시 현장
ex2. 대한민국 축구 기적의 4강 진출

##소제목
- 글자수 최대 20자까지 사용할 수 있습니다.
- {Q}가 {A}에게 각 문단의 내용에 대해 질문합니다.

###문장 규칙
- 문장 스타일은 질문형으로 만들고 문장의 끝은  ‘-했어?’으로 끝냅니다.
- 예시를 참고해 주세요.

####example
ex1. 오늘이 무슨 날이야?
ex2. 애플이 신제품 발표했어?

##내용
- 글자수 최소 20지, 최대 50자까지 입력할 수 있습니다.
- {A}가 {Q}에게 각 문단의 내용을 요약해서 답변합니다.

###문장 규칙 {A}
- 지금부터 문장의 끝을 ‘-했어.’으로 끝냅니다. 
- 예시를 참고해 주세요.

####example
ex1. 대한민국이 100번째 금메달을 딴 날이야.
ex2. 응, 새벽에 애플이 오늘 신제품을 발표했어.
ex3. 맞아. 손흥민은 대한민국을 최고의 축구선수야.

##제약사항
- content의 내용에 있지 않은 내용은 절대 포함할 수 없습니다.
- 비속어는 반드시 제거합니다.
"""




# temperature 값 입력 UI 추가 (기본값: 0.2)
st.header("Prompt Temperature 설정")
temperature = st.slider("프롬프트 생성의 다양성을 설정하세요 (0.0은 일관성, 1.0은 창의성)", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

# 레이아웃 설정
st.header("본문 텍스트")
main_text = st.text_area("본문 텍스트를 입력하세요.", value=default_main_text, height=200)  # 높이 조정
st.write(calculate_text_length(main_text))  # 본문 텍스트의 글자 수 출력

col1, col2, col3 = st.columns([1.8, 1.8, 2], gap="large")  # 컬럼 비율 조정: 프롬프트 영역을 넓게, 요약 결과는 좁게

# 첫 번째 컬럼 (프롬프트 입력)
with col1:
    st.header("뉴스형 프롬프트")
    prompt1 = st.text_area("뉴스형 프롬프트를 입력하세요.", value=뉴스형_프롬프트, height=500)
    if st.button("뉴스형 프롬프트로 요약하기"):
        if not main_text or not prompt1:
            st.warning("본문 텍스트와 프롬프트를 모두 입력해야 합니다.")
        else:
            with st.spinner('요약문을 생성 중입니다...'):
                response1 = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{prompt1}\n\n{main_text}"}
                    ],
                    max_tokens=1200,  # 더 긴 요약을 위해 max_tokens 증가
                    temperature=temperature,  # 설정한 temperature 값 반영
                    stop=None
                )
                result1 = response1.choices[0].message['content'].strip()  # API 응답을 그대로 사용
                st.session_state['result1'] = result1
                save_to_history(prompt1, st.session_state.get('prompt2', ""), result1, st.session_state.get('result2', ""))

    st.header("친구대화형 프롬프트")
    prompt2 = st.text_area("친구대화형 프롬프트를 입력하세요.", value=친구대화형_프롬프트, height=500)
    if st.button("친구대화형 프롬프트로 요약하기"):
        if not main_text or not prompt2:
            st.warning("본문 텍스트와 프롬프트를 모두 입력해야 합니다.")
        else:
            with st.spinner('요약문을 생성 중입니다...'):
                response2 = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{prompt2}\n\n{main_text}"}
                    ],
                    max_tokens=1200,
                    temperature=temperature,
                    stop=None
                )
                result2 = response2.choices[0].message['content'].strip()  # API 응답을 그대로 사용
                st.session_state['result2'] = result2
                save_to_history(prompt1, prompt2, st.session_state.get('result1', ""), result2)

# 두 번째, 세 번째 컬럼 (요약 결과)
with col2:
    st.header("뉴스형 요약결과")
    summary1 = st.text_area("요약 결과 1", value=st.session_state.get('result1', ''), height=1000)  # 고정 높이 설정
    if st.button("복사하기", key="copy1"):
        st.code(st.session_state.get('result1', ''), language='text')
        st.success("요약 결과 1을 복사하세요.")
    

with col3:
    st.header("친구대화형 요약결과")
    summary2 = st.text_area("요약 결과 2", value=st.session_state.get('result2', ''), height=1000)  # 고정 높이 설정
    if st.button("복사하기", key="copy2"):
        st.code(st.session_state.get('result2', ''), language='text')
        st.success("요약 결과 2를 복사하세요.")
    

# Streamlit 앱 종료
st.stop()
