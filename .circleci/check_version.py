import sys
import tomllib
import urllib.error
import urllib.request

with open("pyproject.toml", "rb") as f:
    project = tomllib.load(f)["project"]

name, version = project["name"], project["version"]
url = f"https://pypi.org/pypi/{name}/{version}/json"

try:
    urllib.request.urlopen(url)
except urllib.error.HTTPError as error:
    if error.code == 404:
        print(f"Version {version} of {name} is new")
        sys.exit(0)
    raise

print(f"Version {version} of {name} is already on PyPI. Bump it in pyproject.toml")
sys.exit(1)
