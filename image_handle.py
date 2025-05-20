import numpy as np
import cv2 as cv
from Bilinear_interpolation import double_biline
import os
import tempfile


def imagehandle(info):
    # 验证输入
    if not all(key in info for key in ['image', 'h', 'w']):
        return None, None
    try:
        # 直接从内存字节数据读取图像
        img_array = np.frombuffer(info['image']['content'], dtype=np.uint8)
        img = cv.imdecode(img_array, cv.IMREAD_COLOR)  # 始终以彩色图像读取
        
        if img is None:
            return None, None
        
        # 获取原始尺寸 (高度, 宽度)
        img=np.array(img)

        SSIZE=img.shape
        DSIZE = (int(info['h']), int(info['w']))
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
