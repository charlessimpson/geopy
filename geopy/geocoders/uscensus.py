from geopy.compat import urlencode
from geopy.geocoders.base import DEFAULT_SENTINEL, Geocoder
from geopy.location import Location
from geopy.util import logger

__all__ = ("USCensus", )


class USCensus(Geocoder):
    """Geocoder using the US Census Geocoding Service API.

    Documentation at:
        https://www.census.gov/geo/maps-data/data/geocoder.html

    .. versionadded:: 1.20.0
    """

    structured_query_params = {
        'city',
        'state',
        'street',
        'zip',
    }

    geocode_path = '/geocoder/locations/onelineaddress'
    geocode_structured_path = '/geocoder/locations/address'

    def __init__(
            self,
            domain='geocoding.geo.census.gov',
            format_string=None,
            scheme=None,
            timeout=DEFAULT_SENTINEL,
            proxies=DEFAULT_SENTINEL,
            user_agent=None,
            ssl_context=DEFAULT_SENTINEL,
            benchmark='Public_AR_Current',
    ):
        """

        :param str domain: Defaults to ``'geocoding.geo.census.gov'``, can
            be changed for testing purposes.

        :param str format_string:
            See :attr:`geopy.geocoders.options.default_format_string`.

        :param str scheme:
            See :attr:`geopy.geocoders.options.default_scheme`.

        :param int timeout:
            See :attr:`geopy.geocoders.options.default_timeout`.

        :param dict proxies:
            See :attr:`geopy.geocoders.options.default_proxies`.

        :param str user_agent:
            See :attr:`geopy.geocoders.options.default_user_agent`.

        :type ssl_context: :class:`ssl.SSLContext`
        :param ssl_context:
            See :attr:`geopy.geocoders.options.default_ssl_context`.

        :param str benchmark: numerical ID or name that references what version
            of the locator should be searched. The general format of the name
            is ``DatasetType_SpatialBenchmark``, defaults to
            ``Public_AR_Current``.

        """
        super(USCensus, self).__init__(
            format_string=format_string,
            scheme=scheme,
            timeout=timeout,
            proxies=proxies,
            user_agent=user_agent,
            ssl_context=ssl_context,
        )
        self.domain = domain.strip('/')
        self.benchmark = benchmark

        self.geocode_api = (
            '%s://%s%s' % (self.scheme, self.domain, self.geocode_path)
        )
        self.geocode_structured_api = (
            '%s://%s%s' % (self.scheme, self.domain, self.geocode_structured_path)
        )

    def geocode(
            self,
            query,
            exactly_one=True,
            timeout=DEFAULT_SENTINEL,
    ):
        """
        Return a location point by address.

        :param str query: The address or query you wish to geocode.

            For a structured query, provide a dictionary whose keys
            are one of: `city`, `state`, `street`, `zip`. Not all prats need to
            be specified.

        :param int timeout: Time, in seconds, to wait for the geocoding service
            to respond before raising a :class:`geopy.exc.GeocoderTimedOut`
            exception. Set this only if you wish to override, on this call
            only, the value set during the geocoder's initialization.

        :param bool exactly_one: Return one result or a list of results, if
            available.

        :rtype: ``None``, :class:`geopy.location.Location` or a list of them, if
            ``exactly_one=False``.

        """

        if isinstance(query, dict):
            params = {
                key: val
                for key, val
                in query.items()
                if key in self.structured_query_params
            }
            api = self.geocode_structured_api
        else:
            params = {
                'address': self.format_string % query,
            }
            api = self.geocode_api

        params['benchmark'] = self.benchmark
        params['format'] = 'json'

        url = "?".join((api, urlencode(params)))

        logger.debug("%s.geocode: %s", self.__class__.__name__, url)
        return self._parse_json(
            self._call_geocoder(url, timeout=timeout), exactly_one
        )

    @staticmethod
    def _parse_match(match):
        latitude = match.get('coordinates', {}).get('y')
        longitude = match.get('coordinates', {}).get('x')
        address = match.get('matchedAddress')

        return Location(address, (latitude, longitude), match)

    @classmethod
    def _parse_json(self, response, exactly_one):
        if response is None or 'result' not in response or \
                'addressMatches' not in response['result']:
            return None
        matches = response['result']['addressMatches']
        if not len(matches):
            return None
        if exactly_one:
            return self._parse_match(matches[0])
        else:
            return [self._parse_match(match) for match in matches]
