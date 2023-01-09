# ------------------------- 학년 선택 
# 형식 st.sidebar.multiselect("안내문구", 리스트)
grade = st.sidebar.multiselect(
	"Select the Grade:",
	options = df['학년'].unique(),
	default = df['학년'].unique()
)

# ------------------------- 학급 선택
class_num = st.sidebar.multiselect(
	"Select the Class_num:",
	options = df['반'].unique(),
	default = df['반'].unique()
)

# 데이터 프레임 칼럼 이름으로 설정하기
df_selection = df.query(
	"학년 == @grade & 반 == @class_num"		# '학년'은 데이터프레임 칼럼
)