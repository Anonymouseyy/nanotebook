import requests, sys, os
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


class detaDrive:
    def __init__(self, key, name):
        self.key = key
        self.url = f"https://drive.deta.sh/v1/{get_project_key_id(key)[1]}/{name}"
        self.def_header = {
            'X-API-Key': key
        }

    @staticmethod
    def checkok(response):
        if response.ok:
            return response.json()
        else:
            return None

    def put(self, file_name, content=None, file_path=None):
        if content ^ file_path:
            raise AssertionError("No content or file path")

        if file_path and not os.path.isfile(file_path):
            raise AssertionError("No file exists at that location")

        size = sys.getsizeof(content.decode("utf8")) if content else os.path.getsize(file_path)

        if size <= 1e6:
            url = f"{self.url}/files?name={file_name}"

            if content:
                return self.checkok(requests.post(url, headers=self.def_header, data=content))

            if file_path:
                with open(file_path, "rb") as f:
                    file_content = f.read()
                return self.checkok(requests.post(url, headers=self.def_header, data=file_content))

        if size > 1e6:
            # Initialize chunked upload
            init = self.checkok(requests.post(f"{self.url}/uploads?name={file_name}", headers=self.def_header))
            if init is None:
                raise AssertionError("Something went wrong while initializing the upload")

            upload_id = init["upload_id"]

            if content:
                pass # CODE NEEDED HERE LMAO

            if file_path:
                file = open(file_path, "rb")
                [part] = 1

                while True:
                    chunk = file.read(9000000)
                    if not chunk: break
                    if not requests.post(f"{self.url}/uploads/{upload_id}/parts?name={file_name}&part={part}", headers=self.def_header).ok:
                        file.close()
                        requests.delete(f"{self.url}/uploads/{upload_id}?name={file_name}", headers=self.def_header)
                        raise AssertionError("Something went wrong while uplaoding the file")
                    part += 1

                file.close()
                return self.checkok(requests.patch(f"{self.url}/uploads/{upload_id}/parts?name={file_name}", headers=self.def_header))

        raise AssertionError("Something went wrong")

    def list(self, limit, prefix, last):
        url = f"{self.url}/files?" + (f"limit={limit}&" if limit else '') + (f"prefix={prefix}&" if prefix else '') \
              + (f"last={last}&" if last else '')
        return self.checkok(requests.get(url, headers=self.def_header))

    def delete(self, files):
        return self.checkok(requests.delete(f"{self.url}/files", headers=self.def_header, data={"names": files}))