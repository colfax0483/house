import os
import sys
import json
import requests
from collections import OrderedDict

global config
global prog
global act

def ParseFile(file, package):
    global config
    global prog
    global act

    fileName, fileExtension = os.path.splitext(file)
    if(fileExtension != ".smali"):
        return [], [], "", [], []

    #print(file)

    prog['cnt'] += 1
    prog['state'] = "parse smali file - " + file
    
    #requests.post("http://localhost:5000/progstate/" + package, data=prog)

    f = open(file, "r", encoding="utf-8")

    dic = {}
    params = list()
    jsinterfaces = {}
    webviewclass = ""
    className = ""
    methodName = ""
    addURI = list()
    UriParse = list()

    while True:
        line = f.readline()
        if not line: break

        line = line.replace('\n', '')

        words = line.split(" ")
        if words[0] == ".class":
            className = line
        elif words[0] == ".method":
            methodName = line

        if ".annotation" in line:
            for annotation in config["static"]["annotation"]:
                if annotation in line:
                    if len(jsinterfaces) == 0:
                        jsinterfaces['activity'] = 'Activity'
                        jsinterfaces['class'] = className
                        jsinterfaces['methods'] = list()
                    jsinterfaces['methods'].append(methodName)

        for searchString in config["static"]["string"]:
            if searchString in line:
                webviewclass = className

        """
        if "Landroid/webkit/WebView" in line:
            webviewclass = className

        if "Landroid/webkit/JavascriptInterface" in line:
            if len(jsinterfaces) == 0:
                jsinterfaces['class'] = className
                jsinterfaces['methods'] = list()
            jsinterfaces['methods'].append(methodName)
        """

        if "const-string" in line:
            for i in range(0, len(words)):
                if(words[i] == "const-string"):
                    dic[words[i+1][:-1]] = (words[i+2]).replace('\"', '')
                    break
        elif "new-instance" in line:
            for i in range(0, len(words)):
                if(words[i] == "new-instance"):
                    dic[words[i+1][:-1]] = (words[i+2])
        elif "getQueryParameter(" in line:
            for word in words:
                if "}" in word:
                    key = word[:-2]
                    if key in dic.keys():
                        params.append(dic[key])# + " : " + className)
                        break
        elif "addURI(" in line:
            for i in range(0, len(words)):
                if "{" in words[i]:
                    host = ""
                    hostkey = words[i+1].replace(',','')
                    pathkey = words[i+2].replace(',','')
                    if hostkey in dic.keys():
                        host = dic[hostkey]
                        if pathkey in dic.keys():
                            host += "/" + dic[pathkey]
                        addURI.append(host)
                        break
        elif "Uri;->parse(" in line:
            for word in words:
                if "{" in word:
                    key = word.replace('{','').replace('},','')
                    if key in dic.keys():
                        UriParse.append(dic[key])
                        break
        elif "addJavascriptInterface(" in line:
            for i in range(0, len(words)):
                if "{" in words[i]:
                    key = words[i+1].replace(',', '')
                    value = words[i+2].replace('},', '')
                    if key in dic.keys() and value in dic.keys():
                        act[dic[key]] = dic[value]
                    break

    f.close()
    return params, jsinterfaces, webviewclass, addURI, UriParse

def Parse(apk, package, xml):
    global config
    global prog
    global act
    pwd = apk[:-4]

    params = list()
    jsinterfaces = list()
    webviewclasses = list()
    addURIs = list()
    UriParse = list()
    UriParses = list()
    result = {}
    prog = dict()
    act = dict()

    prog['cnt'] = 0
    prog['state'] = ""

    config = dict()
    with open("config.json", "r") as read_json:
	    config = json.load(read_json)

    for path, dirs, files in os.walk(pwd):
        for file in files:
            ptmp, jtmp, wtmp, atmp, utmp = ParseFile(os.path.join(path, file), package)
            params += ptmp
            if len(jtmp) != 0:
                jsinterfaces.append(jtmp)
            if wtmp != "":
                webviewclasses.append(wtmp)
            if len(atmp) != 0:
                addURIs += atmp
            if len(utmp) != 0:
                UriParse += utmp
    
    for jsinterface in jsinterfaces:
        jsclass = jsinterface['class'].split(" ")
        jsclass = jsclass[len(jsclass) - 1]
        if jsclass in act.keys():
            jsinterface['activity'] = act[jsclass]

    """
    output.write("[Parameters]\n")
    for param in params:
        output.write(param)
        output.write("\n")
    output.write("[JavascriptInterfaces]\n")
    for jsinterface in jsinterfaces:
        output.write(jsinterface)
        output.write("\n")
    output.write("[Webview Classes]\n")
    for webviewclass in webviewclasses:
        output.write(webviewclass)
        output.write("\n")
    """

    for Uri in UriParse:
        for scheme in xml['Scheme']:
            if scheme in Uri:
                UriParses.append(Uri)
                break

    result["Parameter"] = list(set(params))
    result["JavascriptInterface"] = jsinterfaces
    #result["WebviewClass"] = webviewclasses
    result["addURIs"] = addURIs
    result["UriParses"] = UriParses

    return result
            
if __name__ == "__main__":
    #output = open(sys.argv[2], "w", encoding="utf-8")
    Parse(sys.argv[1])
    #output.close()
