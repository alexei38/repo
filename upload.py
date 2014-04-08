#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pycurl
import StringIO
import json
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--arch", action="store")
parser.add_argument("--repo", action="store")
parser.add_argument("--file", action="append")
parser.add_argument("--snapshot", action="count")

args = vars(parser.parse_args())
io = StringIO.StringIO()
curl = pycurl.Curl()
curl_data = [("file", (curl.FORM_FILE, file)) for file in args['file']]
curl_data.append(("key", "LsdDFjn234rF78hfuI234SDfe789fhw"))
if args['snapshot']:
    curl_data.append(("snapshot", "1"))
curl_data.append(("repo_name", args['repo']))
curl_data.append(("arch", args['arch']))
curl.setopt(curl.POST, 1)
curl.setopt(curl.URL, "http://repo.cc.naumen.ru/upload/")
curl.setopt(curl.HTTPPOST, curl_data)
curl.setopt(curl.VERBOSE, 0)
curl.setopt(pycurl.WRITEFUNCTION, io.write)
curl.perform()
curl.close()

json_decode = json.loads(io.getvalue())
if json_decode['data'] == 'ok':
    print json_decode['url']
    sys.exit(0)
else:
    print "ERR: %s" % json_decode['msg']
    sys.exit(1)

