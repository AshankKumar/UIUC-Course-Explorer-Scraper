"""
This script scrapes data based on the provided term and year.
You can also set the rate limit for requests.

Usage:
python scraper.py <term> <year> --rate_limit <rate_limit>
"""

from collections import defaultdict
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import requests
import time
import json
import argparse

# TODO add exponential backoff
# TODO write to disk in chunks while iterating instead of all at once at the end
# TODO add options for csv
def scrape(term, year, rate_limit):
    url = f'https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{term}.xml'
    response = requests.get(url)

    if response.status_code == 404:
            print(f"Error: The URL '{url}' does not exist. Please check your term and year.")
            sys.exit(1)

    soup = BeautifulSoup(response.content, 'lxml-xml')

    subject_tags = soup.find_all('subject')
    subjects = []
    for tag in subject_tags:
        major_id = tag['id']
        subjects.append(major_id)

    courses_dictionary = defaultdict(defaultdict)
    print("Getting Pages for Majors") # http://courses.illinois.edu/cisapp/explorer/catalog/:year/:semester/:subjectCode
    for major_id in (pbar := tqdm(subjects, unit="major")):
        pbar.set_description(f'Processing {major_id}')
        response = requests.get(f'http://courses.illinois.edu/cisapp/explorer/catalog/{year}/{term}/{major_id}.xml')
        soup = BeautifulSoup(response.content, 'lxml-xml')
        major_name = soup.find('label').text
        courses = soup.find_all('course')
        courses_dictionary[major_id] = {'major_name': major_name, 'courses': [course['href'] for course in courses]}
        time.sleep(rate_limit)  
    print("Finishsed getting pages for majors\n")

    print("Getting Courses for each Major")
    data = []

    total_courses = sum(len(subject_object['courses']) for subject_object in courses_dictionary.values())
    pbar = tqdm(total=total_courses, desc="Processing courses", unit="course")

    for major_id, subject_object in courses_dictionary.items():
        major_name = subject_object['major_name']
        courses = subject_object['courses']
        pbar.set_description(f'Processing {major_name}')
        for c in courses:
            try:
                response = requests.get(c) #http://courses.illinois.edu/cisapp/explorer/schedule/:year/:semester/:subjectCode/:courseNumber
                soup = BeautifulSoup(response.content, 'lxml-xml')

                attributes = []
                genEdCategories = soup.find('genEdCategories')
                if genEdCategories:
                    attributes = [a.text for a in genEdCategories.find_all('description')]
                attributes = sorted(attributes)

                description = soup.description.text
                credit_hours = soup.creditHours.text
                course_name = soup.label.text
                course_number = c.rsplit('/', 1)[-1].split('.')[0]

                new_entry = {'Major': major_name, 'Major Abbreviation': major_id, 'Course Number': course_number, 'Course Name': course_name, 'Description': description, 'Credit Hours': credit_hours, 'Degree Attributes': attributes}
                data.append(new_entry)

                time.sleep(rate_limit)
            except Exception as e:
                tqdm.write(str(e))
                tqdm.write(c)
            pbar.update()   

    pbar.close()
    print("Finished getting courses for each major")
                
    with open(f'{term}-{year}.json', 'w') as f:
        json.dump(data, f, indent=4)

def valid_year(string):
    """Check if string is a valid year between 1900 and two years in the future from the current year."""
    future_year = datetime.now().year + 2
    if not string.isdigit() or int(string) < 1900 or int(string) > future_year:
        message = f"Invalid year: '{string}'. Year must be between 1900 and {future_year}."
        raise argparse.ArgumentTypeError(message)
    return int(string)

def parse_args():
    parser = argparse.ArgumentParser(description='Scraper script.')
    
    parser.add_argument('term', type=str, choices=['fall', 'spring', 'winter', 'summer'], 
                        help='Term in the form: fall, spring, winter, summer.')
    
    parser.add_argument('year', type=valid_year, help='Year in the form: YYYY.')
    
    parser.add_argument('--rate_limit', type=float, default=0.1, 
                        help='Optional argument to dictate the time slept in between each request in seconds. A tenth of a second is used by default.')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    term = args.term
    year = args.year
    rate_limit = args.rate_limit

    scrape(term, year, rate_limit)