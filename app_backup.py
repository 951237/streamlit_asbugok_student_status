import os
import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import app01
import app02

# streamlit 페이지 생성
st.set_page_config(
    page_title='안산부곡초 재학생 현황',		# 브라우저 탭 제목
    page_icon = ":bar_chart:",				# 브라우저 파비콘
    layout = "wide"							# 레이아웃
    )

# 폴더내에 파일 읽어오기
def read_xlsx_files():
	path = "./data"
	file_list = os.listdir(path)
	lst_xlsx = [file for file in file_list if file.endswith(".xlsx")]	# 폴더내 확장자가 엑셀파일 인것을 리스트에 담기
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
lst_xlsx.sort()		# 리스트 정렬하기
default_ix = lst_xlsx[-1]	# 셀렉박스 기본값을 최신파일로 설정

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
str_date = file_xlsxs.split('.')[0]		# 파일이름에서 날짜 추출
str_now = f'{str_date[:2]}.{str_date[2:4]}.{str_date[4:]}' 	# 날짜의 형식 만들기

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

# 추세선 그래프
st.write('## 재적인원 추세 그래프')

def make_list_by_date(p_file):
    name_date = p_file.split('.')[0]		# 파일에서 확장자 앞 이름 분리
    df = get_excelfile(p_file).ffill()

    df_0927 = df[['학년', '합계']]
    t_0927 = df_0927.groupby('학년').sum()	# 학년으로 그룹짓기
    test_t = t_0927.T.reset_index()		# 행열 변환하기
    test_t = test_t[['1학년', '2학년', '3학년', '4학년', '5학년', '6학년']]
    return test_t, name_date	# 1~6학년의 인원과 날짜 데이터를 반환

result = []
lst_date = [] 	# 엑셀파일 이름 모을 리스트

# 파일의 리스트를 이용해서 데이터를 추출하고 하나의 데이터 프레임으로 만들기
for i in lst_xlsx:
    df_temp, name_date = make_list_by_date(i)
    result.append(df_temp)
    lst_date.append(name_date)
df_result = pd.concat(result)		# 리스트의 데이터를 하나의 데이터 프레임으로 생성하기
df_result['날짜'] = lst_date		# 날짜 데이터를 칼럼으로 넣기
df_result.columns.name = None
df_result = df_result.set_index('날짜')	# 날짜를 인덱스로 설정

st.line_chart(df_result, use_container_width=True)


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

# 함수 - 데이터 프레임에서 특정 데이터만 불러오기
def df_query(p_grade):
	# 학년별로 그룹지어서 전체 합계 요약
	str_expr = f"학년 == '{p_grade}'"
	df_gr = df.query(str_expr)
	df_gr = df_gr[['반','남','여']]
	return df_gr

# 함수 - 데이터 프레임을 이용하여 그래프 그리기
def make_plotly_chart(p_gr):
	df_result = df_query(p_gr)

	# 수평 바그래프
	fig = px.bar(
		df_result,
		y = '반',
		x = ['남','여'],
		orientation='h',
		# color = '반',
		template="plotly_white"
	)
	fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})  # 값 정렬
	st.plotly_chart(fig, use_container_width=True)

# 2번째 단락 - 1, 2, 3학년 현황
left_01, mid_01, right_01 = st.columns(3)

with left_01:
	# 학년 인원 그래프로 나타내기 
	left_01.write('### 1학년 학급별 현황')
	make_plotly_chart('1학년')
 
with mid_01:
	# 학년 학급별 현황 그래프로 나타내기 
	mid_01.write('### 2학년 학급별 현황')
	make_plotly_chart('2학년')
 
with right_01:
	# 학년 학급별 현황 그래프로 나타내기 
	right_01.write('### 3학년 학급별 현황')
	make_plotly_chart('3학년')


# 2번째 단락 - 4, 5, 6학년 현황
left_02, mid_02, right_02 = st.columns(3)

with left_02:
	# 학년 학급별 현황 그래프로 나타내기 
	left_02.write('### 4학년 학급별 현황')
	make_plotly_chart('4학년')
 
with mid_02:
	# 학년 학급별 현황 그래프로 나타내기 
	mid_02.write('### 5학년 학급별 현황')
	make_plotly_chart('5학년')
 
with right_02:
	# 학년 학급별 현황 그래프로 나타내기 
	right_02.write('### 6학년 학급별 현황')
	make_plotly_chart('6학년')


# 5번째 단락 - 인구피라미드 (1학년부터 6학년까지)

