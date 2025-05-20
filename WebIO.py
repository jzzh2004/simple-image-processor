from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio import start_server
from image_handle import imagehandle 
import os
def handle():
    # input的合法性校验
    # 自定义校验函数 
    # 获取用户输入
    info = input_group("图像缩放工具",[
        file_upload("选择你要进行缩放的图片:", 
                   accept="image/*", 
                   name='image', 
                   required=True),
        input('输入缩放后图片的高度:', 
             name='h', 
             type=NUMBER, 
             required=True,
             ),
        input('输入缩放后图片的宽度:', 
             name='w', 
             type=NUMBER, 
             required=True,
             )
    ])
    
    resized_img, output_path = imagehandle(info)
    
    if resized_img is None:
        put_error("图像处理失败!")
        return
    
    try:
        # 显示结果
        put_success("图像缩放完成!")
        put_image(open(output_path, 'rb').read())
        
        # 提供下载
        put_file('resized_image.jpg', 
                open(output_path, 'rb').read(), 
                '下载缩放后的图像')
    finally:
        # 清理结果文件
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)

if __name__ == '__main__':
    start_server(
        applications=handle,
        auto_open_webbrowser=True,
    )