#!/usr/local/bin/python
import httplib, urllib
import os
import logging as log
import time
import sys
import hashlib as hash
import errno
import re

class ImgResolver(object):

    def __init__(self,up='./pic/unsolved',sp='./pic/solved'):
        self.uns_path = up
        self.s_path = sp
        self.mem = {}
        self.guess_total = 0
        self.guess_hit = 0
        self.algo = ["tesseract"]
        self.check = None
        self.tmp_file = ""

        try:
            os.makedirs(self.uns_path)
            os.makedirs(self.s_path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                log.error("Unknown OSError")
        else:
            log.error("Cannot Create Folders for Learning")

    def loadPics(self):
        pass

    def getCode(self, imgSHA):
        if self.mem.has_key(imgSHA):
            log.info("Get Code from my memory")
            return self.mem[imgSHA]
        else:
            return ""

    def learn(self, imgSHA, imgCode, correct):

        if self.tmp_file is "":
            return

        if correct:
            t_p = os.path.join(self.s_path, imgCode+".jpeg")
        else:
            t_p = os.path.join(self.uns_path, self.tmp_file)
        log.info("copy file to {}".format(t_p))
        try:
            os.rename(self.tmp_file, t_p)
        except Exception as details:
            log.error("learn failed:{}".format(t_p))
            log.error(details)

        self.mem[imgSHA]=imgCode

    def tesseract(self, img):

        # keep the data
        self.tmp_file = "tmp_"+int(time.time()).__str__()+".jpeg"
        with open(self.tmp_file, "w") as oFd:
            oFd.write(img)

        # use tesseract
        imgCode = os.popen("tesseract -l eng {} stdout 2>/dev/null"\
                .format(self.tmp_file)).readline()[0:-1]
        log.info("Guess Ratio:{}/{}={}%".format(self.guess_hit+1, self.guess_total, \
                ((self.guess_hit+1)*100/(self.guess_total))))
        return imgCode

    def basicCheck(self, imgCode):
        if re.match("[a-zA-Z0-9]{5}", imgCode) is 0:
            log.info("none")
            return None
        else:
            log.info("ture")
            return True

    def resolveImg(self, img):
        # retry
        imgCode = ""
        imgSHA = hash.sha1(img).hexdigest()
        imgCode = self.getCode(imgSHA)
        if self.check is None:
            self.check = self.basicCheck

        for alg in self.algo:
            if self.check(imgCode):
                break
            log.info("Use '{}' solver".format(alg))
            self.guess_total +=1
            imgCode= getattr(self,alg)(img)

        # check
        if self.check(imgCode):
            res = False
            imgCode = ""
        else:
            self.guess_hit += 1
            res = True

        self.learn(imgSHA,imgCode,res)
        return imgCode

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)

    r = ImgResolver()
    with open(sys.argv[1], "r") as inFd:
        img = inFd.read()

    print r.resolveImg(img)
