import sys

import requests


def get_pandoc_deb_url(version: str) -> str:
    """
    Return a download URL for a Pandoc .deb, for the specified version.
    
    Example:
    ```
    python .github/workflows/pandoc_url.py 2.9
    # outputs: https://github.com/jgm/pandoc/releases/download/2.9/pandoc-2.9-1-amd64.deb
    ```
    """
    version_dir = "" if version == "latest" else "tags/"
    url = f"https://api.github.com/repos/jgm/pandoc/releases/{version_dir}{version}"
    response = requests.get(url)
    results = response.json()
    for asset in results["assets"]:
        if asset["name"][-3:] == "deb":
            return asset["browser_download_url"]


if __name__ == "__main__":
    version = sys.argv[1]
    download_url = get_pandoc_deb_url(version)
    print(download_url)
