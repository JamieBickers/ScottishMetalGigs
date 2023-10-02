import azure.functions as func
import logging

from gigs import get_new_gigs, get_existing_gigs

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="getNewGigs")
def getNewGigs(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        get_new_gigs(),
        mimetype="application/json",
    )

@app.route(route="getExistingGigs")
def getExistingGigs(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        get_existing_gigs(),
        mimetype="application/json",
    )
