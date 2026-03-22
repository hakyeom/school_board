import streamlit as st
import pandas as pd

# 이 곳에 Supabase에서 데이터를 가져오는 코드를 추가합니다.
# 예시 데이터프레임
data = {
    'school_name': ['운암중학교', '운암중학교'],
    'title': ['[답변대기] 질문있습니다.', '[답변대기] 이것 좀 확인해주세요.'],
    'content_url': ['http://example.com/1', 'http://example.com/2'],
    'created_at': ['2026-03-01', '2026-03-02']
}
df = pd.DataFrame(data)

st.title("학교 게시판 답변대기 목록")

# 학교 선택 버튼 (향후 여러 학교 추가시 확장)
selected_school = st.button("운암중학교")

if selected_school:
    st.header("운암중학교 답변대기 목록")
    school_df = df[df['school_name'] == '운암중학교']
    
    for index, row in school_df.iterrows():
        st.subheader(row['title'])
        st.write(f"작성일: {row['created_at']}")
        st.link_button("게시물 바로가기", row['content_url'])
        st.divider()
