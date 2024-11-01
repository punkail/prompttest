import streamlit as st

# 페이지 설정 - 와이드 레이아웃 활성화
st.set_page_config(layout="wide")

# 페이지 제목 및 설명
st.title("요약 프롬프트 및 템플릿 테스트 페이지")

# 탭 생성
tab1, tab2 = st.tabs(["요약 프롬프트 & 템플릿 테스트", "프롬프트 리스트"])

# 첫 번째 탭: 요약 프롬프트 & 템플릿 테스트
with tab1:
    st.header("요약 프롬프트 & 템플릿 테스트")
    st.write("요약 프롬프트와 템플릿 테스트 페이지를 나란히 임베딩하여 한 번에 테스트를 진행합니다.")

    # 두 개의 컬럼 생성 (가로로 화면을 최대한 활용)
    col1, col2 = st.columns([1, 1])

    # 1. 요약 프롬프트 테스트 페이지 임베딩
    with col1:
        st.header("요약 프롬프트 테스트")
        st.markdown(
            """
            <iframe src="http://shorts-proto.sandbox.onkakao.net:5001/" width="100%" height="800" frameborder="0"></iframe>
            """,
            unsafe_allow_html=True
        )

    # 2. 템플릿 테스트 페이지 임베딩
    with col2:
        st.header("템플릿 테스트")
        st.markdown(
            """
            <iframe src="https://ai-shorts.deft.kakao.com/config" width="100%" height="800" frameborder="0"></iframe>
            """,
            unsafe_allow_html=True
        )

    # 3. 샘플 URL 리스트 섹션
    st.header("샘플 URL 리스트")

    sample_urls = {
        "뉴스뷰": "https://v.daum.net/v/20241101105927154",
        "콘텐츠뷰": "https://v.daum.net/v/FMexnsqyIv",
        "쇼핑하기": "https://store.kakao.com/tripfit/products/438075189?area=mainp&impression_id=air_store_talkdeal_main&ordnum=3",
        "로컬": "https://place.map.kakao.com/269932132"
    }

    # 가로로 나열하여 세로 스크롤 최소화
    cols = st.columns(len(sample_urls))

    for i, (category, url) in enumerate(sample_urls.items()):
        with cols[i]:
            st.subheader(category)
            st.write(url)
            st.button("복사하기", key=url)

# 두 번째 탭: 프롬프트 리스트
with tab2:
    st.header("프롬프트 리스트")
    st.markdown(
        """
        <iframe src="https://docs.google.com/spreadsheets/d/1oUOQ8vSa3GbeZSxOw8bv3JURV8AVrAJSO2jD1bpPHUM/edit?pli=1&gid=1621344732#gid=1621344732" width="100%" height="800" frameborder="0"></iframe>
        """,
        unsafe_allow_html=True
    )
