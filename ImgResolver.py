#!/usr/local/bin/python
import os
import logging as log
import time
import sys
import hashlib as hash
import errno
import re
from PIL import Image, ImageEnhance

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
        content = None

        if self.check is None:
            self.check = self.basicCheck

        for dir_p, dirs, files in os.walk(self.s_path):
            for f in files:
                f_p = os.path.join(dir_p,f)
                with open(f_p, "r") as inFd:
                    content = inFd.read()
                imgSHA = hash.sha1(content).hexdigest()
                code = os.path.basename(f).split('.')[0]
                if self.check(code):
                    self.mem[imgSHA] = code
                    log.debug("Load Solved: {}={}".format(imgSHA, code))
                else:
                    os.remove(f_p)
                    log.warn("Remove incorrect file: {}".format(f_p))

        for dir_p, dirs, files in os.walk(self.uns_path):
            for f in files:
                with open(os.path.join(dir_p,f), "r") as inFd:
                    content = inFd.read()
                imgSHA = hash.sha1(content).hexdigest()
                code = os.path.basename(f).split('.')[0]

                # if unsolved pics have been updated manually
                if self.check(code):
                    t_p = os.path.join(self.s_path, code+".jpeg")
                    os.rename(os.path.join(dir_p,f), t_p)
                else:
                    code = ""
                self.mem[imgSHA] = code
                log.debug("Load Unsolved: {}={}".format(imgSHA, code))

    def getCode(self, imgSHA):
        """ if exist, return the code; if fail, return \"\"; if not exist, return None"""
        if self.mem.has_key(imgSHA):
            log.info("Get Code from my memory: {}".format(self.mem[imgSHA]))
            return self.mem[imgSHA]
        else:
            return None

    def reportFail(self, imgCode, imgSHA):

        if imgCode == "":
            return

        tmp_file = os.path.join(self.s_path, imgCode+".jpeg")
        t_p = os.path.join(self.uns_path, imgSHA+".jpeg")
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

    def learn(self, imgSHA, imgCode, correct):
        if self.tmp_file is "":
            return

        if correct:
            t_p = os.path.join(self.s_path, imgCode+".jpeg")
        else:
            t_p = os.path.join(self.uns_path, imgSHA+".jpeg")
        log.debug("copy file to {}".format(t_p))
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
        log.info("Guess Ratio:{}/{}={}%".format(self.guess_hit+1, self.guess_total, \
                ((self.guess_hit+1)*100/(self.guess_total))))
        return imgCode

    def basicCheck(self, imgCode):
        if imgCode is None or re.match("^[a-zA-Z0-9]{5}$", imgCode) is None:
            return None
        else:
            return True

    def resolveImg(self, img):
        # retry
        imgCode = ""
        imgSHA = hash.sha1(img).hexdigest()
        imgCode = self.getCode(imgSHA)

        if imgCode is not None:
            return imgCode

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
            res = False
            imgCode = ""
        else:
            self.guess_hit += 1
            res = True

        self.learn(imgSHA,imgCode,res)
        return imgCode, imgSHA

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)

    r = ImgResolver()
    r.loadPics()
    with open(sys.argv[1], "r") as inFd:
        img = inFd.read()

    print r.resolveImg(img)
