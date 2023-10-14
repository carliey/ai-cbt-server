import pandas as pd
import requests


# def get_participants_from_file(attendance_file_url):
#     doc = requests.get(attendance_file_url).content
#     # read the excel file
#     attendance = pd.read_excel(io.BytesIO(doc))
#     records = []
#     for index, row in attendance.iterrows():
#         if isinstance(row[1], int):
#             records.append({'service_number':row[0], 'score':row[1]})
#     return records


def extract_participants_from_excel(excel_file):
    try:
        # Assuming the first row contains column headers like 'id', 'email', 'name'
        df = pd.read_excel(excel_file)
        participants = df.to_dict(orient="records")
        return participants
    except Exception as e:
        return {"error": str(e)}
