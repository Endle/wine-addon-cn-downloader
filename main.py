WINE_CACHE = '~/.cache/wine'
WINE_MONO_REPO = 'https://mirrors.ustc.edu.cn/wine/wine/wine-mono'

import requests
from lxml import etree
import subprocess
import os


def get_pre_elem(content:str) -> etree.Element:
    root = etree.HTML(content)

    pre = root.xpath('/html/body/pre')
    assert type(pre) == list
    assert len(pre) == 1
    pre = pre[0]
    assert pre.tag == 'pre'
    return pre


def get_last_version_string(content:str) -> str:
    pre = get_pre_elem(content)

    provided_versions = [link.text.rstrip('/') for link in pre]
    # Filter out .. Seems not necessary
    # provided_versions = [v for v in provided_versions if v[0] != '.']

    # Warn: Lexicographic Order isn't real version number order. Just being lazy here
    return max(provided_versions)


def download_single_file(url: str, write_to: str):
    import os
    write_to = os.path.expanduser(write_to)
    print("Downloading ", url, "\n\t Saving to ", write_to)
    return subprocess.run(['wget', '-O', write_to, '-nc', '--progress=dot:mega', url])


def download_all(url: str, directory: str) -> None:
    response = requests.get(url)

    response.raise_for_status()
    pre = get_pre_elem(str(response.content))
    files = [link.get('href') for link in pre]
    files = [v for v in files if v[0] != '.']
    files = [v for v in files if 'tests' not in v]
    files = [v for v in files if 'src' not in v]
    #files = [(url + '/' + v) for v in files]
    for f in files:
        download_single_file(url + '/' + f, directory + '/' + f)



def download_wine_mono() -> None:
    response = requests.get(WINE_MONO_REPO)
    response.raise_for_status()
    content = str(response.content)

    selected_version = get_last_version_string(content)
    download_page = WINE_MONO_REPO + '/' + selected_version
    download_all(download_page, WINE_CACHE)



def main():
    download_wine_mono()


if __name__ == '__main__':
    main()