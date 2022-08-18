import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt

# 할일
# TODO:파일의 선택하기
# TODO:그래프 추가 (원그래프, )


# streamlit 페이지 생성
st.set_page_config(
    page_title='Bugok Class Dashboard',		# 브라우저 탭 제목
    page_icon = ":bar_chart:",				# 브라우저 파비콘
    layout = "wide"							# 레이아웃
    )


# 데이터 파일 불러오기 및 전처리
def get_excelfile():
	df = pd.read_excel(
		io = "data.xlsx",
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
	return df

df = get_excelfile()	# 데이터 프레임 생성

# st.dataframe(df)

# --- 사이드바 생성하기 ---
st.sidebar.header("Please Filter Here:")	# 사이드바 헤더(제목)

# 학년 선택 
# 형식 st.sidebar.multiselect("안내문구", 리스트)
grade = st.sidebar.multiselect(
	"Select the Grade:",
	options = df['학년'].unique(),
	default = df['학년'].unique()
)

# 학급 선택
class_num = st.sidebar.multiselect(
	"Select the Class_num:",
	options = df['반'].unique(),
	default = df['반'].unique()
)

# 데이터 프레임 칼럼 이름으로 설정하기
df_selection = df.query(
	"학년 == @grade & 반 == @class_num"		# '학년'은 데이터프레임 칼럼
)

# --- 메인 페이지 ---
st.title(":bar_chart: 안산부곡초 재적인원 현황판")		# 화면 타이틀
st.markdown("##")		# 마크다운 문법 가능

# 상단 현황판
total_class = int(len(df_selection['반']))
total_man = int(df_selection['남'].sum())
total_woman = int(df_selection['여'].sum())
total_student = int(df_selection['남'].sum() + df_selection['여'].sum())

# 화면분할 - 4분할
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

left, right = st.columns(2)

with left:
	# 학년 인원 그래프로 나타내기 

	# 학년별로 그룹지어서 전체 합계 요약
	total_student_line = (
		df_selection.groupby(by=['학년']).sum()[['합계']].sort_values(by="합계")
	)

	# 수평 바그래프
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

st.write('### 남녀 비율 그래프')
with right:
	# pie graph
	labels = 'Boy', 'Girl'
	man_ratio = (total_man / total_student) * 100
	woman_ratio = (total_woman / total_student) * 100

	sizes = [man_ratio, woman_ratio]

	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

	st.pyplot(fig1)