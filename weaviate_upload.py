import weaviate
import json
import requests

API_URL = "https://uac5lhb2yub711ud.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
  "Authorization": "Bearer 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",
}

def get_client():
    resource_owner_config = weaviate.AuthClientPassword(
    username = "ashankkumar01@gmail.com", 
    password = "ThisIsDumb@1", 
    scope = "offline_access"
    )
    
    return weaviate.Client(
    url = "https://smartcoursesearch2.weaviate.network",
    auth_client_secret=resource_owner_config,
    )


def get_vector(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def batch_get_vector(start, end, data):

    descriptions = [data[i]['Description Vectorized'] for i in range(start, end)]
    import time
    start = time.time()
    print('started')
    output = get_vector({"inputs":descriptions})['embeddings']
    print(time.time()-start)
    print(len(output))
    print(len(output[0]))
    return output

def upload_data():
    client.schema.delete_class("Course")

    class_obj = {
        "class": "Course",
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
            "name": "degree_attrs_codes",
            },
            {
            "dataType": [
                "text"
            ],
            "description": "Full subject name",
            "name": "full_subject",
            }
        ]
    }

    client.schema.create_class(class_obj)

    data = ''
    with open('data/final.json', 'r') as j:
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
                "degree_attrs": d["Degree Attributes"],
                "avg_grade": d["Mean Grade"],
                "degree_attrs_codes": d["Degree Attributes Codes"],
                "full_subject": d["Subject"]
            }


            client.batch.add_data_object(properties, "Course", vector = embeddings_array[i%100])

client = get_client()

print("client")
upload_data()
print("done")




while True:
    input_str = input()
    vector = get_vector({"inputs":input_str})['embeddings']

    result = (
        client.query
        .get("Course", ["subject", "course", "vectorized_description", "degree_attrs", "degree_attrs_codes"])
        # .with_additional(['certainty'])
        # .with_where(where_filter)
        # .with_near_text(nearText)
        .with_near_vector({"vector":vector})
        .with_limit(10)
        .do()
    )
    print(json.dumps(result, indent=4))


