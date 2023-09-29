import azure.functions as func
import logging
import json

from gigs import get_gigs

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="getGigs")
def getGigs(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # return func.HttpResponse(
    #     json.dumps(get_gigs()),
    #     mimetype="application/json",
    # )

    return func.HttpResponse(
        json.dumps("test"),
        mimetype="application/json",
    )