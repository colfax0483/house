from . import SmaliParser
from . import XMLParser
from . import apktool

import json
import sys
import os
import datetime
import requests
from collections import OrderedDict

def run(apk, out, package):
    app = dict()
    app["app"] = {"apk":apk[12:], "package":package, "date":str(datetime.datetime.today())}

    #print("Unpack APK file")
    #apktool.unpack(apk)
    print("Parse AndroidManifest.xml")
    prog = {'width':'5', 'state':'parse AndroidManifest.xml'}
    requests.post("http://localhost:5000/progstate/" + package, data=prog)
    xml = XMLParser.xml(apk)

    print("Parse smali files")
    prog = {'width':'10', 'state':'parse smali files'}
    requests.post("http://localhost:5000/progstate/" + package, data=prog)
    parse = SmaliParser.Parse(apk, package, xml)
    
    prog = {'width':'60', 'state':'finish to parse smali files'}
    requests.post("http://localhost:5000/progstate/" + package, data=prog)


    result = {**app, **xml, **parse}

    with open(out, 'w', encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent="\t")

    return result

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])