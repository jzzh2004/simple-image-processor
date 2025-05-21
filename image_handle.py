import random
import numpy as np
import cv2 as cv
from Bilinear_interpolation import double_biline
import os
import tempfile

def imagescale(info):
    try:
        # 直接从内存字节数据读取图像
        img_array = np.frombuffer(info['image'], dtype=np.uint8)
        img = cv.imdecode(img_array, cv.IMREAD_COLOR)  # 始终以彩色图像读取
        
        if img is None:
            return None, None
        
        # 获取原始尺寸 (高度, 宽度)
        img=np.array(img)

        SSIZE=img.shape
        DSIZE = (int(info['mode_params']['height']), int(info['mode_params']['width']))
#三通道分开处理
        b,g,r = cv.split(img)

        b=double_biline(b,SSIZE,DSIZE)
        g=double_biline(g,SSIZE,DSIZE)
        r=double_biline(r,SSIZE,DSIZE)
        resized_img = cv.merge((b,g,r))
        
        # 保存结果到临时文件
        output_path = os.path.join(tempfile.gettempdir(), 'resized_output.jpg')
        cv.imwrite(output_path, resized_img, [int(cv.IMWRITE_JPEG_QUALITY), 100])
        
        return resized_img, output_path
        
    except Exception as e:
        print(f"图像处理错误: {e}")
        return None, None




def imagenoise(info):
        img_array = np.frombuffer(info['image'], dtype=np.uint8)
        img = cv.imdecode(img_array, cv.IMREAD_COLOR)  # 始终以彩色图像读取
        if img is None:
            return None, None
        # 获取原始尺寸 (高度, 宽度)
        img=np.array(img)


        if info['mode_params']['noise_type'] == '高斯噪声':
            noise = np.random.normal(0,50,size=img.size).reshape(img.shape[0],img.shape[1],img.shape[2])
# 加上噪声
            img = img + noise
            new_img = np.clip(img,0,255)
            
        
        elif info['mode_params']['noise_type'] == '椒盐噪声':
            x = img.reshape(1,-1)  
# 设置信噪比
            SNR = 0.85
# 得到要加噪的像素数目
            noise_num = x.size * (1-SNR)
# 得到需要加噪的像素值的位置
            list = random.sample(range(0,x.size),int(noise_num))
            for i in list:
                if random.random() >= 0.5:
                    x[0][i] = 0
                else:
                    x[0][i] = 255
            new_img = x.reshape(img.shape)

        elif info['mode_params']['noise_type'] == '泊松噪声':
            noise = np.random.poisson(lam=20,size=img.shape).astype('uint8')
            img = img + noise
            new_img = np.clip(img,0,255)

        elif info['mode_params']['noise_type'] == '均匀噪声':
            noise = np.random.uniform(50,100,img.shape)
            img = img + noise
            new_img = np.clip(img, 0, 255)


        output_path = os.path.join(tempfile.gettempdir(), 'output.jpg')
        cv.imwrite(output_path, new_img, [int(cv.IMWRITE_JPEG_QUALITY), 100])
        
        return new_img, output_path


def imagefilter(info):
    img_array = np.frombuffer(info['image'], dtype=np.uint8)
    img = cv.imdecode(img_array, cv.IMREAD_COLOR)  # 始终以彩色图像读取
    if img is None:
        return None, None
        # 获取原始尺寸 (高度, 宽度)
    img=np.array(img)

    if info['mode_params']['filter_type'] == '高斯滤波':
        new_image = cv.GaussianBlur(img,ksize=(5,5),sigmaX=0,sigmaY=0)

    elif info['mode_params']['filter_type'] == '中值滤波':
        noise = np.random.normal(0,50,size=img.size).reshape(img.shape[0],img.shape[1],img.shape[2])
        img = img + noise
        img = np.clip(img,0,255)
        img = np.uint8(img)
        new_image = cv.medianBlur(img,3)
    
    elif info['mode_params']['filter_type'] == '均值滤波':
        noise = np.random.normal(0,50,size=img.size).reshape(img.shape[0],img.shape[1],img.shape[2])
        img = img + noise
        img = np.clip(img,0,255)
        img = np.uint8(img)
        new_image = cv.blur(img,(3,3))

    output_path = os.path.join(tempfile.gettempdir(), 'output.jpg')
    cv.imwrite(output_path, new_image, [int(cv.IMWRITE_JPEG_QUALITY), 100])
        
    return new_image, output_path

def imagecrop(info):
    x = int(info['mode_params']['x'])
    y = int(info['mode_params']['y'])
    crop_w = int(info['mode_params']['crop_w'])
    crop_h = int(info['mode_params']['crop_h'])
    img_array = np.frombuffer(info['image'], dtype=np.uint8)
    img = cv.imdecode(img_array, cv.IMREAD_COLOR)  # 始终以彩色图像读取
    if img is None:
        return None, None
        # 获取原始尺寸 (高度, 宽度)
    img=np.array(img)
    # 裁剪图像
    new_image = img[y:y+crop_h, x:x+crop_w]
    # 保存裁剪后的图像
    output_path = os.path.join(tempfile.gettempdir(), 'output.jpg')
    cv.imwrite(output_path, new_image, [int(cv.IMWRITE_JPEG_QUALITY), 100])
    # 返回裁剪后的图像和保存路径
    # 这里可以根据需要返回裁剪后的图像和保存路径
    # 例如，返回裁剪后的图像和保存路径
    return new_image, output_path

def imagehandle(info):
    mode = info['mode']
    if mode == '图像缩放':
        new_image ,output_path= imagescale(info)     

    if mode == '添加噪声':
        new_image, output_path = imagenoise(info)

    if mode == '滤波去噪':
        new_image , output_path = imagefilter(info)
    
    if mode == '图像裁剪':
        new_image , output_path = imagecrop(info)

    return new_image,output_path,mode