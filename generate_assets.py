"""
Hello Kitty 动画序列帧生成器
生成带透明通道的高清像素/卡通风格动作帧：
- idle (待机呼吸)
- walk (走步)
- cute (卖萌，眨眼、害羞腮红、爱心)
- middle_finger (搞笑反差：举起爪子比中指，傲娇白眼/怒气符号)
- drag (被拎起，四肢扑腾)
"""

import os
import math
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

def ensure_dirs():
    states = ["idle", "walk", "cute", "middle_finger", "drag"]
    for s in states:
        d = os.path.join(ASSETS_DIR, s)
        os.makedirs(d, exist_ok=True)

def draw_kitty_base(draw, ox=0, oy=0, eye_type="normal", blush=False, body_tilt=0, leg_offset=(0, 0)):
    """
    绘制 Hello Kitty 基础外形 (128x128 画布)
    ox, oy: 头部微调偏移
    """
    # 颜色定义
    WHITE = (255, 255, 255, 255)
    BLACK = (30, 30, 30, 255)
    YELLOW = (255, 215, 0, 255)
    RED = (235, 45, 60, 255)
    DARK_RED = (180, 25, 40, 255)
    BLUE = (65, 120, 225, 255)
    PINK = (255, 160, 180, 200)

    # 1. 身体 (蓝色背带裤 + 黄纽扣)
    body_x = 64
    body_y = 90 + oy
    
    # 腿部/脚
    lx_off, rx_off = leg_offset
    # 左脚
    draw.ellipse([body_x - 22 + lx_off, body_y + 16, body_x - 6 + lx_off, body_y + 26], fill=WHITE, outline=BLACK, width=3)
    # 右脚
    draw.ellipse([body_x + 6 + rx_off, body_y + 16, body_x + 22 + rx_off, body_y + 26], fill=WHITE, outline=BLACK, width=3)

    # 身体躯干 (蓝色背带衣)
    draw.ellipse([body_x - 20, body_y - 8, body_x + 20, body_y + 20], fill=BLUE, outline=BLACK, width=3)
    # 红色内搭衬衫领口
    draw.ellipse([body_x - 12, body_y - 12, body_x + 12, body_y + 2], fill=RED, outline=BLACK, width=2)
    # 背带裤黄色扣子
    draw.ellipse([body_x - 10, body_y + 2, body_x - 6, body_y + 6], fill=YELLOW, outline=BLACK, width=1)
    draw.ellipse([body_x + 6, body_y + 2, body_x + 10, body_y + 6], fill=YELLOW, outline=BLACK, width=1)

    # 2. 头部 (横向椭圆 + 猫耳朵)
    hx = 64 + ox
    hy = 52 + oy

    # 耳朵 (左耳与右耳)
    # 左耳
    draw.polygon([(hx - 36, hy - 16), (hx - 44, hy - 40), (hx - 20, hy - 32)], fill=WHITE, outline=BLACK)
    draw.line([(hx - 36, hy - 16), (hx - 44, hy - 40), (hx - 20, hy - 32)], fill=BLACK, width=3)
    # 右耳
    draw.polygon([(hx + 20, hy - 32), (hx + 44, hy - 40), (hx + 36, hy - 16)], fill=WHITE, outline=BLACK)
    draw.line([(hx + 20, hy - 32), (hx + 44, hy - 40), (hx + 36, hy - 16)], fill=BLACK, width=3)

    # 头部大椭圆
    draw.ellipse([hx - 45, hy - 30, hx + 45, hy + 30], fill=WHITE, outline=BLACK, width=3)

    # 修复耳朵与头部接缝内侧的线，用白色遮盖
    draw.polygon([(hx - 34, hy - 17), (hx - 42, hy - 38), (hx - 22, hy - 31)], fill=WHITE)
    draw.polygon([(hx + 22, hy - 31), (hx + 42, hy - 38), (hx + 34, hy - 17)], fill=WHITE)

    # 3. 经典红蝴蝶结 (左耳下方偏上, 观众视角的左上方)
    bow_x = hx - 26
    bow_y = hy - 25
    # 蝴蝶结左叶
    draw.ellipse([bow_x - 16, bow_y - 12, bow_x - 2, bow_y + 8], fill=RED, outline=BLACK, width=2)
    # 蝴蝶结右叶
    draw.ellipse([bow_x + 2, bow_y - 12, bow_x + 16, bow_y + 8], fill=RED, outline=BLACK, width=2)
    # 蝴蝶结中心圆
    draw.ellipse([bow_x - 7, bow_y - 6, bow_x + 7, bow_y + 6], fill=DARK_RED, outline=BLACK, width=2)

    # 4. 面部五官
    # 眼睛
    if eye_type == "normal":
        draw.ellipse([hx - 23, hy - 3, hx - 17, hy + 7], fill=BLACK)
        draw.ellipse([hx + 17, hy - 3, hx + 23, hy + 7], fill=BLACK)
    elif eye_type == "blink":
        draw.line([hx - 25, hy + 2, hx - 15, hy + 2], fill=BLACK, width=3)
        draw.line([hx + 15, hy + 2, hx + 25, hy + 2], fill=BLACK, width=3)
    elif eye_type == "happy":
        draw.arc([hx - 26, hy - 6, hx - 14, hy + 6], start=200, end=340, fill=BLACK, width=3)
        draw.arc([hx + 14, hy - 6, hx + 26, hy + 6], start=200, end=340, fill=BLACK, width=3)
    elif eye_type == "grumpy":
        draw.line([hx - 25, hy, hx - 15, hy + 3], fill=BLACK, width=3)
        draw.ellipse([hx - 22, hy + 1, hx - 17, hy + 6], fill=BLACK)
        draw.line([hx + 25, hy, hx + 15, hy + 3], fill=BLACK, width=3)
        draw.ellipse([hx + 17, hy + 1, hx + 22, hy + 6], fill=BLACK)
    elif eye_type == "drag":
        draw.ellipse([hx - 24, hy - 5, hx - 16, hy + 7], fill=BLACK)
        draw.ellipse([hx - 22, hy - 3, hx - 19, hy], fill=WHITE)
        draw.ellipse([hx + 16, hy - 5, hx + 24, hy + 7], fill=BLACK)
        draw.ellipse([hx + 18, hy - 3, hx + 21, hy], fill=WHITE)

    # 鼻子 (横向小黄椭圆)
    draw.ellipse([hx - 5, hy + 3, hx + 5, hy + 11], fill=YELLOW, outline=BLACK, width=2)

    # 胡须 (左右各3根)
    draw.line([hx - 32, hy - 2, hx - 47, hy - 7], fill=BLACK, width=2)
    draw.line([hx - 33, hy + 5, hx - 49, hy + 5], fill=BLACK, width=2)
    draw.line([hx - 32, hy + 12, hx - 47, hy + 17], fill=BLACK, width=2)
    draw.line([hx + 32, hy - 2, hx + 47, hy - 7], fill=BLACK, width=2)
    draw.line([hx + 33, hy + 5, hx + 49, hy + 5], fill=BLACK, width=2)
    draw.line([hx + 32, hy + 12, hx + 47, hy + 17], fill=BLACK, width=2)

    # 腮红 (卖萌时)
    if blush:
        draw.ellipse([hx - 34, hy + 6, hx - 22, hy + 16], fill=PINK)
        draw.ellipse([hx + 22, hy + 6, hx + 34, hy + 16], fill=PINK)

    return hx, hy, body_x, body_y


def generate_idle():
    """生成待机帧 (微呼吸起伏、眨眼)"""
    for i in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        oy = 1 if i in [1, 2] else 0
        eye = "blink" if i == 2 else "normal"
        
        hx, hy, bx, by = draw_kitty_base(draw, ox=0, oy=oy, eye_type=eye)
        
        # 正常下垂双手
        draw.ellipse([bx - 26, by - 2, bx - 14, by + 12], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        draw.ellipse([bx + 14, by - 2, bx + 26, by + 12], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        
        img.save(os.path.join(ASSETS_DIR, "idle", f"idle_{i}.png"))


def generate_walk():
    """生成走动帧 (双腿交替迈出，手臂前后摇摆)"""
    steps = [
        {"leg": (-4, 4), "arm": (-3, 3), "oy": 0},
        {"leg": (0, 0), "arm": (0, 0), "oy": -2},
        {"leg": (4, -4), "arm": (3, -3), "oy": 0},
        {"leg": (0, 0), "arm": (0, 0), "oy": -2},
    ]
    for i, s in enumerate(steps):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        hx, hy, bx, by = draw_kitty_base(draw, ox=0, oy=s["oy"], eye_type="normal", leg_offset=s["leg"])
        
        la_y, ra_y = s["arm"]
        draw.ellipse([bx - 26, by + la_y, bx - 14, by + 14 + la_y], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        draw.ellipse([bx + 14, by + ra_y, bx + 26, by + 14 + ra_y], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        
        img.save(os.path.join(ASSETS_DIR, "walk", f"walk_{i}.png"))


def generate_cute():
    """生成卖萌帧 (笑眼、歪头、大腮红、冒爱心、小爪捧脸)"""
    for i in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        ox = -2 if i in [0, 1] else 2
        oy = -2 if i in [1, 2] else 0
        
        hx, hy, bx, by = draw_kitty_base(draw, ox=ox, oy=oy, eye_type="happy", blush=True)
        
        # 捧脸动作
        draw.ellipse([hx - 26, hy + 10, hx - 14, hy + 22], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        draw.ellipse([hx + 14, hy + 10, hx + 26, hy + 22], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        
        # 头顶冒爱心
        heart_y = 14 + (i % 2) * -3
        heart_x = 92
        PINK_HEART = (255, 70, 120, 255)
        draw.ellipse([heart_x - 8, heart_y - 6, heart_x - 1, heart_y + 1], fill=PINK_HEART)
        draw.ellipse([heart_x - 1, heart_y - 6, heart_x + 6, heart_y + 1], fill=PINK_HEART)
        draw.polygon([(heart_x - 8, heart_y - 2), (heart_x + 6, heart_y - 2), (heart_x - 1, heart_y + 7)], fill=PINK_HEART)
        
        # 小闪光粒子
        draw.ellipse([heart_x + 10, heart_y - 4, heart_x + 13, heart_y - 1], fill=(255, 220, 50, 230))
        
        img.save(os.path.join(ASSETS_DIR, "cute", f"cute_{i}.png"))


def generate_middle_finger():
    """
    生成搞笑反差比中指帧：
    Kitty 露出鄙视的小眼神，伸出白爪，中指直挺挺竖起！
    头旁带有动漫怒气十字筋 (💢)
    """
    for i in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        shake_x = -1 if i % 2 == 1 else 1
        
        hx, hy, bx, by = draw_kitty_base(draw, ox=shake_x, oy=0, eye_type="grumpy", blush=False)
        
        # 左手叉腰
        draw.ellipse([bx - 26 + shake_x, by + 2, bx - 14 + shake_x, by + 14], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        
        # 右手：向前直挺挺举起，比出中指！
        hand_x = bx + 22 + shake_x
        hand_y = by - 8
        
        # 抬起的手掌
        draw.ellipse([hand_x - 10, hand_y + 4, hand_x + 10, hand_y + 20], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        
        # 竖立的显府中指！
        finger_top = hand_y - 15
        draw.rounded_rectangle([hand_x - 3, finger_top, hand_x + 3, hand_y + 8], radius=3, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        draw.ellipse([hand_x - 8, hand_y + 2, hand_x - 2, hand_y + 9], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=1)
        draw.ellipse([hand_x + 2, hand_y + 2, hand_x + 8, hand_y + 9], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=1)
        
        # 动漫暴躁十字筋 (💢)
        anger_x = hx + 30 + shake_x
        anger_y = hy - 16
        anger_color = (240, 20, 20, 255)
        draw.line([anger_x - 6, anger_y - 2, anger_x + 6, anger_y - 2], fill=anger_color, width=3)
        draw.line([anger_x - 6, anger_y + 2, anger_x + 6, anger_y + 2], fill=anger_color, width=3)
        draw.line([anger_x - 2, anger_y - 6, anger_x - 2, anger_y + 6], fill=anger_color, width=3)
        draw.line([anger_x + 2, anger_y - 6, anger_x + 2, anger_y + 6], fill=anger_color, width=3)
        
        img.save(os.path.join(ASSETS_DIR, "middle_finger", f"finger_{i}.png"))


def generate_drag():
    """生成被抓住后颈皮提起的帧 (四肢慌乱扑腾，小汗珠)"""
    for i in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        leg_anim = [(-3, 3), (3, -3), (-2, 4), (4, -2)][i]
        hx, hy, bx, by = draw_kitty_base(draw, ox=0, oy=-6, eye_type="drag", leg_offset=leg_anim)
        
        arm_anim = [(-6, 6), (6, -6), (-4, 8), (8, -4)][i]
        draw.ellipse([bx - 28, by - 12 + arm_anim[0], bx - 14, by + 2 + arm_anim[0]], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        draw.ellipse([bx + 14, by - 12 + arm_anim[1], bx + 28, by + 2 + arm_anim[1]], fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=2)
        
        SWEAT = (80, 180, 255, 240)
        draw.ellipse([hx + 34, hy - 4, hx + 40, hy + 4], fill=SWEAT)
        
        img.save(os.path.join(ASSETS_DIR, "drag", f"drag_{i}.png"))


if __name__ == "__main__":
    ensure_dirs()
    print("Generating assets...")
    generate_idle()
    generate_walk()
    generate_cute()
    generate_middle_finger()
    generate_drag()
    print("All assets generated successfully!")
