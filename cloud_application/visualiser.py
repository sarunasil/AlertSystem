import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from collections import defaultdict
import pandas
import datetime
import requests
import pymongo

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

db_url = "mongodb://localhost:27017/cloud"
client = pymongo.MongoClient(db_url)
db = client.get_database()

users_collection = db["users"]
root_user = users_collection.find_one({"username": "admin"}, {"_id": False})

VALID_CREDENTIALS = [
    [user["username"], user["password"]] for user in users_collection.find({}, {'_id': False})
]
VALID_CREDENTIALS.append([root_user["username"], root_user["password"]])

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_CREDENTIALS
)


def fetch_original_alerts():
    timestamps = defaultdict(list)

    start = datetime.datetime.today().date()
    end = start + datetime.timedelta(days=1)
    delta = int((end - start).total_seconds() / 60)
    start_str = datetime.datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
    end_str = datetime.datetime.strftime(end, "%Y-%m-%d %H:%M:%S")

    response = requests.post("http://localhost:8080/login", json={"username": root_user["username"], "password": root_user["password"]})
    token = response.json()["token"]
    headers = {"Authorization": "Bearer {0}".format(token)}

    response = requests.get("http://localhost:8080/alarms", headers=headers)
    if response.status_code != 200:
        return timestamps, start_str, end_str, delta

    response = response.text
    if response == "":
        return timestamps, start_str, end_str, delta

    for line in response.split("\n"):
        if line == "":
            continue

        data = line.split(" - ", 2)
        if data[1] != "WARNING":
            continue

        timestamps[data[2]].append(data[0])
        start = min(start, datetime.datetime.date(datetime.datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S,%f")))
        end = max(end, datetime.timedelta(days=1) + datetime.datetime.date(datetime.datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S,%f")))

    delta = int((end - start).total_seconds() / 60)
    start_str = datetime.datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
    end_str = datetime.datetime.strftime(end, "%Y-%m-%d %H:%M:%S")

    return timestamps, start_str, end_str, delta


def update_alerts_graph():
    all_original_alerts, start_str, end_str, delta = fetch_original_alerts()
    all_timestamps_values = {}
    timestamps = pandas.date_range(start=start_str, end=end_str, periods=delta + 1)
    max_timestamp_value = 0

    for identifier in all_original_alerts:
        original_alerts = all_original_alerts[identifier]
        timestamps_values = {str(timestamp): 0 for timestamp in timestamps}

        for alert_timestamp in original_alerts:
            original_timestamp = datetime.datetime.strptime(alert_timestamp, "%Y-%m-%d %H:%M:%S,%f")
            closest_timestamp = datetime.datetime(year=original_timestamp.year, month=original_timestamp.month, day=original_timestamp.day,
                                                  hour=original_timestamp.hour, minute=original_timestamp.minute)

            closest_timestamp = str(closest_timestamp)
            timestamps_values[closest_timestamp] += 1
            max_timestamp_value = max(max_timestamp_value, timestamps_values[closest_timestamp])

        all_timestamps_values[identifier] = timestamps_values

    return all_timestamps_values, start_str, end_str, max_timestamp_value


def update_graph():

    all_timestamps_values, start_str, end_str, max_timestamp_value = update_alerts_graph()

    return html.Div(children=[
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': list(timestamps_values.keys()), 'y': list(timestamps_values.values()), 'type': 'scatter', 'name': identifier} for identifier, timestamps_values in all_timestamps_values.items()
                ],
                'layout': {
                    'title': 'Alarm Messages Visualisation',
                    'xaxis': {"range": [start_str, end_str]},
                    'yaxis': {"range": [0, max_timestamp_value]}
                }
            }
        )
    ])


app.layout = update_graph

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
