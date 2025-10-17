import random
import numpy as np
import cv2 as cv
from Bilinear_interpolation import double_biline
import os
import tempfile


fdfj
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
            img = img/255 
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
        new_image = cv.GaussianBlur(img,(9,9),0)

    elif info['mode_params']['filter_type'] == '中值滤波':

        new_image = cv.medianBlur(img, 5)
    
    elif info['mode_params']['filter_type'] == '均值滤波':
        kernel_size = 3
# 使用均值滤波进行去噪
        denoised_image = cv.blur(img, (kernel_size, kernel_size))

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

def frequency_filter(info):
    img_array = np.frombuffer(info['image'], dtype=np.uint8)
    img = cv.imdecode(img_array, cv.IMREAD_GRAYSCALE)  # 读取为灰度图像
    if img is None:
        return None, None

    # 获取滤波参数
    filter_type = info['mode_params']['filter_type']
    filter_size = int(info['mode_params']['filter_size'])

    # 计算图像中心
    rows, cols = img.shape
    center_row, center_col = rows // 2, cols // 2

    # 进行傅里叶变换并中心化
    f1 = np.fft.fft2(img)
    f1shift = np.fft.fftshift(f1)

    # 创建滤波掩膜
    mask = np.zeros((rows, cols), dtype=np.float32)
    if filter_type == '低通滤波':
        # 中心区域为1，其他区域为0
        mask[center_row - filter_size // 2:center_row + filter_size // 2,
             center_col - filter_size // 2:center_col + filter_size // 2] = 1
    elif filter_type == '高通滤波':
        # 中心区域为0，其他区域为1
        mask[:, :] = 1
        mask[center_row - filter_size // 2:center_row + filter_size // 2,
             center_col - filter_size // 2:center_col + filter_size // 2] = 0

    # 应用掩膜进行滤波
    f1shift_filtered = f1shift * mask

    # 逆中心化并进行逆傅里叶变换
    f2 = np.fft.ifftshift(f1shift_filtered)
    img_new = np.fft.ifft2(f2)

    # 取绝对值并归一化到0-255
    img_new = np.abs(img_new)
    img_new = np.uint8(255 * (img_new - np.min(img_new)) / (np.max(img_new) - np.min(img_new)))

    # 保存结果到临时文件
    output_path = os.path.join(tempfile.gettempdir(), 'output.jpg')
    cv.imwrite(output_path, img_new)

    return img_new, output_path



def reconstruct_image_from_spectra(magnitude_spectrum, phase_spectrum):
    """
    使用幅度谱和相位谱重构原图像
    """
    try:
        # 将幅度谱和相位谱转换回频谱
        magnitude = np.exp(magnitude_spectrum) - 1  # 还原取对数前的幅度谱
        phase = (phase_spectrum / 255.0) * (2 * np.pi) - np.pi  # 将相位谱还原到 [-π, π]
        f1shift = magnitude * np.exp(1j * phase)  # 组合成复数频谱

        # 逆中心化并进行逆傅里叶变换
        f2 = np.fft.ifftshift(f1shift)
        img_reconstructed = np.fft.ifft2(f2)

        # 取绝对值并归一化到 0-255
        img_reconstructed = np.abs(img_reconstructed)
        img_reconstructed = np.uint8(255 * (img_reconstructed - np.min(img_reconstructed)) /
                                     (np.max(img_reconstructed) - np.min(img_reconstructed)))

        return img_reconstructed

    except Exception as e:
        print(f"重构图像时发生错误: {e}")
        return None
    
def Spectral_decomposition(info):
    img_array = np.frombuffer(info['image'], dtype=np.uint8)
    img = cv.imdecode(img_array, cv.IMREAD_GRAYSCALE)  # 读取为灰度图像
    if img is None:
        return None, None

    # 进行傅里叶变换并中心化
    f1 = np.fft.fft2(img)
    f1shift = np.fft.fftshift(f1)

    # 计算幅度谱和相位谱
    magnitude_spectrum = np.abs(f1shift)
    phase_spectrum = np.angle(f1shift)

    # 对幅度谱取对数并归一化到 0-255
    magnitude_spectrum_log = np.log(1 + magnitude_spectrum)  # 取对数
    magnitude_spectrum_normalized = np.uint8(255 * (magnitude_spectrum_log - np.min(magnitude_spectrum_log)) /
                                             (np.max(magnitude_spectrum_log) - np.min(magnitude_spectrum_log)))

    # 将相位谱平移到 0-255
    phase_spectrum_normalized = (phase_spectrum + np.pi) / (2 * np.pi)  # 将范围从 [-π, π] 映射到 [0, 1]
    phase_spectrum_normalized = np.uint8(255 * phase_spectrum_normalized)

    # 使用幅度谱和相位谱重构原图像
    img_reconstructed = reconstruct_image_from_spectra(magnitude_spectrum_log, phase_spectrum_normalized)

    # 保存幅度谱、相位谱和重构图像到临时文件
    output_path_magnitude = os.path.join(tempfile.gettempdir(), 'magnitude_spectrum.jpg')
    output_path_phase = os.path.join(tempfile.gettempdir(), 'phase_spectrum.jpg')
    output_path_reconstructed = os.path.join(tempfile.gettempdir(), 'reconstructed_image.jpg')
    cv.imwrite(output_path_magnitude, magnitude_spectrum_normalized)
    cv.imwrite(output_path_phase, phase_spectrum_normalized)
    cv.imwrite(output_path_reconstructed, img_reconstructed)

    # 返回结果
    new_image = {'magnitude_spectrum': magnitude_spectrum_normalized,
                 'phase_spectrum': phase_spectrum_normalized,
                 'reconstructed_image': img_reconstructed}
    output_path = {'magnitude_spectrum': output_path_magnitude,
                   'phase_spectrum': output_path_phase,
                   'reconstructed_image': output_path_reconstructed}
    return new_image, output_path 

def imagehandle(info):

    mode = info['mode']

    if mode == '图像缩放':
        new_image ,output_path = imagescale(info)     

    if mode == '添加噪声':
        new_image, output_path = imagenoise(info)

    if mode == '滤波去噪':
        new_image , output_path = imagefilter(info)
    
    if mode == '图像裁剪':
        new_image , output_path = imagecrop(info)

    if mode == '频域滤波':
        new_image , output_path = frequency_filter(info)
    
    if mode == '频谱分解':
        new_image, output_path = Spectral_decomposition(info)

    return new_image,output_path,mode
