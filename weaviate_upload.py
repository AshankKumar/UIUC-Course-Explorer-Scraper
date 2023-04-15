import weaviate
import json
import requests
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    




def get_vector(text):
    return MODEL.encode(text)

def batch_get_vector(start, end, data):

    descriptions = [data[i]['Description Vectorized'] for i in range(start, end)]
    import time
    start = time.time()
    print('started')
    output = get_vector(descriptions)
    print(time.time()-start)
    print(len(output))
    print(len(output[0]))
    return output

def upload_data():
    client.schema.delete_class("Uiuc_course_search")

    class_obj = {
        "class": "Uiuc_course_search",
        "vectorizer": "none",  
        "properties": [
            {
            "dataType": [
                "string"
            ],
            "description": "Subject or department of said course",
            "name": "subject",
            },
            {
            "dataType": [
                "int"
            ],
            "description": "Course number",
            "name": "course",
            },
            {
            "dataType": [
                "string"
            ],
            "description": "Course name",
            "name": "name",
            },
            {
            "dataType": [
                "text"
            ],
            "description": "Course description",
            "name": "description",
            },
            {
            "dataType": [
                "int"
            ],
            "description": "Course credit hours",
            "name": "credit_hours",
            },
            {
            "dataType": [
                "number"
            ],
            "description": "Course's average gpa",
            "name": "avg_grade",
            },
            {
            "dataType": [
                "int[]"
            ],
            "description": "Numerical representation of a course's degree attrs",
            "name": "degree_attrs",
            },
            {
            "dataType": [
                "text"
            ],
            "description": "Full subject name",
            "name": "full_subject",
            },
            {
            "dataType": [
                "boolean"
            ],
            "description": "Boolean to indicate if there are multiple credit hour options",
            "name": "credit_hour_options",
            }
        ]
    }

    client.schema.create_class(class_obj)

    data = ''
    with open('final4.json', 'r') as j:
        data = json.loads(j.read())

    with client.batch as batch:
        batch.batch_size=100
        embeddings_array = []
        for i, d in enumerate(data):
            if i%100 == 0:
                embeddings_array = batch_get_vector( i, min(i+100, len(data)), data)
            print(f"importing course: {i+1}")

            properties = {
                "subject": d["Subject Abbreviation"],
                "course": d["Course"],
                "name": d["Name"],
                "description": d["Description"],
                "credit_hours": d["Credit Hours"],
                "avg_grade": d["Mean Grade"],
                "degree_attrs": d["Degree Attributes"],
                "full_subject": d["Subject"],
                "credit_hour_options": d["Credit Options"]
            }


            client.batch.add_data_object(properties, "Uiuc_course_search", vector = embeddings_array[i%100])

client = get_client()

print("client")
upload_data()
print("done")


while True:
    input_str = input()
    vector = get_vector(str(input_str))

    where_filter = {  
        "path": ["credit_hours"],
        "operator": "Equal",
        "valueInt": 7
    }

    result = (
        client.query
        .get("Uiuc_course_search", ["subject", "course", "description", "degree_attrs", "credit_hours"])
        .with_near_vector({"vector":vector})
        .with_where(where_filter)
        .with_limit(3)
        .do()
    )
    print(json.dumps(result, indent=4))


