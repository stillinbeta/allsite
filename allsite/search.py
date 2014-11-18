from collections import defaultdict
import functools
import itertools
import json


from tornado import gen
import tornado.log
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient

from allsite.util import APIKeys, redis_conn
from allsite import rollbar

DAY_SECS = 60 * 60 * 24
API_URL = 'https://www.googleapis.com/qpxExpress/v1/trips/search?key={}'

logger = tornado.log.gen_log

class SearchHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        # TODO check encoding
        try:
            request = json.loads(str(self.request.body, 'utf8'))
            results = yield self.calculate_cost(request)
            self.finish(json.dumps({'results': results}))
        except:
            logger.error("Oh no :(")
            rollbar.report_error(request=self.request)
            raise

    @gen.coroutine
    def calculate_cost(self, request):
        cities = request['cities']
        members = request['members']
        start_date = request['start_date']
        end_date = request['end_date']

        prices = defaultdict(dict)

        member_airports = {member['airport'] for member in members}
        logger.info(cities)
        all_airports = member_airports | set(cities)

        cost = functools.partial(self.get_roundtrip_cost,
                                 start_date=start_date,
                                 end_date=end_date)

        prices = yield {'{}:{}'.format(orig, dest): gen.maybe_future(cost(orig, dest))
                        for orig, dest in itertools.product(member_airports, all_airports)}

        results = []
        for city in all_airports:
            city_obj = {'city': city, 'total_price': 0, 'result_lines': []}
            for member in members:
                price = prices['{}:{}'.format(member['airport'], city)]
                city_obj['result_lines'].append({'name': member['name'],
                                                 'price': price})
                city_obj['total_price'] += price
            results.append(city_obj)
        results.sort(key=lambda c: c['total_price'])

        return results

    @gen.coroutine
    def get_roundtrip_cost(self, origin, dest, start_date, end_date):
        if origin == dest:
            return 0
        else:
            key = '.'.join([origin.upper(), dest.upper(), start_date, end_date])
            cached = redis_conn.get(key)
            if cached is not None:
                return float(cached)
            ioloop = tornado.ioloop.IOLoop.instance()
            value = yield self.qpx(origin, dest, start_date, end_date)
            redis_conn.set(key, value, DAY_SECS)
            return value

    @gen.coroutine
    def qpx(self, origin, dest, start_date, end_date):
        req = {'request': {
                  "slice": [
                      {'origin': origin,
                       'destination': dest,
                       'date': start_date},
                      {'origin': dest,
                       'destination': origin,
                       'date': end_date}
                  ],
                  "passengers": {
                       "adultCount": 1,
                       "infantInLapCount": 0,
                       "infantInSeatCount": 0,
                       "childCount": 0,
                       "seniorCount": 0
                  },
                  "solutions": 1,
                  "refundable": False,
                  "saleCountry": "US"
               }}
        body = json.dumps(req)
        client = AsyncHTTPClient()
        response = yield client.fetch(
            API_URL.format(APIKeys.get()),
            method='POST',
            headers={'Content-type': 'application/json'},
            body=body
        )
        decoded = json.loads(str(response.body, 'utf8'))
        # https://developers.google.com/qpx-express/v1/trips/search#response
        # trips.tripOption.0.saleTotal will be something like 'USD486.67'
        # The 3: strips this.
        return float(decoded['trips']['tripOption'][0]['saleTotal'][3:])


