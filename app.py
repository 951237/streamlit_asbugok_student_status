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
lst_xlsx.sort()
default_ix = lst_xlsx[-1]

# st.dataframe(df)

# --- 사이드바 생성하기 ---
st.sidebar.header("Please Filter Here:")	# 사이드바 헤더(제목)
# 파일 선택하기 
file_xlsxs = st.sidebar.selectbox(
	"Select data file:",
	lst_xlsx,
	index=lst_xlsx.index(default_ix)  # 마지막 값 선택
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


# 첫번째 단락
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
		color = total_student_line.index,
		template="plotly_white"
	)

	st.plotly_chart(fig_total_student, use_container_width=True)

with right:
	right.write('### 전교 남녀 비율')
	# pie graph
 
	test = df.groupby('학년').sum()

	test_t = test.T.reset_index()
	test_t.columns = ['성별', '1학년', '2학년', '3학년', '4학년', '5학년', '6학년']
	test_t = test_t.drop(index=2)

	col_list = list(test_t)
	col_list.remove('성별')
	test_t['합계'] = test_t[col_list].sum(axis=1)
	test_t = test_t[['성별','합계']]

	fig = px.pie(test_t, values='합계', names='성별')

	st.plotly_chart(fig, use_container_width=True)

def df_query(p_grade):
	# 학년별로 그룹지어서 전체 합계 요약
	str_expr = f"학년 == '{p_grade}'"
	df_gr = df.query(str_expr)
	df_gr = df_gr[['반','합계']]
	return df_gr

# 2번째 단락 - 1, 2, 3학년 현황
left_01, mid_01, right_01 = st.columns(3)

with left_01:
	# 학년 인원 그래프로 나타내기 
	left_01.write('### 1학년 학급별 현황')

	df_1gr = df_query('1학년')

	# 수평 바그래프
	fig_1gr_student = px.bar(
		df_1gr,
		y = '반',
		x = '합계',
		orientation='h',
		color = '반',
		template="plotly_white"
	)

	st.plotly_chart(fig_1gr_student, use_container_width=True)
 
with mid_01:
	# 학년 학급별 현황 그래프로 나타내기 
	mid_01.write('### 2학년 학급별 현황')

	# 학년별로 그룹지어서 전체 합계 요약
	df_2gr = df_query('2학년')

	# 수평 바그래프
	fig_2gr_student = px.bar(
		df_2gr,
		y = '반',
		x = '합계',
  		orientation='h',
		color = '반',
		template="plotly_white"
	)

	st.plotly_chart(fig_2gr_student, use_container_width=True)
 
with right_01:
	# 학년 학급별 현황 그래프로 나타내기 
	right_01.write('### 3학년 학급별 현황')

	# 학년별로 그룹지어서 전체 합계 요약
	df_3gr = df_query('3학년')

	# 수평 바그래프
	fig_3gr_student = px.bar(
		df_3gr,
		y = '반',
		x = '합계',
  		orientation='h',
		color = '반',
		template="plotly_white"
	)

	st.plotly_chart(fig_3gr_student, use_container_width=True)

# 2번째 단락 - 4, 5, 6학년 현황
left_02, mid_02, right_02 = st.columns(3)

with left_02:
	# 학년 학급별 현황 그래프로 나타내기 
	left_02.write('### 4학년 학급별 현황')

	df_4gr = df_query('4학년')

	# 수평 바그래프
	fig_4gr_student = px.bar(
		df_4gr,
		y = '반',
		x = '합계',
		orientation='h',
		color = '반',
		template="plotly_white"
	)

	st.plotly_chart(fig_4gr_student, use_container_width=True)
 
with mid_02:
	# 학년 학급별 현황 그래프로 나타내기 
	mid_02.write('### 5학년 학급별 현황')

	# 학년별로 그룹지어서 전체 합계 요약
	df_5gr = df_query('5학년')

	# 수평 바그래프
	fig_5gr_student = px.bar(
		df_5gr,
		y = '반',
		x = '합계',
  		orientation='h',
		color = '반',
		template="plotly_white"
	)

	st.plotly_chart(fig_5gr_student, use_container_width=True)
 
with right_02:
	# 학년 학급별 현황 그래프로 나타내기 
	right_02.write('### 6학년 학급별 현황')

	# 학년별로 그룹지어서 전체 합계 요약
	df_6gr = df_query('6학년')

	# 수평 바그래프
	fig_6gr_student = px.bar(
		df_6gr,
		y = '반',
		x = '합계',
  		orientation='h',
		color = '반',
		template="plotly_white"
	)

	st.plotly_chart(fig_6gr_student, use_container_width=True)


# 5번째 단락 - 인구피라미드 (1학년부터 6학년까지)




