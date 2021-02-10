import os
import sys

def unpack(apk):
    dir = apk[:-4]
    print("java -jar android/bin/apktool.jar d %s -f --output %s"%(apk, dir))
    os.system("java -jar android/bin/apktool.jar d %s -f --output %s"%(apk, dir))
    #os.system("java -jar apktool.jar d 'com.sampleapp_21000832_apps.evozi.com.apk' -f --output 'output'")
    
    pwd = apk[:-4]
    AndroidManifest = pwd + "/AndroidManifest.xml"

    f = open(AndroidManifest, "r")

    line = f.readline()
    package = ""

    words = line.split(" ")
    for word in words:
        if "package=\"" in word:
            package = word[9:-1]
    print(package)
    return package

if __name__ == "__main__":
    unpack(sys.argv[1])