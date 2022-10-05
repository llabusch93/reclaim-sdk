from httpx import Client
from os import environ
import pathlib
import toml

CONF_FILE = pathlib.Path("~/.reclaimai.toml").expanduser()


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

    def __init__(self, **kwargs):
        super().__init__(base_url=self._api_url, http2=True)

        if "token" in kwargs:
            self._token = kwargs["token"]

        elif "RECLAIM_TOKEN" in environ:
            self._token = environ["RECLAIM_TOKEN"]

        elif CONF_FILE.exists():
            config = toml.load(CONF_FILE)
            self._token = config["reclaim_ai"]["token"]

        if self._token:
            self.authenticate(self._token)

    def authenticate(self, token):
        """
        Authenticate the client with the given token.
        """
        self.cookies.set("RECLAIM", self._token)
