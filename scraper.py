import sys
from bs4 import BeautifulSoup
import requests
from collections import defaultdict
import time
import json
import pandas as pd

def scrape(term, year, rate_limit=1):
    url = f'https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{term}.xml'
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
    print ("Getting Pages for Subjects")
    for subject_id, href in subjects:
        response = requests.get(href)
        soup = BeautifulSoup(response.content, 'lxml-xml')
        subject_name = soup.find('label').text
        courses = soup.find_all('course')
        courses_dictionary[subject_id] = {'subject_name': subject_name, 'courses': [course['href'] for course in courses]}
        print(f'{i}/{len(subjects)}')
        i += 1
        time.sleep(rate_limit)
        break

    print ("Getting Courses for each Subject")
    data = []
    for subject_id, subject_object in courses_dictionary.items():
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

                time.sleep(rate_limit)
                i += 1
            except Exception as e:
                print(e)
                print(c)
        break
    df = pd.DataFrame(data, columns = ['Subject', 'Subject Abbreviation', 'Course', 'Name', 'Description', 'Credit Hours', 'Degree Attributes'])
    df.to_csv(f"{term}-{year}-courses.csv", index=False)





if __name__ == "__main__":
    num_args = len(sys.argv) - 1

    if (num_args == 2):
        term = sys.argv[1]
        year = sys.argv[2]
        scrape(term, year)