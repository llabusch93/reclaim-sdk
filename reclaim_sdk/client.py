import pathlib
from os import environ

import toml
from httpx import Client, HTTPStatusError
from reclaim_sdk.exceptions import RecordNotFound, InvalidRecord

CONF_FILE = pathlib.Path("~/.reclaim.toml").expanduser()


class ReclaimClient(Client):
    """
    The client is a singleton, so we can use it to store the token and
    the API URL. It should be initialized in the main script once.
    """

    _instance = None
    _token = None
    _api_url = "https://api.app.reclaim.ai"

    @property
    def is_authenticated(self):
        return "RECLAIM" in self.cookies

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, token="", **kwargs):
        super().__init__(base_url=self._api_url, http2=True)

        if token:
            self._token = token

        elif "RECLAIM_TOKEN" in environ:
            self._token = environ["RECLAIM_TOKEN"]

        elif CONF_FILE.exists():
            try:
                self._token = toml.load(CONF_FILE)["reclaim_ai"]["token"]
            except KeyError:
                raise KeyError(f"Token not found in {CONF_FILE}.")

        if self._token:
            self.authenticate(self._token)

        else:
            raise ValueError("No Reclaim.ai token provided.")

    def authenticate(self, token):
        """
        Authenticate the client with the given token.
        """
        self.cookies.set("RECLAIM", self._token)


class ReclaimAPICall(object):
    """
    Context manager for API calls to Reclaim.ai.
    It will catch any HTTPError and raise a ReclaimAPIError instead.
    """

    def __init__(self, object, id=None, **kwargs):
        """
        Initialize the API call context manager.

        :param object (ReclaimModel): The object to call the API on.
        :param id (int): The ID of the object to call the API on.
        :param kwargs: Additional keyword arguments to pass to the client.
        """
        self.object = object
        self.object_id = id
        self.client = ReclaimClient(**kwargs)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_value, traceback):

        if exc_type is HTTPStatusError:

            if exc_value.response.status_code == 404:
                if self.object_id is not None:
                    id = self.object_id
                else:
                    id = self.object.id
                raise RecordNotFound(
                    f"{self.object._name} with ID {id} not found."
                )

            elif exc_value.response.status_code in (400, 422, 500):
                raise InvalidRecord(
                    f"The submitted {self.object._name} is invalid."
                )

            else:
                raise exc_value
