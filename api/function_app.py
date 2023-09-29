import azure.functions as func
import logging
import json

#from gigs import get_gigs
def get_gigs():
    return "dfrghdf"

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="getGigs")
def getGigs(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        return func.HttpResponse(
            json.dumps(get_gigs()),
            mimetype="application/json",
        )
    except Exception as e:
        return func.HttpResponse(
            "test",
            mimetype="application/json",
        )

    # return func.HttpResponse(
    #     json.dumps("test"),
    #     mimetype="application/json",
    # )