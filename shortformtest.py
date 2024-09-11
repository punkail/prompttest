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

# TTS에서 제외할 텍스트 제거 함수
def filter_tts_text(text):
    lines = text.splitlines()
    filtered_lines = [line for line in lines if not line.startswith('### 추천타이틀') and not line.startswith('### 소제목 및 요약')]
    return '\n'.join(filtered_lines)

# 특수문자 제거 및 한글 텍스트만 남기는 함수
def remove_special_characters(text):
    cleaned_text = re.sub(r'[^\uAC00-\uD7A3\s]', '', text)  # 한글 및 공백만 남기기
    return cleaned_text

# 친구대화형 요약에서 소제목+숫자 제거 함수
def remove_subtitle_numbers(text):
    cleaned_text = re.sub(r'소제목 \d+', '', text)
    return cleaned_text

# 추천타이틀과 소제목 앞에 * 표시 추가
def add_bullet_points(text):
    bullet_text = text.replace("추천타이틀", "* 추천타이틀").replace("소제목 및 요약", "* 소제목 및 요약")
    return bullet_text

# TTS 자동 생성 함수
def create_tts(result, key):
    if result:
        filtered_text = filter_tts_text(result)
        tts = generate_tts(filtered_text, lang='ko')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        st.session_state[key] = audio_file.getvalue()

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
타이틀
 -원본 타이틀 의미를 유지해서 5개의 추천 타이틀 생성해.
 -타이틀 어투는 숏폼 영상 타이틀에 적합하게 트렌디하고 간결하게 작성해.
 -각 타이틀은 20자 이내로 생성해.

소제목
 -각 문단 시작할 때 문단 내용을 바탕으로 소제목 만들어.
 -소제목 글자수는 최대 20자야.
 -소제목의 위치는 각 문단 시작할 때 첫번째 줄에 배치해줘.

본문
 -전달하는 원본 텍스트 의미를 유지해서 300자로 요약해줘.
 -1차 요약된 내용을 8문단으로 나눠줘.
 -각 문단의 내용을 한글기준 50자 이내로 요약해.
 -요약문의 어투는 뉴스 아나운서가 사용하는 뉴스어, 표준어로 작성해.
 -9번째 문단을 추가로 더 생성하고, 본문 내용을 마무리하는 클로징 멘트 50자 이내로 작성해.
"""

# 친구대화형 프롬프트 텍스트 설정
친구대화형_프롬프트 = """
타이틀
 -원본 타이틀 의미를 유지해서 5개의 추천 타이틀 생성해. 
 -타이틀 어투는 숏폼 영상 타이틀에 적합하게 트렌디하고 간결하게 작성해.
 -각 타이틀은 20자 이내로 생성해.

소제목
 -각 문단 시작할 때 문단 내용을 바탕으로 소제목 작성해. 
 -소제목 글자수는 최대 20자의 의문형으로 끝내.
 -소제목 어투는 숏폼 영상 타이틀에 적합하게 트렌디하고 간결하게 작성해.
 -각 소제목은 의문형으로 끝내.
 -소제목의 위치는 각 문단 시작할 때 첫번째 줄에 배치해줘.

본문
 -전달하는 원본 텍스트 의미를 유지해서 300자로 1차 요약해줘. 
 -친구에게 알려주는 자연스럽고 편한 어투로 적어줘.
 -트렌디하고 간결한 어투로 재미있게 적어줘.
 -1차 요약된 내용을 8문단으로 나눠줘.
 -각 문단의 내용을 한글기준 50자 이내로 요약해.
 -9번째 문단을 추가로 더 생성해.
 -마지막 문단은 본문 내용을 마무리하는 클로징 멘트 50자 이내로 작성해.
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
                result1 = remove_special_characters(add_bullet_points(response1.choices[0].message['content'].strip()))  # 특수문자 제거 및 * 표시 추가
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
                    temperature=temperature,  # 설정한 temperature 값 반영
                    stop=None
                )
                result2 = remove_special_characters(remove_subtitle_numbers(add_bullet_points(response2.choices[0].message['content'].strip())))  # 특수문자 및 소제목+숫자 제거, * 표시 추가
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
