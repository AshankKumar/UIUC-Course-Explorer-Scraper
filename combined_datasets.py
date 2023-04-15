import pandas as pd

df_courses = pd.read_csv('fa-2023-courses.csv')
df_gpa = pd.read_csv('gpa_condensed.csv')


merged_df = pd.merge(df_courses, df_gpa, on=['Subject Abbreviation', 'Course'], how='left')

merged_df.to_csv('fa-2023-courses-with-gpa.csv', index=False)