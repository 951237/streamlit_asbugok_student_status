import pandas as pd
import plotly.express as px
import streamlit as st

# 할일
# TODO:파일의 선택하기
# TODO:그래프 추가 (원그래프, )


# streamlit 페이지 생성
st.set_page_config(
    page_title='Bugok Class Dashboard',
    page_icon = ":bar_chart:",
    layout = "wide"
    )


# 엑셀파일 불러오기
# 데이터 파일 불러오기
df = pd.read_excel(
    io = "/Users/mac/project/app_bugok_dashboard_student/data.xlsx",
    engine="openpyxl",
    sheet_name="실시간 학생수",
    skiprows=1,
    usecols="A:D",
    nrows=39
)

# '반'칼럼 nan값 삭제
df = df.dropna(axis=0, subset=['반'])

# 이덱스 리셋
df = df.reset_index(drop='INDEX')

# 학년에 칼럼에 학년 입력하기
df['학년'].loc[:5] = '1학년'
df['학년'].loc[5:9] = '2학년'
df['학년'].loc[9:14] = '3학년'
df['학년'].loc[14:20] = '4학년'
df['학년'].loc[20:25] = '5학년'
df['학년'].loc[25:] = '6학년'

# 인원 합계
df['합계'] = df['남'] + df['여']

# st.dataframe(df)

# sidebar
st.sidebar.header("Please Filter Here:")

grade = st.sidebar.multiselect(
	"Select the Grade:",
	options = df['학년'].unique(),
	default = df['학년'].unique()
)

class_num = st.sidebar.multiselect(
	"Select the Class_num:",
	options = df['반'].unique(),
	default = df['반'].unique()
)

# 데이터 프레임 칼럼 이름으로 설정하기
df_selection = df.query(
	"학년 == @grade & 반 == @class_num"
)

# --- 메인 페이지 ---
st.title(":bar_chart: 안산부곡초 재적인원 현황판")
st.markdown("##")

# 상단 현황판
total_class = int(len(df_selection['반']))
total_man = int(df_selection['남'].sum())
total_woman = int(df_selection['여'].sum())
total_student = int(df_selection['남'].sum() + df_selection['여'].sum())

left_column, middle01_column, middle02_column, right_column = st.columns(4)
with left_column:
    st.subheader("전체 학급수:")
    st.subheader(f"총 {total_class:,}학급")
with middle01_column:
    st.subheader("남학생 인원:")
    st.subheader(f"{total_man:,}명")
with middle02_column:
    st.subheader("여학생 인원:")
    st.subheader(f"{total_woman:,}명")
with right_column:
    st.subheader("전체 인원:")
    st.subheader(f"{total_student:,}명")
    
st.markdown("---")

total_student_line = (
    df_selection.groupby(by=['학년']).sum()[['합계']].sort_values(by="합계")
)

fig_total_student = px.bar(
	total_student_line,
	x = '합계',
	y = total_student_line.index,
	orientation='h',
	title = "<b>Total Student Line</b>",
	color_discrete_sequence=["#0083B8"] * len(total_student_line),
	template="plotly_white"
)

st.plotly_chart(fig_total_student)