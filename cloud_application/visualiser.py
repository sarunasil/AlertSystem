import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import pandas
import datetime
import requests
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

VALID_CREDENTIALS = [
    [os.environ["JWT_USER"], os.environ["JWT_PASSWORD"]]
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_CREDENTIALS
)


def fetch_original_alerts():

    timestamps = []

    response = requests.post("http://localhost:8080/login", json={"username": os.environ["JWT_USER"], "password": os.environ["JWT_PASSWORD"]})
    token = response.json()["token"]
    headers = {"Authorization": "Bearer {0}".format(token)}

    response = requests.get("http://localhost:8080/alarms", headers=headers)
    if response.status_code != 200:
        return timestamps

    response = response.text
    if response == "":
        return timestamps

    for line in response.split("\n"):
        if line == "":
            continue

        data = line.split(" - ", 2)
        if data[1] != "WARNING":
            continue

        timestamps.append(data[0])

    return timestamps


def update_alerts_graph():

    original_alerts = fetch_original_alerts()

    start = datetime.datetime.today().date()
    end = start + datetime.timedelta(days=1)

    if len(original_alerts) > 0:
        start = min(start, datetime.datetime.date(datetime.datetime.strptime(original_alerts[0], "%Y-%m-%d %H:%M:%S,%f")))
        end = max(end, datetime.timedelta(days=1) + datetime.datetime.date(datetime.datetime.strptime(original_alerts[-1], "%Y-%m-%d %H:%M:%S,%f")))

    delta = int((end - start).total_seconds() / 60)
    start_str = datetime.datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
    end_str = datetime.datetime.strftime(end, "%Y-%m-%d %H:%M:%S")

    timestamps = pandas.date_range(start=start_str, end=end_str, periods=delta + 1)
    timestamps_values = {str(timestamp): 0 for timestamp in timestamps}

    for timestamp in original_alerts:
        original_timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
        closest_timestamp = datetime.datetime(year=original_timestamp.year, month=original_timestamp.month, day=original_timestamp.day,
                                              hour=original_timestamp.hour, minute=original_timestamp.minute)

        closest_timestamp = str(closest_timestamp)
        timestamps_values[closest_timestamp] += 1

    return timestamps_values, start_str, end_str


def update_graph():

    timestamps_values, start_str, end_str = update_alerts_graph()

    x_values = list(timestamps_values.keys())
    y_values = list(timestamps_values.values())

    return html.Div(children=[
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': x_values,
                     'y': y_values, 'type': 'scatter'},
                ],
                'layout': {
                    'title': 'Alarm Messages Visualisation',
                    'xaxis': {"range": [start_str, end_str]},
                    'yaxis': {"range": [min(y_values), max(y_values)]}
                }
            }
        )
    ])


app.layout = update_graph

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
