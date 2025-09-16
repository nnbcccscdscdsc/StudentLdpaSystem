#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证码生成工具
"""

import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from flask import session

def generate_captcha_text(length=4):
    """生成验证码文本"""
    # 使用数字和字母，排除容易混淆的字符
    chars = string.ascii_uppercase + string.digits
    # 排除容易混淆的字符
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(random.choice(chars) for _ in range(length))

def create_captcha_image(text, width=120, height=40):
    """创建验证码图片"""
    # 创建图片
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    except:
        try:
            font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 24)
        except:
            font = ImageFont.load_default()
    
    # 绘制背景干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)), width=1)
    
    # 绘制验证码文字
    char_width = width // len(text)
    for i, char in enumerate(text):
        x = i * char_width + random.randint(5, 15)
        y = random.randint(5, 15)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, font=font, fill=color)
    
    # 添加噪点
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    return img

def generate_captcha():
    """生成验证码并返回base64编码的图片"""
    # 生成验证码文本
    captcha_text = generate_captcha_text()
    
    # 将验证码文本存储到session中
    session['captcha'] = captcha_text.lower()
    
    # 创建验证码图片
    img = create_captcha_image(captcha_text)
    
    # 转换为base64编码
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_captcha(user_input):
    """验证用户输入的验证码"""
    if 'captcha' not in session:
        return False
    
    stored_captcha = session.get('captcha', '').lower()
    user_captcha = user_input.lower().strip()
    
    # 验证结果
    is_valid = stored_captcha == user_captcha
    
    # 验证后清除session中的验证码（无论成功失败都清除）
    session.pop('captcha', None)
    
    return is_valid
