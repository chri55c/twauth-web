import json
import os

import uvicorn
from dotenv import load_dotenv
# from flask import Flask, render_template, request, url_for
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# import oauth2 as oauth
from requests_oauthlib import OAuth1Session

# app = Flask(__name__)
app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.debug = False

request_token_url = "https://api.twitter.com/oauth/request_token"
access_token_url = "https://api.twitter.com/oauth/access_token"
authorize_url = "https://api.twitter.com/oauth/authorize"
show_user_url = "https://api.twitter.com/1.1/users/show.json"

# Support keys from environment vars (Heroku).
load_dotenv()
APP_CONSUMER_KEY = os.getenv("APP_CONSUMER_KEY", "API_Key_from_Twitter")
APP_CONSUMER_SECRET = os.getenv("APP_CONSUMER_SECRET", "API_Secret_from_Twitter")


oauth_store = {}


@app.get("/", response_class=HTMLResponse)
def hello(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/start", response_class=HTMLResponse)
def start(request: Request):
    # note that the external callback URL must be added to the whitelist on
    # the developer.twitter.com portal, inside the app settings
    app_callback_url = request.url_for("callback")
    print(f"callback: {app_callback_url}")

    # Generate the OAuth request tokens, then display them
    # consumer = oauth.Consumer(APP_CONSUMER_KEY, APP_CONSUMER_SECRET)
    # client = oauth.Client(consumer)
    # resp, content = client.request(
    #     request_token_url,
    #     "POST",
    #     body=urllib.parse.urlencode({"oauth_callback": app_callback_url}),
    # )
    oauth = OAuth1Session(APP_CONSUMER_KEY, client_secret=APP_CONSUMER_SECRET)
    resp = oauth.fetch_request_token(request_token_url)

    # if resp["status"] != "200":
    #     error_message = "Invalid response, status {status}, {message}".format(
    #         status=resp["status"], message=content.decode("utf-8")
    #     )
    #     # return render_template("error.html", error_message=error_message)
    #     return templates.TemplateResponse(
    #         "error.html", {"request": request, "error_message": error_message}
    #     )

    oauth_token = resp.get("oauth_token")
    oauth_token_secret = resp.get("oauth_token_secret")

    oauth_store[oauth_token] = oauth_token_secret
    return templates.TemplateResponse(
        "start.html",
        {
            "request": request,
            "authorize_url": authorize_url,
            "oauth_token": oauth_token,
            "request_token_url": request_token_url,
        },
    )


@app.get("/callback", response_class=HTMLResponse)
def callback(
    request: Request,
    oauth_token: str,
    oauth_verifier: str,
    oauth_denied: bool = False,
):
    # Accept the callback params, get the token and call the API to
    # display the logged-in user's name and handle

    # if the OAuth request was denied, delete our local token
    # and show an error message
    if oauth_denied:
        if oauth_denied in oauth_store:
            del oauth_store[oauth_denied]
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": "the OAuth request was denied by this user",
            },
        )

    if not oauth_token or not oauth_verifier:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": "callback param(s) missing"},
        )

    # unless oauth_token is still stored locally, return error
    if oauth_token not in oauth_store:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": "oauth_token not found locally"},
        )

    oauth_token_secret = oauth_store[oauth_token]

    # if we got this far, we have both callback params and we have
    # found this token locally
    oauth = OAuth1Session(
        APP_CONSUMER_KEY,
        client_secret=APP_CONSUMER_SECRET,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
        verifier=oauth_verifier,
    )

    access_token = oauth.fetch_access_token(access_token_url)

    screen_name = access_token.get("screen_name")
    user_id = access_token.get("user_id")

    # These are the tokens you would store long term, someplace safe
    real_oauth_token = access_token.get("oauth_token")
    real_oauth_token_secret = access_token.get("oauth_token_secret")

    # Call api.twitter.com/1.1/users/show.json?user_id={user_id}

    oauth = OAuth1Session(
        APP_CONSUMER_KEY,
        client_secret=APP_CONSUMER_SECRET,
        resource_owner_key=real_oauth_token,
        resource_owner_secret=real_oauth_token_secret,
    )
    real_resp = oauth.get(show_user_url + "?user_id=" + user_id)

    if real_resp.status_code != 200:
        error_message = (
            "Invalid response from Twitter API GET users/show: {status}".format(
                status=real_resp.status_code
            )
        )
        return templates.TemplateResponse(
            "error.html", {"request": request, "error_message": error_message}
        )

    response = json.loads(real_resp.content)

    friends_count = response["friends_count"]
    statuses_count = response["statuses_count"]
    followers_count = response["followers_count"]
    name = response["name"]

    # don't keep this token and secret in memory any longer
    del oauth_store[oauth_token]

    return templates.TemplateResponse(
        "callback-success.html",
        {
            "request": request,
            "screen_name": screen_name,
            "user_id": user_id,
            "name": name,
            "friends_count": friends_count,
            "statuses_count": statuses_count,
            "followers_count": followers_count,
            "access_token_url": access_token_url,
        },
    )


# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template("error.html", error_message="uncaught exception"), 500


if __name__ == "__main__":
    uvicorn.run("twauth-web:app", host="0.0.0.0", port=8000)
