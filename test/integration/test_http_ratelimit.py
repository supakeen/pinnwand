import copy
import time
import unittest.mock

import tornado.testing
import tornado.web

from pinnwand import app, configuration, defensive


class RateLimitTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self) -> tornado.web.Application:
        return app.make_application()

    def test_ratelimit_verification_on_endpoints(self):
        with unittest.mock.patch("pinnwand.defensive.should_be_ratelimited") as patch:
            patch.return_value = False

            self.fetch(
                "/",
                method="GET",
            )

            patch.assert_called()
            patch.reset_mock()

    def test_ratelimit_application_on_one_client(self):
        config = configuration.ConfigurationProvider.get_config()
        ratelimlit_copy = copy.deepcopy(config._ratelimit)
        ratelimlit_copy["read"]["capacity"] = 2
        ratelimlit_copy["read"]["consume"] = 2
        ratelimlit_copy["read"]["refill"] = 1

        with unittest.mock.patch.dict("pinnwand.defensive.ConfigurationProvider._config._ratelimit", ratelimlit_copy):
            with unittest.mock.patch.dict("pinnwand.defensive.ratelimit_area", clear=True):
                response = self.fetch(
                    "/",
                    method="GET",
                )

                assert response.code == 200

                response = self.fetch(
                    "/",
                    method="GET",
                )

                assert response.code == 429

    def test_ratelimit_application_on_multiple_clients(self):
        config = configuration.ConfigurationProvider.get_config()
        ratelimlit_copy = copy.deepcopy(config._ratelimit)
        area = "read"
        ratelimlit_copy[area]["capacity"] = 10
        ratelimlit_copy[area]["consume"] = 7
        ratelimlit_copy[area]["refill"] = 1

        ip1 = "192.168.15.32"
        ip2 = "10.45.134.23"

        with unittest.mock.patch.dict("pinnwand.defensive.ConfigurationProvider._config._ratelimit", ratelimlit_copy):
            with unittest.mock.patch.dict("pinnwand.defensive.ratelimit_area", clear=True):
                assert defensive.should_be_ratelimited(ip1, area) is False
                assert defensive.should_be_ratelimited(ip1, area) is True
                assert defensive.should_be_ratelimited(ip2, area) is False
                assert defensive.should_be_ratelimited(ip2, area) is True
                assert defensive.should_be_ratelimited(ip2, area) is True
                time.sleep(10)  # Give it enough time to replenish
                assert defensive.should_be_ratelimited(ip1, area) is False
                assert defensive.should_be_ratelimited(ip2, area) is False

    def test_bucket_tokens_consumption(self):
        config = configuration.ConfigurationProvider.get_config()
        ratelimlit_copy = copy.deepcopy(config._ratelimit)
        area = "read"
        consumption = 7
        capacity = 10
        ratelimlit_copy[area]["capacity"] = capacity
        ratelimlit_copy[area]["consume"] = consumption
        ratelimlit_copy[area]["refill"] = 1

        ip = "192.168.15.32"
        with unittest.mock.patch.dict("pinnwand.defensive.ConfigurationProvider._config._ratelimit", ratelimlit_copy):
            with unittest.mock.patch.dict("pinnwand.defensive.ratelimit_area", clear=True):
                defensive.should_be_ratelimited(ip, area)
                limiter = defensive.ratelimit_area[area]
                tokens_remaining = limiter._storage.get_token_count(ip.encode("utf-8"))
                assert tokens_remaining == capacity - consumption

