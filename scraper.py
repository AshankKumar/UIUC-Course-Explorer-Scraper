import sys
from bs4 import BeautifulSoup
import requests
from collections import defaultdict
import time
import json
import pandas as pd

def scrape(term, year):
    # url = f'https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{term}.xml'
    url = 'https://courses.illinois.edu/cisapp/explorer/schedule/2023/fall.xml'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml-xml')

    subject_tags = soup.find_all('subject')
    subjects = []
    for tag in subject_tags:
        subject_id = tag['id']
        href = tag['href']
        subjects.append((subject_id, href))
    
    courses_dictionary = defaultdict(defaultdict)
    i = 1
    for subject_id, href in subjects:
        response = requests.get(href)
        soup = BeautifulSoup(response.content, 'lxml-xml')
        subject_name = soup.find('label').text
        courses = soup.find_all('course')
        courses_dictionary[subject_id] = {'subject_name': subject_name, 'courses': [course['href'] for course in courses]}
        print(f'{i}/{len(subjects)}')
        i += 1
        time.sleep(1)

    with open("subjects_and_courses.json", "w") as f:
        json.dump(courses_dictionary, f)

def scrape_with_provided_json(json_file):
    with open(json_file, "r") as f:
        subject_dict = json.load(f)

    # df = pd.DataFrame(columns=['Subject', 'Subject Abbreviation', 'Course', 'Name', 'Description', 'Credit Hours', 'Degree Attributes'])
    # data = ['Subject', 'Subject Abbreviation', 'Course', 'Name', 'Description', 'Credit Hours', 'Degree Attributes']
    data = []
    for subject_id, subject_object in subject_dict.items():
        print(f"Processing: {subject_id}")
        subject_name = subject_object['subject_name']
        courses = subject_object['courses']
        i = 1
        for c in courses:
            try:
                print(f'{subject_id}: {i}/{len(courses)}')
                response = requests.get(c)
                soup = BeautifulSoup(response.content, 'lxml-xml')

                attributes = []
                genEdCategories = soup.find('genEdCategories')
                if genEdCategories:
                    attributes = [a.text for a in genEdCategories.find_all('description')]

                description = soup.description.text
                credit_hours = soup.creditHours.text
                course_name = soup.label.text
                course_number = c.rsplit('/', 1)[-1].split('.')[0]

                new_row = [subject_name, subject_id, course_number, course_name, description, credit_hours, attributes]
                data.append(new_row)

                time.sleep(1)
                i += 1
            except Exception as e:
                print(e)
                print(c)
        
    df = pd.DataFrame(data, columns = ['Subject', 'Subject Abbreviation', 'Course', 'Name', 'Description', 'Credit Hours', 'Degree Attributes'])
    df.to_csv("fa-2023-courses.csv", index=False)





if __name__ == "__main__":
    num_args = len(sys.argv) - 1

    if (num_args == 1):
        scrape_with_provided_json(sys.argv[1])
    elif (num_args == 2):
        term = sys.argv[1]
        year = sys.argv[2]
        scrape(term, year)