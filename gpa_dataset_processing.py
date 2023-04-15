import pandas as pd

df = pd.read_csv('gpa.csv')
df_subset = df.loc[:, ['Subject', 'Course', 'Course Title', 'Average Grade']]

grouped_df = df_subset.groupby(['Subject', 'Course'])['Average Grade'].mean()
grouped_df = grouped_df.rename('Mean Grade').reset_index()
grouped_df = grouped_df.rename(columns={'Subject': 'Subject Abbreviation'})
grouped_df.to_csv('gpa_condensed.csv', index=False)
