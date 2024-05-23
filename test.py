from model import Rental
import json


with open("data/1/report.json", "r") as fp:
    inputs = json.load(fp)


inputs = {
    k.replace(" ", "_").replace("(", "").replace(")", "").lower(): v 
    for k, v in inputs.items()
}
rental = Rental(**inputs)