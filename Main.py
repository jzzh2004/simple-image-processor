from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio import start_server
from image_handle import imagehandle 
import os
import subprocess
import threading
import time
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def validate_image_params(mode_params, mode):
    """验证输入参数的合法性"""
    if mode == '图像缩放':
        height = mode_params.get('height', 0)
        width = mode_params.get('width', 0)
        if height <= 0 or width <= 0:
            return False, "高度和宽度必须大于0"
        if height > 4000 or width > 4000:
            return False, "高度和宽度不能超过4000像素"
    
    elif mode == '图像裁剪':
        x = mode_params.get('x', -1)
        y = mode_params.get('y', -1) 
        crop_w = mode_params.get('crop_w', 0)
        crop_h = mode_params.get('crop_h', 0)
        if x < 0 or y < 0:
            return False, "起始坐标不能为负数"
        if crop_w <= 0 or crop_h <= 0:
            return False, "裁剪宽度和高度必须大于0"
        if crop_w > 2000 or crop_h > 2000:
            return False, "裁剪尺寸不能超过2000像素"
    
    elif mode == '频域滤波':
        filter_size = mode_params.get('filter_size', 0)
        if filter_size <= 0:
            return False, "滤波器大小必须大于0"
        if filter_size > 200:
            return False, "滤波器大小不能超过200"
    
    elif mode == '边缘检测':
        threshold1 = mode_params.get('threshold1', 0)
        threshold2 = mode_params.get('threshold2', 0)
        if mode_params.get('edge_type') == 'Canny边缘检测':
            if threshold1 <= 0 or threshold2 <= 0:
                return False, "阈值必须大于0"
            if threshold1 >= threshold2:
                return False, "低阈值必须小于高阈值"
    
    elif mode == '二维DFT可视化':
        block_size = mode_params.get('block_size', 0)
        if block_size < 8 or block_size > 128:
            return False, "块大小必须在8-128之间"
        if block_size & (block_size - 1) != 0:
            return False, "块大小必须是2的幂次方（8, 16, 32, 64, 128）"
    
    return True, ""

def setup_localtunnel():
    """设置localtunnel创建公网链接"""
    def run_localtunnel():
        try:
            result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("💡 提示：需要安装Node.js来使用localtunnel创建公网链接")
                print("下载地址：https://nodejs.org/")
                return
            
            time.sleep(3)
            print("🔗 正在创建公网访问链接...")
            process = subprocess.Popen(
                ['npx', 'localtunnel', '--port', '8080'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for line in process.stdout:
                if 'your url is:' in line.lower():
                    url = line.strip().split()[-1]
                    print(f"🌐 公网访问地址: {url}")
                    print("📝 注意：首次访问可能需要点击'Click to Continue'")
                    break
                    
        except FileNotFoundError:
            print("💡 提示：安装Node.js后可以使用以下命令创建公网链接：")
            print("npx localtunnel --port 8080")
        except Exception as e:
            print(f"⚠️ localtunnel启动失败: {e}")
            print("💡 备选方案：可以手动运行 'npx localtunnel --port 8080'")
    
    thread = threading.Thread(target=run_localtunnel, daemon=True)
    thread.start()

def main_interface():
    """主界面"""
    clear()
    
    # 美化的标题页面
    put_html('''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 60px 20px; margin: -20px -20px 40px -20px; text-align: center; color: white; border-radius: 0 0 20px 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
        <h1 style="margin: 0; font-size: 3.5em; font-weight: 300; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🖼️ 数字图像处理系统</h1>
        <p style="margin: 20px 0 0 0; font-size: 1.4em; opacity: 0.9; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">Digital Image Processing Laboratory</p>
        <div style="margin-top: 30px; font-size: 1em; opacity: 0.85; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);">
            <span style="margin: 0 20px; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px;">📊 空域处理</span>
            <span style="margin: 0 20px; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px;">🌊 频域分析</span>
            <span style="margin: 0 20px; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px;">🔍 图像增强</span>
        </div>
    </div>
    ''')
    
    with use_scope('main_content'):
        # 功能特色展示
        put_html('''
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-bottom: 40px;">
            <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e0e7ff 100%); border-left: 5px solid #6366f1; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(99,102,241,0.1); transition: transform 0.3s ease;">
                <h3 style="color: #6366f1; margin-top: 0; font-size: 1.3em; display: flex; align-items: center;"><span style="margin-right: 10px;">🎨</span>空域处理</h3>
                <p style="color: #64748b; margin-bottom: 0; line-height: 1.6;">图像缩放、噪声处理、滤波去噪等经典空域算法</p>
            </div>
            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-left: 5px solid #10b981; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(16,185,129,0.1); transition: transform 0.3s ease;">
                <h3 style="color: #10b981; margin-top: 0; font-size: 1.3em; display: flex; align-items: center;"><span style="margin-right: 10px;">🌊</span>频域分析</h3>
                <p style="color: #64748b; margin-bottom: 0; line-height: 1.6;">DFT可视化、频谱分解、频域滤波等高级算法</p>
            </div>
            <div style="background: linear-gradient(135deg, #fef7ff 0%, #f3e8ff 100%); border-left: 5px solid #a855f7; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(168,85,247,0.1); transition: transform 0.3s ease;">
                <h3 style="color: #a855f7; margin-top: 0; font-size: 1.3em; display: flex; align-items: center;"><span style="margin-right: 10px;">✨</span>图像增强</h3>
                <p style="color: #64748b; margin-bottom: 0; line-height: 1.6;">直方图均衡化、边缘检测等图像质量提升算法</p>
            </div>
        </div>
        ''')
        
        # 模式选择
        put_html('''
        <div style="background: white; padding: 35px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px; border: 1px solid #e2e8f0;">
            <h3 style="color: #1e293b; margin-top: 0; font-size: 1.5em; display: flex; align-items: center; margin-bottom: 25px;">
                <span style="margin-right: 15px; font-size: 1.2em;">🎛️</span>选择处理模式
            </h3>
        </div>
        ''')
        
        mode = select("", [
            {'label': '📏 图像缩放', 'value': '图像缩放'},
            {'label': '🔊 添加噪声', 'value': '添加噪声'},
            {'label': '🧹 滤波去噪', 'value': '滤波去噪'},
            {'label': '✂️ 图像裁剪', 'value': '图像裁剪'},
            {'label': '🌊 频域滤波', 'value': '频域滤波'},
            {'label': '📊 频谱分解', 'value': '频谱分解'},
            {'label': '📈 直方图均衡化', 'value': '直方图均衡化'},
            {'label': '🔍 边缘检测', 'value': '边缘检测'},
            {'label': '🎯 二维DFT可视化', 'value': '二维DFT可视化'}
        ])
        
        put_success(f"✅ 已选择模式：{mode}")
        
        # 图像上传
        put_html('''
        <div style="background: white; padding: 35px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 30px 0; border: 1px solid #e2e8f0;">
            <h3 style="color: #1e293b; margin-top: 0; font-size: 1.5em; display: flex; align-items: center; margin-bottom: 25px;">
                <span style="margin-right: 15px; font-size: 1.2em;">📁</span>上传待处理图像
            </h3>
        </div>
        ''')
        
        image = file_upload("", accept="image/*", help_text="支持 JPG, PNG, BMP 等格式，文件大小不超过10MB")
        
        if not image:
            put_error("❌ 请选择图片文件！")
            return
        
        if len(image['content']) > 10 * 1024 * 1024:
            put_error("❌ 图片文件大小不能超过10MB！")
            return
        
        put_success("✅ 图片上传成功")
        
        # 参数设置
        put_html('''
        <div style="background: white; padding: 35px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 30px 0; border: 1px solid #e2e8f0;">
            <h3 style="color: #1e293b; margin-top: 0; font-size: 1.5em; display: flex; align-items: center; margin-bottom: 25px;">
                <span style="margin-right: 15px; font-size: 1.2em;">⚙️</span>算法参数设置
            </h3>
        </div>
        ''')
        
        mode_params = get_mode_parameters(mode)
        
        # 参数验证
        if mode_params:
            valid, error_msg = validate_image_params(mode_params, mode)
            if not valid:
                put_error(f"❌ 参数错误：{error_msg}")
                return
        
        # 处理图像
        put_html('''
        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fcd34d 100%); padding: 40px; border-radius: 20px; text-align: center; margin: 30px 0; box-shadow: 0 10px 30px rgba(252,211,77,0.2); border: 1px solid #f59e0b;">
            <h3 style="color: #92400e; margin: 0; font-size: 1.6em; display: flex; align-items: center; justify-content: center;">
                <span style="margin-right: 15px; animation: spin 2s linear infinite;">🔄</span>正在处理图像...
            </h3>
            <p style="color: #92400e; margin: 15px 0 0 0; opacity: 0.8; font-size: 1.1em;">请稍候，算法正在运行中</p>
        </div>
        <style>
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        </style>
        ''')
        
        info = {
            'mode': mode,
            'image': image['content'],
            'mode_params': mode_params,
            'original_image': image['content']  # 保存原始图像
        }
        
        try:
            new_image, output_path, processed_mode = imagehandle(info)
            output_handle(new_image, output_path, processed_mode, image['content'])
        except Exception as e:
            put_error(f"❌ 图像处理失败：{str(e)}")

def get_mode_parameters(mode):
    """根据模式获取参数"""
    mode_params = None
    
    if mode == '图像缩放':
        mode_params = input_group("", [
            input('目标高度 (像素):', name='height', type=NUMBER, required=True, 
                  help_text="建议范围：50-4000像素"),
            input('目标宽度 (像素):', name='width', type=NUMBER, required=True,
                  help_text="建议范围：50-4000像素"),
        ])
    elif mode == '添加噪声':
        mode_params = input_group("", [
            select('噪声类型:', 
                   options=[
                       {'label': '🔔 高斯噪声', 'value': '高斯噪声'},
                       {'label': '⚫ 椒盐噪声', 'value': '椒盐噪声'},
                       {'label': '📊 泊松噪声', 'value': '泊松噪声'},
                       {'label': '📈 均匀噪声', 'value': '均匀噪声'}
                   ], 
                   name='noise_type')
        ])
    elif mode == '滤波去噪':
        mode_params = input_group("", [
            select('滤波方法:', 
                   options=[
                       {'label': '🌊 高斯滤波', 'value': '高斯滤波'},
                       {'label': '📊 中值滤波', 'value': '中值滤波'},
                       {'label': '📈 均值滤波', 'value': '均值滤波'}
                   ], 
                   name='filter_type'),
        ])
    elif mode == '图像裁剪':
        mode_params = input_group("", [
            input('起始X坐标:', name='x', type=NUMBER, required=True,
                  help_text="从0开始"),
            input('起始Y坐标:', name='y', type=NUMBER, required=True,
                  help_text="从0开始"),
            input('裁剪宽度:', name='crop_w', type=NUMBER, required=True,
                  help_text="建议范围：10-2000像素"),
            input('裁剪高度:', name='crop_h', type=NUMBER, required=True,
                  help_text="建议范围：10-2000像素")
        ])
    elif mode == '频域滤波':
        put_info("🌊 频域滤波：在频率域进行滤波操作，可以有效去除特定频率的噪声")
        mode_params = input_group("", [
            select('滤波类型:', 
                   options=[
                       {'label': '🔽 低通滤波', 'value': '低通滤波'},
                       {'label': '🔼 高通滤波', 'value': '高通滤波'}
                   ], 
                   name='filter_type'),
            input('滤波器大小:', name='filter_size', type=NUMBER, required=True,
                  help_text="建议范围：5-200")
        ])
    elif mode == '频谱分解':
        put_info("📊 频谱分解：将图像分解为幅度谱和相位谱，并尝试重构原图像")
    elif mode == '直方图均衡化':
        put_info("📈 直方图均衡化：增强图像对比度，改善图像的视觉效果")
    elif mode == '边缘检测':
        mode_params = input_group("", [
            select('边缘检测方法:', 
                   options=[
                       {'label': '🔍 Sobel边缘检测', 'value': 'Sobel边缘检测'},
                       {'label': '✨ Canny边缘检测', 'value': 'Canny边缘检测'},
                       {'label': '📊 Laplacian边缘检测', 'value': 'Laplacian边缘检测'}
                   ], 
                   name='edge_type'),
            input('低阈值 (仅Canny):', name='threshold1', type=NUMBER, value=50,
                  help_text="Canny边缘检测的低阈值"),
            input('高阈值 (仅Canny):', name='threshold2', type=NUMBER, value=150,
                  help_text="Canny边缘检测的高阈值")
        ])
    elif mode == '二维DFT可视化':
        put_info("🎯 二维DFT可视化：对图像进行二维离散傅里叶变换，可视化频域特性")
        mode_params = input_group("", [
        select('分析范围:', 
               options=[
                   {'label': '🖼️ 整张图片', 'value': 'full_image'},
                   {'label': '🎯 中心图像块', 'value': 'center_block'}
               ], 
               name='analysis_scope'),
        select('分析块大小 (仅中心块模式):', 
               options=[
                   {'label': '8×8', 'value': 8},
                   {'label': '16×16', 'value': 16},
                   {'label': '32×32 (推荐)', 'value': 32},
                   {'label': '64×64', 'value': 64},
                   {'label': '128×128', 'value': 128}
               ], 
               name='block_size'),
        select('可视化类型:', 
               options=[
                   {'label': '📊 幅度谱', 'value': '幅度谱'},
                   {'label': '🌊 相位谱', 'value': '相位谱'},
                   {'label': '📈 实部', 'value': '实部'},
                   {'label': '📉 虚部', 'value': '虚部'},
                   {'label': '⚡ 功率谱', 'value': '功率谱'}
               ], 
               name='visualization_type')
    ])
    
    return mode_params

def output_handle(new_image, output_path, mode, original_image_content):
    """处理输出结果"""
    clear()
    
    if new_image is None:
        put_html('''
        <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); padding: 50px; text-align: center; border-radius: 20px; box-shadow: 0 10px 30px rgba(239,68,68,0.2);">
            <h1 style="color: #dc2626; margin: 0; font-size: 2.5em;">❌ 处理失败</h1>
            <p style="color: #dc2626; margin: 20px 0 0 0; font-size: 1.2em;">图像处理过程中发生错误，请检查输入参数或重新尝试</p>
        </div>
        ''')
        put_html('<div style="text-align: center; margin-top: 30px;">')
        put_button("🏠 返回首页", onclick=main_interface, color='primary')
        put_html('</div>')
        return
    
    # 成功页面标题
    put_html(f'''
    <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); padding: 50px; text-align: center; border-radius: 20px; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(34,197,94,0.2);">
        <h1 style="color: #16a34a; margin: 0; font-size: 2.8em; font-weight: 300;">✅ {mode} 完成！</h1>
        <p style="color: #16a34a; margin: 20px 0 0 0; font-size: 1.3em; opacity: 0.9;">图像处理成功，以下是对比结果</p>
    </div>
    ''')
    
    # 显示原始图像和处理结果的对比
    if mode in ['频谱分解', '二维DFT可视化']:
        handle_complex_output_with_comparison(new_image, output_path, mode, original_image_content)
    else:
        handle_simple_output_with_comparison(new_image, output_path, mode, original_image_content)
    
    # 返回首页按钮
    put_html('''
    <div style="text-align: center; margin-top: 50px; padding: 30px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.05);">
        <p style="color: #64748b; margin-bottom: 20px; font-size: 1.2em;">✨ 处理完成！您可以下载结果或返回继续处理其他图像</p>
    </div>
    ''')
    put_html('<div style="text-align: center; margin-top: 25px;">')
    put_button("🏠 返回首页", onclick=main_interface, color='primary')
    put_html('</div>')

def handle_complex_output_with_comparison(new_image, output_path, mode, original_image_content):
    """处理复杂输出结果（带原图对比）"""
    if mode == '频谱分解':
        put_html('''
        <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px;">
            <h3 style="color: #1e293b; margin-top: 0; font-size: 1.6em; display: flex; align-items: center;">
                <span style="margin-right: 12px;">📊</span>频谱分解结果
            </h3>
        </div>
        ''')
        
        # 显示原始图像
        put_html('<div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); margin-bottom: 25px;">')
        put_html('<h4 style="color: #374151; margin-top: 0; display: flex; align-items: center; font-size: 1.2em;"><span style="margin-right: 10px;">🖼️</span>原始图像</h4>')
        put_image(original_image_content)
        put_html('</div>')
        
        # 处理结果
        sections = [
            ('magnitude_spectrum', '幅度谱', '显示图像的频率成分强度分布'),
            ('phase_spectrum', '相位谱', '显示图像的相位信息'),
            ('reconstructed_image', '重构图像', '使用幅度谱和相位谱重构的图像')
        ]
        
        for key, title, desc in sections:
            put_html('<div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); margin-bottom: 25px;">')
            put_html(f'<h4 style="color: #374151; margin-top: 0; display: flex; align-items: center; font-size: 1.2em;"><span style="margin-right: 10px;">📈</span>{title}</h4>')
            put_html(f'<p style="color: #6b7280; margin-bottom: 20px; font-size: 1em; line-height: 1.6;">{desc}</p>')
            put_image(open(output_path[key], 'rb').read())
            put_file(f'{key}.jpg', open(output_path[key], 'rb').read(), f'📥 下载{title}')
            put_html('</div>')
        
        # 清理临时文件
        for key, path in output_path.items():
            if os.path.exists(path):
                os.unlink(path)
                
    elif mode == '二维DFT可视化':
        put_html('''
        <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px;">
            <h3 style="color: #1e293b; margin-top: 0; font-size: 1.6em; display: flex; align-items: center;">
                <span style="margin-right: 12px;">🎯</span>二维DFT可视化结果
            </h3>
        </div>
        ''')
        
        # 显示原始图像
        put_html('<div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); margin-bottom: 25px;">')
        put_html('<h4 style="color: #374151; margin-top: 0; display: flex; align-items: center; font-size: 1.2em;"><span style="margin-right: 10px;">🖼️</span>原始完整图像</h4>')
        put_image(original_image_content)
        put_html('</div>')
        
        sections = [
            ('original_block', '提取的图像块', '用于DFT分析的图像区域'),
            ('dft_visualization', 'DFT可视化结果', '频域特性的可视化展示'),
            ('dft_3d', 'DFT三维可视化', '频域特性的三维立体展示')
        ]
        
        for key, title, desc in sections:
            put_html('<div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); margin-bottom: 25px;">')
            put_html(f'<h4 style="color: #374151; margin-top: 0; display: flex; align-items: center; font-size: 1.2em;"><span style="margin-right: 10px;">📊</span>{title}</h4>')
            put_html(f'<p style="color: #6b7280; margin-bottom: 20px; font-size: 1em; line-height: 1.6;">{desc}</p>')
            put_image(open(output_path[key], 'rb').read())
            put_file(f'{key}.jpg', open(output_path[key], 'rb').read(), f'📥 下载{title}')
            put_html('</div>')
        
        # 清理临时文件
        for key, path in output_path.items():
            if os.path.exists(path):
                os.unlink(path)

def handle_simple_output_with_comparison(new_image, output_path, mode, original_image_content):
    """处理简单输出结果（带原图对比）"""
    put_html('''
    <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px;">
        <h3 style="color: #1e293b; margin-top: 0; font-size: 1.6em; display: flex; align-items: center;">
            <span style="margin-right: 12px;">📊</span>处理结果对比
        </h3>
    </div>
    ''')
    
    # 使用网格布局显示对比
    put_html('''
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
    ''')
    
    # 原始图像
    put_html('''
    <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); border: 2px solid #e2e8f0;">
        <h4 style="color: #374151; margin-top: 0; text-align: center; display: flex; align-items: center; justify-content: center; font-size: 1.3em;">
            <span style="margin-right: 10px;">🖼️</span>原始图像
        </h4>
    ''')
    put_image(original_image_content)
    put_html('</div>')
    
    # 处理结果
    put_html(f'''
    <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); border: 2px solid #10b981;">
        <h4 style="color: #10b981; margin-top: 0; text-align: center; display: flex; align-items: center; justify-content: center; font-size: 1.3em;">
            <span style="margin-right: 10px;">✨</span>{mode}结果
        </h4>
    ''')
    put_image(open(output_path, 'rb').read())
    put_html('</div>')
    
    put_html('</div>')  # 结束网格布局
    
    # 下载区域
    put_html('''
    <div style="background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
        <h4 style="color: #475569; margin-top: 0; font-size: 1.2em;">📥 下载处理结果</h4>
    ''')
    
    # 根据模式设置下载文件名和图标
    file_configs = {
        '图像缩放': ('resized_image.jpg', '📏'),
        '添加噪声': ('noisy_image.jpg', '🔊'), 
        '滤波去噪': ('filtered_image.jpg', '🧹'),
        '图像裁剪': ('cropped_image.jpg', '✂️'),
        '频域滤波': ('frequency_filtered.jpg', '🌊'),
        '直方图均衡化': ('equalized_image.jpg', '📈'),
        '边缘检测': ('edge_detected.jpg', '🔍')
    }
    
    filename, icon = file_configs.get(mode, ('processed_image.jpg', '📊'))
    put_file(filename, open(output_path, 'rb').read(), f'{icon} 下载{mode}后的图像')
    put_html('</div>')
    
    # 清理临时文件
    if output_path and os.path.exists(output_path):
        os.unlink(output_path)

def start_app():
    """启动应用"""
    try:
        setup_localtunnel()
        main_interface()
    except KeyboardInterrupt:
        print("\n👋 程序已退出")

if __name__ == '__main__':
    start_server(
        applications=start_app,
        debug=True,
        auto_open_webbrowser=True,
        port=8080
    )