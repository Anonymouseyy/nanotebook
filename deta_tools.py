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
        item = {"key": keys}
        item.update(data)
        return self.checkok(requests.put(f"{self.url}/items", headers=self.def_header, json={"items": [item]}))

    def get(self, key):
        return self.checkok(requests.get(f"{self.url}/items/{quote(key)}", headers=self.def_header))

    def delete(self, key):
        return self.checkok(requests.delete(f"{self.url}/items/{quote(key)}", headers=self.def_header))

    def insert(self, item):
        return self.checkok(requests.post(f"{self.url}/items", headers=self.def_header, json={"item": item}))

    def update(self, key, updates):
        return self.checkok(requests.patch(f"{self.url}/items/{quote(key)}", headers=self.def_header,
                                           json={"set": updates}))

    def query(self, query=None, limit=None):
        data = {}

        if query:
            data["query"] = query
        if limit:
            data["limit"] = limit

        return self.checkok(requests.post(f"{self.url}/query", headers=self.def_header, json=data))


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
        if not (content is None or file_path is None) or (content is None and file_path is None):
            raise AssertionError("No content or file path")

        if file_path and not os.path.isfile(file_path):
            raise AssertionError("No file exists at that location")

        content = content.encode("utf-8")
        size = len(content) if content else os.path.getsize(file_path)

        if size <= 1e6:
            url = f"{self.url}/files?name={quote(file_name)}"

            if content:
                return self.checkok(requests.post(url, headers=self.def_header, data=content))

            if file_path:
                with open(file_path, "rb") as f:
                    file_content = f.read()
                return self.checkok(requests.post(url, headers=self.def_header, data=file_content))

        if size > 1e6:
            # Initialize chunked upload
            init = self.checkok(requests.post(f"{self.url}/uploads?name={quote(file_name)}", headers=self.def_header))
            if init is None:
                raise AssertionError("Something went wrong while initializing the upload")

            upload_id = init["upload_id"]

            if content:
                chunks = []

                i = 0
                while i < len(content):
                    if i + 900000 < len(str):
                        chunks.append(str[i:i + 900000])
                    else:
                        chunks.append(str[i:])
                    i += 900000

                for count, chunk in enumerate(chunks):
                    if not requests.post(f"{self.url}/uploads/{quote()}/parts?name={quote(file_name)}&part={quote(str(count+1))}",
                                         headers=self.def_header, data=chunk).ok:
                        requests.delete(f"{self.url}/uploads/{upload_id}?name={file_name}", headers=self.def_header)
                        raise AssertionError("Something went wrong while uplaoding the file")

                return self.checkok(
                    requests.patch(f"{self.url}/uploads/{quote(upload_id)}/parts?name={quote(file_name)}", headers=self.def_header))

            if file_path:
                file = open(file_path, "rb")
                part = 1

                while True:
                    chunk = file.read(9000000)
                    if not chunk: break
                    if not requests.post(f"{self.url}/uploads/{quote(upload_id)}/parts?name={quote(file_name)}&part={quote(str(part))}",
                                         headers=self.def_header, data=chunk).ok:
                        file.close()
                        requests.delete(f"{self.url}/uploads/{quote(upload_id)}?name={quote(file_name)}", headers=self.def_header)
                        raise AssertionError("Something went wrong while uplaoding the file")
                    part += 1

                file.close()
                return self.checkok(
                    requests.patch(f"{self.url}/uploads/{quote(upload_id)}/parts?name={quote(file_name)}", headers=self.def_header))

        raise AssertionError("Something went wrong")

    def get(self, file_name):
        res = requests.get(f"{self.url}/files/download?name={quote(file_name)}", headers=self.def_header)

        if not res.ok:
            raise AssertionError("Something went wrong")

        return res.content

    def list(self, limit, prefix, last):
        url = f"{self.url}/files?" + (f"limit={quote(limit)}&" if limit else '') + (f"prefix={quote(prefix)}&" if prefix else '') \
              + (f"last={quote(str(last))}&" if last else '')
        return self.checkok(requests.get(url, headers=self.def_header))

    def delete(self, files):
        return self.checkok(requests.delete(f"{self.url}/files", headers=self.def_header, json={"names": files}))
