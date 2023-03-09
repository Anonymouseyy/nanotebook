import requests


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

        return requests.put(f"{self.url}/items", headers=self.def_header, data={items}) or None

    def get(self, key):
        return requests.get(f"{self.url}/items/{key}", headers=self.def_header) or None

    def delete(self, key):
        return requests.delete(f"{self.url}/items/{key}", headers=self.def_header) or None

    def insert(self, item):
        return requests.post(f"{self.url}/items", headers=self.def_header, data={"item": item}) or None

    def update(self, key, updates):
        return requests.patch(f"{self.url}/items/{key}", headers=self.def_header, data={"set": updates}) or None

    def query(self, query, limit):
        return requests.post(f"{self.url}/query", headers=self.def_header, data={"query": query,
                                                                                 "limit": limit}) or None
