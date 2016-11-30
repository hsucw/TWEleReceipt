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

    def loadPics(self):
        content = None

        if self.check is None:
            self.check = self.basicCheck

    def tesseract(self, img):

        # keep the data
        fileName = "tmp_"+int(time.time()+random.randint(1,99999)).__str__()+".jpeg"
        while os.path.exists( fileName ):
            fileName = "tmp_"+int(time.time()+random.randint(1,99999)).__str__()+".jpeg"
        self.tmp_file = fileName
        with open(self.tmp_file, "w") as oFd:
            oFd.write(img)
        # resolve noise
        try:
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
        except Exception as e:
            pass
        else:
            pass
        # use tesseract

        imgCode = os.popen("tesseract -l eng -psm 8 {} stdout 2>/dev/null"\
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
        # retry
        imgCode = None

        if self.check is None:
            self.check = self.basicCheck

        for alg in self.algo:
            if self.check(imgCode):
                break
            self.guess_total +=1
            imgCode= getattr(self,alg)(img)
            log.debug("Use '{}' solver: {}".format(alg, imgCode))

        # check
        if not self.check(imgCode):
            imgCode = ""
        else:
            self.guess_hit += 1

        return imgCode

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)

    r = ImgResolver()
    r.loadPics()
    with open(sys.argv[1], "r") as inFd:
        img = inFd.read()

    print r.resolveImg(img)
