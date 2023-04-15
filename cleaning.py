import pandas as pd
from bs4 import BeautifulSoup
import requests
import ast
import json

def getSubjectNamesDict():
    URL = 'https://courses.illinois.edu/cisapp/explorer/catalog/2023/spring.xml'

    url_link = requests.get(URL)
    soup = BeautifulSoup(url_link.text, "lxml")

    subjects = soup.find_all('subject')

    dic = {}
    for subject in subjects:
        # print(subject.id)
        # break
        # print(subject['id'] + " " + subject.text)
        dic[subject['id']] = subject.text
    return dic

enums = {
    'Nat Sci & Tech - Phys Sciences course': 'Nat Sci & Tech', 
    'Social & Beh Sci - Beh Sci': 'Social & Beh Sci', 
    'Social & Beh Sci - Soc Sci course': 'Social & Beh Sci', 
    'Advanced Composition': 'Advanced Composition', 
    'Nat Sci & Tech - Life Sciences course': 'Nat Sci & Tech', 
    'Grand Challenge-Sustainability course': 'Grand Challenge', 
    'Camp Honors/Chanc Schol course': 'Camp Honors/Chanc Schol', 
    'Nat Sci & Tech - Life Sciences': 'Nat Sci & Tech', 
    'Nat Sci & Tech - Phys Sciences': 'Nat Sci & Tech', 
    'Quantitative Reasoning II': 'Quantitative Reasoning II', 
    'Humanities - Lit & Arts': 'Humanities', 
    'Camp Honors/Chanc Schol': 'Camp Honors/Chanc Schol', 
    'Humanities - Hist & Phil': 'Humanities', 
    'Grand Challenge-Health/Well': 'Grand Challenge', 
    'Cultural Studies - Non-West': 'Cultural Studies', 
    'Social & Beh Sci - Soc Sci': 'Social & Beh Sci', 
    'Advanced Composition course': 'Advanced Composition', 
    'Quantitative Reasoning II course': 'Quantitative Reasoning II', 
    'Cultural Studies - US Minority course': 'Cultural Studies', 
    'Social & Beh Sci - Beh Sci course': 'Social & Beh Sci', 
    'Grand Challenge-Sustainability': 'Grand Challenge', 
    'Composition I course': 'Composition I course', 
    'Cultural Studies - US Minority': 'Cultural Studies', 
    'Cultural Studies - Non-West course': 'Cultural Studies', 
    'Humanities - Lit & Arts course': 'Humanities', 
    'Cultural Studies - Western': 'Cultural Studies', 
    'Quantitative Reasoning I course': 'Quantitative Reasoning I course', 
    'Humanities - Hist & Phil course': 'Humanities', 
    'Cultural Studies - Western course': 'Cultural Studies', 
    'James Scholars course': 'James Scholars course', 
    'Grand Challenge-Inequality': 'Grand Challenge'
}

enums_last_level = {
'Nat Sci & Tech': 0,
'Social & Beh Sci': 1,
'Advanced Composition': 2,
'Grand Challenge': 3,
'Camp Honors/Chanc Schol': 4,
'Quantitative Reasoning II': 5,
'Humanities': 6,
'Cultural Studies': 7,
'Composition I course': 8,
'Quantitative Reasoning I course': 9,
'James Scholars course': 10,
}

new_enums = {
    'Social & Behavioral Sciences': 0,
    'Cultural Studies': 1,
    'Humanities & the Arts': 2,
    'Advanced Composition': 3,
    'Quantitative Reasoning': 4,
    'Natural Sciences & Technology': 5,
    'Composition I': 6
}

# combined = pd.read_csv('data/combined-courses-gpas.csv')

# combined['Degree Attributes'] = combined['Degree Attributes'].str.replace('.', '')
# combined['Degree Attributes'] = combined['Degree Attributes'].str.replace(', and', ',')
# combined['Degree Attributes'] = combined['Degree Attributes'].str.split(',')
# combined['Degree Attributes Codes'] = ''

# for i, row in combined.iterrows():
#     value = row["Degree Attributes"]
    
#     if isinstance(value, list):
#         combined.at[i,'Degree Attributes Codes'] = list(map(lambda x: enums_last_level[enums[x.strip()]], value))

# combined = combined[combined["Credit Hours"].str.contains("TO|OR|To|Or|to|or")==False]
# combined["Credit Hours"] = combined["Credit Hours"].str.extract('(\d+)')
# combined = combined[~combined['Description'].str.match(r'Same as.*')]

# combined['Degree Attributes'].fillna(value='[None]', inplace=True)
# combined['Average Grade'].fillna(value=-1.0, inplace=True)
# combined.loc[combined['Degree Attributes Codes'] == '', 'Degree Attributes Codes'] = '[-1]'

# abbrevToFullNameSubjects = getSubjectNamesDict()
# combined['Subject Full Name'] = combined['Subject'].apply(lambda x: abbrevToFullNameSubjects[x])

# combined['Description Vectorized'] = 'The course subject is ' + combined['Subject Full Name'] + '.\n' + 'The course name is ' + combined['Name'] + '.\n' + 'The course is about ' + combined['Description']

# print(combined.shape)
# combined.to_csv("data/final2.csv", index=False)

df = pd.read_csv('fa-2023-courses-with-gpa.csv')

def parse_list(str_list):
    return ast.literal_eval(str_list)

def apply_function(lst):
    return [new_enums[element] for element in lst]

def transform_credit_hours(value):
    value = value.strip().rstrip('.').replace(' OR ', '-').replace(' TO ', '-').replace(' or ', '-').replace(' to ', '-')
    value = value.replace('hours', '')
    if '-' in value:
        print(value)
        x, y = value.split('-')
        credit_options = True
        credit_hours = int((float(x) + float(y)) / 2)
    else:
        credit_options = False
        credit_hours = int(float(value))
    return pd.Series({'Credit Options': credit_options, 'Credit Hours': credit_hours})

# Convert Column to List
df['Degree Attributes'] = df['Degree Attributes'].apply(parse_list)

# Apply numeric mapping to Degree Attrs
df['Degree Attributes'] = df['Degree Attributes'].apply(lambda x: apply_function(x))

# Get rid of NaN in average gpa column
df['Mean Grade'] = df['Mean Grade'].fillna(-1)

df[['Credit Options', 'Credit Hours']] = df['Credit Hours'].apply(transform_credit_hours)

#TODO: Vectorized Description:
df['Description Vectorized'] = 'The course subject is ' + df['Subject'] + '.\n' + 'The course name is ' + df['Name'] + '.\n' + 'The course is about ' + df['Description']

df['Credit Hours'] = df['Credit Hours'] + 7

print(df.head())

df.to_csv('final4.csv', index=False)

# Convert to Json
data_dict = df.to_dict('records')
with open('final4.json', 'w') as f:
    json.dump(data_dict, f)


