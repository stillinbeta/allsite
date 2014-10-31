# Allsite
Want to have an Onsite? Where's the cheapest place to put it? Let's find out!

# Setup

`pip install -r requirements.txt`

Add the following to your .env:

* `GOOGLE_API_KEYS`: comma-seperated API keys. More than one will be round-robin chosen.
* `REDIS_URL`: probably `redis://localhost` locally.

## KEEP IN MIND:

free quota is only 50 requests/day :( Requests are cached between queries, however.

# To deploy to heroku:

* Add a redis addon, make sure it specifies `REDIS_URL`
* Create a heroku app
* `heroku config:set GOOGLE_API_KEYS=<key1>,<key2>`
* `git push heroku master`
