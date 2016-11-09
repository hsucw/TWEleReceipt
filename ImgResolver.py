#!/usr/local/bin/python
import os
import logging as log
import time
import sys
import hashlib as hash
import errno
import re
import random
from PIL import Image, ImageEnhance



class ImgResolver(object):

    def __init__(self):
        self.guess_total = 0
        self.guess_hit = 0
        self.algo = ["tesseract"]
        self.check = None
        self.tmp_file = ""


    def reportFail(self, imgCode, imgSHA):

        if imgCode == "":
            return

        self.guess_hit -= 1
        try:
            os.rename(tmp_file, t_p)
        except:
            log.error("Rename file error: {} -> {}".format(tmp_file, t_p))
        try:
            self.mem[imgSHA]=""
        except KeyError:
            log.error("No such key {} in imgCode mem".format(imgSHA))
        log.debug("Report Fail:{}".format(imgCode))

    def tesseract(self, img):

        # keep the data
        fileName = "tmp_"+int(time.time()+random.randint(1,99999)).__str__()+".jpeg"
        while os.path.exists( fileName ):
            fileName = "tmp_"+int(time.time()+random.randint(1,99999)).__str__()+".jpeg"
        self.tmp_file = fileName
        with open(self.tmp_file, "w") as oFd:
            oFd.write(img)

        # resolve noise
        im = Image.open(self.tmp_file)
        enhancer = ImageEnhance.Color(im)
        im = enhancer.enhance(0.0)
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(3.0)
        enhancer = ImageEnhance.Brightness(im)
        im = enhancer.enhance(10.0)
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(20.0)
        enhancer = ImageEnhance.Sharpness(im)
        im = enhancer.enhance(0.0)
        im.save(self.tmp_file)

        # use tesseract

        imgCode = os.popen("tesseract -l eng {} stdout 2>/dev/null"\
                .format(self.tmp_file)).readline()[0:-1]
        log.debug("Guess Ratio:{}/{}={}%".format(self.guess_hit+1, self.guess_total, \
                ((self.guess_hit+1)*100/(self.guess_total))))

        os.remove( self.tmp_file )


        return imgCode

    def basicCheck(self, imgCode):
        if imgCode is None or re.match("^[a-zA-Z0-9]{5}$", imgCode) is None:
            return None
        else:
            return True

    def resolveImg(self, img):

        imgCode=""
        if self.check is None:
            self.check = self.basicCheck

        for alg in self.algo:
            if self.check(imgCode):
                break
            log.debug("Use '{}' solver".format(alg))
            self.guess_total +=1
            imgCode= getattr(self,alg)(img)

        # check
        if not self.check(imgCode):
            log.debug("Basic Check Fail")
            res = False
            imgCode = ""
        else:
            log.debug("Resolve Success")
            self.guess_hit += 1
            res = True

        #self.learn(imgSHA,imgCode,res)



        return imgCode

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)

    r = ImgResolver()
    with open(sys.argv[1], "r") as inFd:
        img = inFd.read()

    print r.resolveImg(img)
