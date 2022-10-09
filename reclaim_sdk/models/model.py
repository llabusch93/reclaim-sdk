from reclaim_sdk.client import ReclaimAPICall


class ReclaimModel(object):
    """
    This is the base model for any storable object on Reclaim.ai. It implements
    the basic CRUD operations.
    """

    _endpoint = None
    _name = None
    _required_fields = []
    _default_params = {}

    def __init__(self, data: dict = {}, **kwargs) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"{self._name} ({self.id} - {self.name})"

    def __str__(self) -> str:
        return f"{self.name}"

    def __getitem__(self, key):
        """
        Get a value from the data dictionary.
        """
        return self._data.get(key, None)

    def __setitem__(self, key, value):
        """
        Set a value in the data dictionary.
        """
        self._data[key] = value

    def __delitem__(self, key):
        """
        Delete a key from the data dictionary.
        """
        del self._data[key]

    def __eq__(self, __o: object) -> bool:
        """
        The objects are equal if they have the same ID and type.
        """
        return self.id == __o.id and self.__class__ == __o.__class__

    # Make it possible to use the object as a context manager
    # and automatically save the object to the API when exiting the context.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
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
    def id(self):
        """
        The ID of the object. Must be implemented by the subclass.
        """
        raise NotImplementedError("Must be implemented by subclass.")

    @property
    def name(self):
        raise NotImplementedError()

    @name.setter
    def name(self, value):
        raise NotImplementedError()

    @classmethod
    def search(cls, **kwargs):
        """
        Search for objects. The given keyword arguments are used as
        filter parameters. Only equal filters are supported (==).

        FIXME: Make the search more flexible and support more operators.
               As this is reverse engineered from the API, we don't know
               what is supported and if there is a search syntax for
               more complex queries in the query parameters.
        """
        with ReclaimAPICall(cls) as client:
            res = client.get(cls._endpoint, params=cls.query_params())
            res.raise_for_status()

        results = []

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

        with ReclaimAPICall(cls, id=id) as client:
            res = client.get(
                f"{cls._endpoint}/{id}", params=cls.query_params()
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

        with ReclaimAPICall(self) as client:
            res = client.post(self._endpoint, json=self._data, params=kwargs)
            res.raise_for_status()

        self._data = res.json()

    def _update(self, **kwargs):
        """
        Update the object with the data in this object.
        """
        self._ensure_defaults()

        with ReclaimAPICall(self) as client:
            res = client.put(
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

    def delete(self, **kwargs):
        """
        Delete the object.
        """

        with ReclaimAPICall(self) as client:
            res = client.delete(f"{self._endpoint}/{self.id}", params=kwargs)
            res.raise_for_status()

        self._data = {}
        return True
