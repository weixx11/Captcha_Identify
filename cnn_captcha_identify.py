#!/usr/bin/env python
#coding=utf-8


import  tensorflow as tf
from captcha.image import  ImageCaptcha
import numpy as np
import  matplotlib.pyplot as plt
from PIL import  Image
import  random

number = ['0','1','2','3','4','5','6','7','8','9']
#alphabet=["a",'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
#ALPHABET=["A",'B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

def random_captcha_text(char_set=number,captcha_size=4):
    """
    随机生成验证码
    :param char_set: 可选验证码字符串
    :param captcha_size: 验证码长度
    :return:
    """
    captcha_text = []
    for i in range(captcha_size):
        c = random.choice(char_set)
        captcha_text.append(c)
    return captcha_text

#生成验证码
def get_captcha_text_and_image():
    """
    生成验证码图片
    :return:captcha_text返回验证码内容，captcha_image返回验证码图片
    """
    image = ImageCaptcha()
    captcha_text = random_captcha_text()
    captcha_text = ''.join(captcha_text)

    captcha = image.generate(captcha_text)

    captcha_image = Image.open(captcha)
    captcha_image = np.array(captcha_image)
    return captcha_text,captcha_image

def convert2gray(image):
    """
    将图片进行灰度
    :param image:
    :return:
    """
    if len(image.shape) > 2:
        gray = np.mean(image, -1)
        # 上面的转法较快，正规转法如下
        # r, g, b = image[:,:,0], image[:,:,1], image[:,:,2]
        # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray
    else:
        return image


def text2vec(text):
    """
    将文本lables转换成向量
    :param text:
    :return:
    """
    text_len = len(text)
    if text_len > MAX_CAPTCHA:
        raise ValueError('验证码最长4个字符')

    vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)
    """
    def char2pos(c):  
        if c =='_':  
            k = 62  
            return k  
        k = ord(c)-48  
        if k > 9:  
            k = ord(c) - 55  
            if k > 35:  
                k = ord(c) - 61  
                if k > 61:  
                    raise ValueError('No Map')   
        return k  
    """
    for i, c in enumerate(text):
        idx = i * CHAR_SET_LEN + int(c)
        vector[idx] = 1
    return vector


def get_next_batch(batch_size=128):
    """
    生成一个训练的batch
    :param batch_size: batch大小
    :return:
    """
    batch_x = np.zeros([batch_size,IMAGE_HEIGHT*IMAGE_WIDTH])
    batch_y = np.zeros([batch_size,MAX_CAPTCHA*CHAR_SET_LEN])

    #防止有时候生成的图像大小不是（60,160,3）
    def wrap_gen_captcha_text_and_image():
        while True:
            text ,image = get_captcha_text_and_image()
            if image.shape == (60,160,3):
                return text,image
    for i in range(batch_size):
        text ,image = wrap_gen_captcha_text_and_image()
        image = convert2gray(image)

        batch_x[i,:] = image.flatten()/255  #将数据转换成0-1之间
        batch_y[i,:] = text2vec(text)
    return  batch_x,batch_y

def crack_captcha_cnn(w_alpha=0.01,b_alpha=0.1):
    """
    定义CNN网络结构
    :param w_alpha:
    :param b_alpha:
    :return:
    """
    #将图片转成灰色
    x = tf.reshape(X,shape=[-1,IMAGE_HEIGHT,IMAGE_WIDTH,1])

    #三层卷积层
    w_c1 = tf.Variable(w_alpha*tf.random_normal([3,3,1,32]))
    b_c1 = tf.Variable(b_alpha*tf.random_normal([32]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x,w_c1,strides=[1,1,1,1],padding='SAME'),b_c1))
    conv1 = tf.nn.max_pool(conv1,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')
    conv1 = tf.nn.dropout(conv1,keep_prob)

    w_c2 = tf.Variable(w_alpha*tf.random_normal([3,3,32,64]))
    b_c2 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1,w_c2,strides=[1,1,1,1],padding='SAME'),b_c2))
    conv2 = tf.nn.max_pool(conv2,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')
    conv2 = tf.nn.dropout(conv2,keep_prob)

    w_c3 = tf.Variable(w_alpha*tf.random_normal([3,3,64,64]))
    b_c3 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2,w_c3,strides=[1,1,1,1],padding='SAME'),b_c3))
    conv3 = tf.nn.max_pool(conv3,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')
    conv3 = tf.nn.dropout(conv3,keep_prob)

    #全连接
    w_d = tf.Variable(w_alpha*tf.random_normal([8*20*64,1024])) #在这里卷积没有将图片变小，池化将图片变小，每一次池化高跟宽减小一倍
    '''
    h=60,w=160
    池化层：将4个数变成1个数
    第一次池化：h/2=30 w/2=80
    第二次池化：h/2=15 w/2=40
    由于padding="SAME" 7.5补充
    第三次池化：h/2=8 w/2=20
    '''
    b_d = tf.Variable(b_alpha*tf.random_normal([1024]))
    dense = tf.reshape(conv3,[-1,w_d.get_shape().as_list()[0]])
    dense = tf.nn.relu(tf.add(tf.matmul(dense,w_d),b_d))
    dense = tf.nn.dropout(dense,keep_prob)

    w_out = tf.Variable(w_alpha*tf.random_normal([1024,MAX_CAPTCHA*CHAR_SET_LEN]))
    b_out = tf.Variable(b_alpha*tf.random_normal([MAX_CAPTCHA*CHAR_SET_LEN]))
    out = tf.add(tf.matmul(dense,w_out),b_out)
    return out

def train_crack_captcha_cnn():
    """
    训练网络
    :return:
    """
    output = crack_captcha_cnn()
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
    # loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(output, Y))
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)
    predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    max_idx_p = tf.argmax(predict, 2)
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
    correct_pred = tf.equal(max_idx_p, max_idx_l)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
    #保存模型
    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        step = 0
        while True:
            batch_x, batch_y = get_next_batch(64)
            _, loss_ = sess.run([optimizer, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
            print(step,'loss:',loss_)

            #每100步计算一次准确率
            if step % 100 == 0:
                batch_x_test,batch_y_test = get_next_batch(100)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print(step,'acc:',acc)
                #如果准确率大于95%，保存模型
                if acc > 0.95:
                    saver.save(sess,"./model/crack_capcha.model",global_step=step)
                    break
            step += 1


def crack_captcha(captcha_image):
    """
    测试模型
    :param captcha_image:
    :return:
    """
    output = crack_captcha_cnn()

    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, "./model/crack_capcha.model-2100")

        predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
        text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})
        text = text_list[0].tolist()
        return text

if __name__ == '__main__':
    train = 0  #表示训练模型
    train = 1  #表示测试模型
    if train == 0:
        number = ['0','1','2','3','4','5','6','7','8','9']
        text, image = get_captcha_text_and_image()

        print("验证码图像维度：",image.shape)  #(60, 160, 3)


        #图像大小
        IMAGE_HEIGHT = 60
        IMAGE_WIDTH = 160
        MAX_CAPTCHA = len(text)
        print("验证码文本最长字符数：",MAX_CAPTCHA)

        #文本转向量
        char_set = number
        CHAR_SET_LEN = len(char_set)

        X = tf.placeholder(tf.float32,[None,IMAGE_HEIGHT*IMAGE_WIDTH])
        Y = tf.placeholder(tf.float32,[None,MAX_CAPTCHA*CHAR_SET_LEN])
        keep_prob = tf.placeholder(tf.float32)  #dropout参数

        train_crack_captcha_cnn()

    if train == 1:
        number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        IMAGE_HEIGHT = 60
        IMAGE_WIDTH = 160
        char_set = number
        CHAR_SET_LEN = len(char_set)

        text, image = get_captcha_text_and_image()

        f = plt.figure()
        ax = f.add_subplot(111)
        ax.text(0.1, 0.9, text, ha='center', va='center', transform=ax.transAxes)
        plt.imshow(image)

        plt.show()

        MAX_CAPTCHA = len(text)
        image = convert2gray(image)
        image = image.flatten() / 255

        X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT * IMAGE_WIDTH])
        Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA * CHAR_SET_LEN])
        keep_prob = tf.placeholder(tf.float32)  # dropout

        predict_text = crack_captcha(image)
        print("正确: {}  预测: {}".format(text, predict_text))