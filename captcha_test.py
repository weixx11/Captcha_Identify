#!/usr/bin/env python
#coding=utf-8

import  tensorflow as tf
from captcha.image import  ImageCaptcha
import numpy as np
import  matplotlib.pyplot as plt
from PIL import  Image
import  random
import  cv2

number=['0','1','2','3','4','5','6','7','8','9']
alphabet=["a",'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
ALPHABET=["A",'B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

def Gray(image):
    B_image = image[:,:,0]
    G_image = image[:,:,1]
    R_image = image[:,:,2]
    Gray_image = R_image*0.3+G_image*0.59+B_image*0.11
    Gray_image = Gray_image.astype(np.uint8)
    return Gray_image

def random_captcha_text(char_set=number+alphabet+ALPHABET,captcha_size=4):
    captcha_text = []
    for i in range(captcha_size):
        c = random.choice(char_set)
        captcha_text.append(c)
    return captcha_text

#生成验证码
def get_captcha_text_and_image():
    image = ImageCaptcha()
    captcha_text = random_captcha_text()
    captcha_text = ''.join(captcha_text)

    captcha = image.generate(captcha_text)

    captcha_image = Image.open(captcha)
    captcha_image = np.array(captcha_image)
    return captcha_text,captcha_image
# random_text=random_captcha_text()

# print(random_text)

if __name__=="__main__":
    text,image = get_captcha_text_and_image()
    image = Gray(image)
    print(text)
    print(image)
    print(image.dtype)
    cv2.imshow("demo",image)
    # cv2.imwrite("my-test.jpg",image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # f=plt.figure()
    # ax=f.add_subplot(111)
    # ax.text(0.1,0.9,text,ha='center',va='center',transform=ax.transAxes)
    # plt.imshow(image)
    # plt.show()