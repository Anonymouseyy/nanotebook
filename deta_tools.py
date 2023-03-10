import requests
from urllib.parse import quote


def get_project_key_id(project_key: str = None, project_id: str = None):
    if not project_key:
        raise AssertionError("No project key defined")

    if not project_id:
        project_id = project_key.split("_")[0]

    if project_id == project_key:
        raise AssertionError("Bad project key provided")

    return project_key, project_id


class detaBase:
    def __init__(self, key, name):
        self.key = key
        self.url = f"https://database.deta.sh/v1/{get_project_key_id(key)[1]}/{name}"
        self.def_header = {
            'X-API-Key': key
        }

    @staticmethod
    def checkok(response):
        if response.ok:
            return response.json()
        else:
            return None

    def put(self, keys, data):
        items = []
        for i in range(len(data)):
            key = None
            try:
                key = keys[i]
            finally: pass

            if key is not None:
                item = data[i]
                item["key"] = key
                items.append(item)
            else:
                items.append(data[i])

        return self.checkok(requests.put(f"{self.url}/items", headers=self.def_header, data={items}))

    def get(self, key):
        return self.checkok(requests.get(f"{self.url}/items/{quote(key)}", headers=self.def_header))

    def delete(self, key):
        return self.checkok(requests.delete(f"{self.url}/items/{quote(key)}", headers=self.def_header))

    def insert(self, item):
        return self.checkok(requests.post(f"{self.url}/items", headers=self.def_header, data={"item": item}))

    def update(self, key, updates):
        return self.checkok(requests.patch(f"{self.url}/items/{quote(key)}", headers=self.def_header, data={"set": updates}))

    def query(self, query=None, limit=None):
        data = {}

        if query:
            data["query"] = query
        if limit:
            data["limit"] = limit

        return self.checkok(requests.post(f"{self.url}/query", headers=self.def_header, data=data))
