from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio import start_server
from image_handle import imagehandle 
import os
def inputhandle():
    # input的合法性校验
    # 自定义校验函数 
    # 获取用户输入
    mode = select("请选择图像处理模式:",['图像缩放','添加噪声','滤波去噪','图像裁剪','频域滤波'])
    put_text("你选择的模式：",mode)
    # 公共输入：上传图像
    image = file_upload("选择你要处理的图片:",accept="image/*")
    put_text("已提交图片")
    # 根据模式动态添加专属参数
    if mode == '图像缩放':
        # 缩放模式参数
        mode_params = input_group("缩放参数", [
            input('目标高度 (像素):', name='height', type=NUMBER, required=True),
            input('目标宽度 (像素):', name='width', type=NUMBER, required=True),
        ])
    elif mode == '添加噪声':
        # 噪声模式参数
       mode_params = input_group("噪声参数", [
            select('噪声类型:', 
           options=['高斯噪声', '椒盐噪声','泊松噪声','均匀噪声'], 
           name='noise_type')
])

    elif mode == '滤波去噪':
        # 去噪模式参数
        mode_params = input_group("去噪参数", [
            select('滤波方法:', 
                   options=['高斯滤波', '中值滤波', '均值滤波'], 
                   name='filter_type'),])
    elif mode == '图像裁剪':
        # 裁剪模式参数
        mode_params = input_group("裁剪参数", [
            input('起始X坐标:', name='x', type=NUMBER, required=True),
            input('起始Y坐标:', name='y', type=NUMBER, required=True),
            input('裁剪宽度:', name='crop_w', type=NUMBER, required=True),
            input('裁剪高度:', name='crop_h', type=NUMBER, required=True)
        ])
    elif mode == '频域滤波':
        mode_params = input_group("频域滤波参数", [
            select('滤波类型:', 
                   options=['低通滤波', '高通滤波'], 
                   name='filter_type'),
            input('滤波器大小:', name='filter_size', type=NUMBER, required=True)
        ])
    else :
        put_error("how can you go there?")   #已完成输出，输入整理尚未完成 

    # 合并所有输入
    info = {
        'mode': mode,
        'image': image['content'],  # 文件对象
        'mode_params': mode_params
    }
    return info

def output_handle(new_image , output_path,mode):
    if new_image is None:
        put_error('图像处理失败！')
        return

    if mode == '图像缩放':
        put_success("图像缩放完成!")
        put_image(open(output_path, 'rb').read())
        # 提供下载
        put_file('resized_image.jpg', 
                open(output_path, 'rb').read(), 
                '下载缩放后的图像')
        
    if mode == '添加噪声':
        put_success("图像添加噪声完成!")
        put_image(open(output_path, 'rb').read())
        # 提供下载
        put_file('resized_image.jpg', 
                open(output_path, 'rb').read(), 
                '下载添加噪声后的图像')

    if mode == '滤波去噪':
        put_success("图像去噪完成!")
        put_image(open(output_path, 'rb').read())
        # 提供下载
        put_file('resized_image.jpg', 
                open(output_path, 'rb').read(), 
                '下载去噪后的图像')

    if mode == '图像裁剪':
        put_success("图像裁剪完成!")
        put_image(open(output_path, 'rb').read())
        # 提供下载
        put_file('resized_image.jpg', 
                open(output_path, 'rb').read(), 
                '下载裁剪后的图像')
    
    if mode == '频域滤波':
        put_success("频域滤波完成!")
        put_image(open(output_path, 'rb').read())
        # 提供下载
        put_file('resized_image.jpg', 
                open(output_path, 'rb').read(), 
                '下载频域滤波后的图像')

    if output_path and os.path.exists(output_path):
            os.unlink(output_path)


if __name__ == '__main__':
    start_server(
        applications=inputhandle,
        debug=True,
        auto_open_webbrowser=True,
        port=8080
    )