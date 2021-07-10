from re import sub

from flask import Flask, request, Response
from prometheus_client import make_wsgi_app, Gauge, Info
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/metrics": make_wsgi_app()
})

metrics = {}


def to_snake_case(name):
    name = sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = sub('__([A-Z])', r'_\1', name)
    name = sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def pars_data(data_name: str, data_value, operation_name: str, backup_name: str):
    if isinstance(data_value, dict):
        for dd, vv in data_value.items():
            pars_data(f"{data_name}_{dd}", vv, operation_name, backup_name)
    else:
        set_metric(data_name, data_value, operation_name, backup_name)


def set_metric(name: str, value, operation_name: str, backup_name: str):
    metric_name = to_snake_case(name)

    if name not in metrics:
        if isinstance(value, int):
            metrics[name] = Gauge(metric_name, name, ["operation", "name"])
        elif isinstance(value, str) or isinstance(value, bool):
            metrics[name] = Info(metric_name, name, ["operation", "name"])
        else:
            return

    m = metrics[name]
    if isinstance(m, Gauge):
        m.labels(operation_name, backup_name).set(value)
    elif isinstance(m, Info):
        m.labels(operation_name, backup_name).info({"data": value})


@app.route("/report", methods=["POST"])
def report() -> Response:
    request.get_json()

    operation_name = request.json["Extra"]["OperationName"]
    backup_name = request.json["Extra"]["backup-name"]

    pars_data("duplicati", request.json["Data"], operation_name, backup_name)

    return Response("Ok", 200)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=80)
