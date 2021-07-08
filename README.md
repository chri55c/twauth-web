# twauth-web

A simple Python + FastAPI web app that demonstrates the flow of obtaining a [Twitter user OAuth access token](https://developer.twitter.com/en/docs/basics/authentication/overview/oauth).

This is a fork of [twitterdev/twauth-web](https://github.com/twitterdev/twauth-web) with the following changes:

- FastAPI instead of Flask
- uvicorn instead of gunicorn
- Poetry instead of Pipenv
- .env instead of .cfg (to work with `load_dotenv()`)
- requests-oauthlib instead of python-oauth2

## Setup

1. Obtain consumer key and secret from the Twitter Developer portal. The app should be configured to enable Sign in with Twitter. See `twauth-web.py` for more details, but you can either:
   1. add these values to a `.env` file (local deployment); or
   2. set environment variables `APP_CONSUMER_KEY` and `APP_CONSUMER_SECRET` (cloud deployment)
2. Setup a [Poetry](https://python-poetry.org/) environment, and install dependencies:
   1. `poetry install`
   2. `poetry shell`
3. Start the app:
   1. `python ./twauth-web.py`; or
   2. `uvicorn twauth-web:app`

> Note: the app must have an Internet-accessible URL - do not attempt to connect via localhost, as this will not work. You can run a tunnel e.g. `ngrok` for local use, or deploy to a cloud platform such as Heroku (a `Procfile` is included).

Open a browser window on your demo app's external URL. Don't click the buttons yet!

Finally, revisit the dev portal, and add your app's callback URL (`https://your-deployed-url/callback`) to the callback URL whitelist setting. Once saved, follow the instructions on the app's web UI to click through the demo pages.

## Reference

[Twitter Developer Portal](https://developer.twitter.com/)

[FastAPI](https://fastapi.tiangolo.com/)

[Requests-OAuthlib](https://requests-oauthlib.readthedocs.io/en/latest/oauth1_workflow.html)

[Bootstrap](https://getbootstrap.com/)

### Credits

Original version by Jacob Petrie

https://twitter.com/jaakkosf

https://github.com/jaakko-sf/twauth-web
