import os
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

# 폴더내에 
def read_xlsx_files():
	path = "./data"
	file_list = os.listdir(path)
	lst_xlsx = [file for file in file_list if file.endswith(".xlsx")]
	return lst_xlsx
	


# 데이터 파일 불러오기 및 전처리
def get_excelfile(p_file):
	df = pd.read_excel(
		io = f'./data/{p_file}',
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

	# 인원 합계
	df['합계'] = df['남'] + df['여']
	return df

lst_xlsx = read_xlsx_files()

# st.dataframe(df)

# --- 사이드바 생성하기 ---
st.sidebar.header("Please Filter Here:")	# 사이드바 헤더(제목)
# 파일 선택하기 
file_xlsxs = st.sidebar.selectbox(
	"Select data file:",
	lst_xlsx,
	index=lst_xlsx[-1]
)

# 데이터프레임 만들기
df = get_excelfile(file_xlsxs).ffill()	# 데이터 프레임 생성
str_date = file_xlsxs.split('.')[0]
str_now = f'{str_date[:2]}.{str_date[2:4]}.{str_date[4:]}'

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
st.write(f"### {str_now} 현재")
st.title(":bar_chart: 안산부곡초 재적인원 현황판")

# 화면 타이틀
st.markdown("##")		# 마크다운 문법 가능

# 상단 현황판
total_class = int(len(df_selection['반']))
total_man = int(df_selection['남'].sum())
total_woman = int(df_selection['여'].sum())
total_student = int(df_selection['남'].sum() + df_selection['여'].sum())

# 화면분할 - 4분할
left_column, middle01_column, middle02_column, right_column = st.columns(4)
with left_column:
    st.subheader(f"전체 학급수 : {total_class}학급")
with middle01_column:
    st.subheader(f"남학생 : {total_man}명")
with middle02_column:
    st.subheader(f"여학생 : {total_woman}명")
with right_column:
    st.subheader(f"전체 : {total_student}명")
    
st.markdown("---")

left, right = st.columns([3,2])

with left:
	# 학년 인원 그래프로 나타내기 
	left.write('### 학년별 인원')

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
		color_discrete_sequence=["#0083B8"] * len(total_student_line),
		template="plotly_white"
	)

	st.plotly_chart(fig_total_student, use_container_width=True)

with right:
	right.write('### 남녀 비율')
	# pie graph
 
	test = df_selection.groupby('학년').sum()

	test_t = test.T.reset_index()
	test_t.columns = ['성별', '1학년', '2학년', '3학년', '4학년', '5학년', '6학년']
	test_t = test_t.drop(index=2)

	col_list = list(test_t)
	col_list.remove('성별')
	test_t['합계'] = test_t[col_list].sum(axis=1)
	test_t = test_t[['성별','합계']]

	fig = px.pie(test_t, values='합계', names='성별')

	st.plotly_chart(fig, use_container_width=True)


fig1 = px.bar(df_selection, 
	x='지역', 
	y='인원',
	title="전보유형별 제출 현황",
	color='전보유형',
	text_auto=True   #그래프에 수치 나타내기
	)
fig1.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})  # 값 정렬
st.plotly_chart(fig1, use_container_width=True)

# 2줄 3칼럼 - 학년별 집계 보이기
