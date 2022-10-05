from reclaimai_sdk.client import ReclaimClient
from contextlib import contextmanager


class ReclaimModel(object):
    """
    This is the base model for any storable object on Reclaim.ai. It implements
    the basic CRUD operations.
    """

    _endpoint = None
    _name = None
    _required_fields = []
    _client = ReclaimClient()
    _default_params = {}

    def __repr__(self) -> str:
        return f"{self._name} ({self.id} - {self.name})"

    def __str__(self) -> str:
        return f"{self.name}"

    def __init__(self, id: int = None, data: dict = {}, **kwargs) -> None:
        self._data = data
        self.autosave = kwargs.get("autosave", True)

    def __getitem__(self, key):
        return self._data.get(key, None)

    def __setitem__(self, key, value):
        """
        Set a value in the data dictionary and sync the object.
        """
        self._data[key] = value
        if self.autosave:
            self.save()

    def __delitem__(self, key):
        """
        Delete a key from the data dictionary and sync the object.
        """
        del self._data[key]
        if self.autosave:
            self.save()

    @classmethod
    def query_params(cls, **kwargs):
        """
        Return the query parameters for the API call.
        """
        params = {}
        params.update(kwargs)
        params.update(cls._default_params)
        return params

    @property
    def name(self):
        raise NotImplementedError()

    @name.setter
    def name(self, value):
        raise NotImplementedError()

    @property
    def id(self):
        return self._data.get("id", None)

    @classmethod
    def search(cls, **kwargs):
        """
        Search for objects with the given query filter.
        The kwargs fill be used to filter the results.
        """
        results = []
        res = cls._client.get(cls._endpoint, params=cls.query_params())
        res.raise_for_status()

        for item in res.json():
            results.append(cls(data=item))

        # Filter the results
        for key, value in kwargs.items():
            results = [item for item in results if item[key] == value]

        return results

    @classmethod
    def get(cls, id: int, **kwargs):
        """
        Get a specific object by ID.
        """
        res = cls._client.get(
            f"{cls._endpoint}/{id}", params=cls.query_params(**kwargs)
        )
        res.raise_for_status()

        return cls(data=res.json())

    def update(self, **kwargs):
        """
        Get the object again from the API and update the data.
        """
        self._data = self.get(self.id, **kwargs)._data

    def _ensure_defaults(self):
        """
        Make sure all required fields are set.
        """
        for field, default_value in self._required_fields:
            if field not in self._data:
                self._data[field] = default_value

            if not self._data[field]:
                raise ValueError(f"Missing required field: {field}")

    def _create(self, **kwargs):
        """
        Create a new object from the data in this object.
        """
        self._ensure_defaults()

        res = self._client.post(self._endpoint, json=self._data, params=kwargs)
        res.raise_for_status()
        self._data = res.json()

    def _update(self, **kwargs):
        """
        Update the object with the data in this object.
        """
        self._ensure_defaults()

        res = self._client.put(
            f"{self._endpoint}/{self.id}",
            json=self._data,
            params=kwargs,
        )
        res.raise_for_status()
        self._data = res.json()

    def save(self, **kwargs):
        """
        Create or update an object based on the data in this object. This is
        called automatically when setting or deleting a value in the data
        dictionary.
        """
        if self.id is None:
            self._create(**kwargs)
        else:
            self._update(**kwargs)

    @contextmanager
    def postpone_save(self):
        """
        A context manager that temporarily disables the autosave feature
        and performs a manual save at the end of the context.
        """
        autosave = self.autosave
        self.autosave = False
        yield self
        self.save()
        self.autosave = autosave

    @contextmanager
    def disable_save(self):
        """
        A context manager that temporarily disables the autosave feature.
        """
        autosave = self.autosave
        self.autosave = False
        yield self
        self.autosave = autosave

    def delete(self, **kwargs):
        """
        Delete the object.
        """
        res = self._client.delete(
            f"{self._endpoint}/{self.id}", params=self.query_params()
        )
        res.raise_for_status()
        self._data = {}
        return True
