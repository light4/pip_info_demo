#!/usr/bin/env python

import argparse
import json
import socket
import urllib.request
from dataclasses import dataclass

# timeout in seconds
timeout = 10
socket.setdefaulttimeout(timeout)


class PipInfoError(Exception):
    pass


class ServerError(PipInfoError):
    pass


class PkgNotFound(PipInfoError):
    pass


@dataclass
class Info(object):
    name: str
    version: str
    author: str
    author_email: str
    home_page: str
    project_url: str
    release_url: str
    summary: str


@dataclass
class PkgBriefInfo(object):
    name: str
    version: str
    author: str
    author_email: str
    home_page: str
    project_url: str
    release_url: str
    summary: str
    download_urls: list

    def show(self):
        for k in self.__dataclass_fields__:
            v = getattr(self, k)
            if isinstance(v, list):
                print("{:<16}:".format(k.title()))
                for i in v:
                    print("    - {}".format(i))
            else:
                print("{:<16}: {}".format(k.title(), v))


def get_pkg_json(pkg: str):
    url = 'https://pypi.org/pypi/{}/json'.format(pkg)
    try:
        with urllib.request.urlopen(url) as f:
            return json.load(f)
    except urllib.request.HTTPError as e:
        if e.code >= 500:
            raise ServerError('request {} failed'.format(url))
        elif e.code >= 400:
            raise PkgNotFound('request {}: {}'.format(url, e.reason))


def parse_pkg_brief_info(content):
    def cls_fields(cls, data):
        return {k: v for k, v in data.items() if k in cls.__dataclass_fields__}

    info = content.get('info')
    inner_info = cls_fields(Info, info)
    urls = content.get('urls')
    download_urls = []
    for u in urls:
        download_urls.append(u.get('url'))
    return PkgBriefInfo(download_urls=download_urls, **inner_info)


def parse_args():
    parser = argparse.ArgumentParser(description='pip-info: show python package info.')
    parser.add_argument('pkg_names',
                        metavar='pkg_name',
                        type=str,
                        nargs='+',
                        help='show info of multiple packages')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    for pkg in args.pkg_names:
        try:
            json_content = get_pkg_json(pkg)
        except PipInfoError as e:
            print(e)
            continue
        info = parse_pkg_brief_info(json_content)
        info.show()
        print()


if __name__ == "__main__":
    main()
