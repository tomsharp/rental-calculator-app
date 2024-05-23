import json
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
import plotly.io as pio

from model import Rental
from process import split_df_into_report_tables, process_report_table


app = Flask(__name__)


def _map_types(x):
    return {
        "number": "decimal",
        "integer": "number",
    }[x]


def load_metadata():
    return


def load_metadata():
    with open("data/metadata.json", "r") as fp:
        return json.load(fp)


def load_report(metadata):
    with open(metadata["location"], "r") as fp:
        return json.load(fp)


def save_report(rental: Rental, name) -> str:
    p = Path(f"data/{name}")
    p.mkdir(parents=True, exist_ok=True)
    path_to_file = p / "report.json"
    with open(path_to_file, "w") as fp:
        json.dump(rental.model_dump(), fp)
    return str(path_to_file)


def update_metadata(report_metadata):
    metadata = load_metadata()
    metadata.append(report_metadata)
    with open("data/metadata.json", "w") as fp:
        json.dump(metadata, fp)


@app.route("/")
def landing_page():
    metadata = load_metadata()
    return render_template("landing.html", reports=metadata)


@app.route("/report", methods=["POST"])
def report():
    selected_report = request.form["report"]
    return redirect(url_for("show_report", report_name=selected_report))


@app.route("/show_report/<report_name>")
def show_report(report_name):

    metadata = load_metadata()
    selected_report_metadata = [i for i in metadata if i["name"] == report_name][0]

    inputs = load_report(selected_report_metadata)

    inputs = {
        k.replace(" ", "_").replace("(", "").replace(")", "").lower(): v
        for k, v in inputs.items()
    }
    rental = Rental(**inputs)

    df = pd.DataFrame([rental.model_dump()])
    tables = split_df_into_report_tables(df)
    tables = [process_report_table(t) for t in tables]

    return render_template("report.html", report_name=report_name, tables=tables)


def _report_builder_input_fields():
    metadata = [
        {"label": "Report Name:", "id": "name", "type": "text", "required": True},
        {
            "label": "Report Description:",
            "id": "description",
            "type": "text",
            "required": False,
        },
    ]
    properties = [
        {
            "id": k,
            "label": v["title"],
            "type": _map_types(v["type"]),
            "required": True,
        }
        for k, v in Rental.schema()["properties"].items()
    ]
    input_fields = metadata + properties
    return input_fields


@app.route("/report_builder", methods=["GET", "POST"])
def report_builder():

    input_fields = _report_builder_input_fields()


    if request.method != "POST":
        return render_template("report_builder.html", input_fields=input_fields)

    # button push
    report_data = request.form
    rental = Rental(**report_data)
    
    # Check if the report name already exists
    metadata = load_metadata()
    existing_report_names = [item["name"] for item in metadata]
    if report_data["name"] in existing_report_names:
        # Render the report_builder.html template with an error message
        error_message = "Report name already exists. Please choose a different name."
        return render_template("report_builder.html", input_fields=input_fields, error_message=error_message, **report_data)

    try:
        rental = Rental(**report_data)
    except Exception as e:
        raise Exception(f"Error saving report, error: {e}")
    try:
        report_location = save_report(rental, report_data["name"])
    except Exception as e:
        raise Exception(f"Cannot save report, error: {e}")
    report_metadata = {
        "name": report_data["name"],
        "description": report_data["description"],
        "location": report_location,
    }
    try:
        update_metadata(report_metadata)
    except Exception as e:
        raise Exception(f"Cannot save metadata, error: {e}")

    return redirect(url_for("show_report", report_name=report_data["name"]))


@app.route("/edit_report/<report_name>", methods=["GET", "POST"])
def edit_report(report_name):
    # Load metadata to retrieve report details
    metadata = load_metadata()

    # Find the selected report
    selected_report_metadata = [r for r in metadata if r["name"] == report_name][0]

    if request.method == "POST":
        # Handle form submission to update the report details
        updated_report_data = request.form
        print(updated_report_data)
        rental = Rental(**updated_report_data)
        
        # Update the report metadata
        save_report(rental, selected_report_metadata['name'])
        
        # Redirect to the updated report page
        return redirect(url_for("show_report", report_name=report_name))

    # Pre-fill the form fields with the current report details
    input_fields = []
    report = load_report(selected_report_metadata)
    for k, v in Rental.schema()["properties"].items():
        input_fields.append({"label": v["title"], "id": k, "type": _map_types(v["type"]), "value": report[k]})

    return render_template("edit_report.html", report_name=report_name, input_fields=input_fields)


if __name__ == "__main__":
    app.run(debug=True)
