import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC_DIR = r"C:\Users\54185\.gemini\antigravity\brain\c19f2c68-0ce4-4dad-b07c-b3c15b82e807"
DEST_DIR = os.path.join(os.path.dirname(__file__), "assets")

IMG_IDLE = os.path.join(SRC_DIR, "test_green_screen_1789361974634.jpg")
IMG_SASSY = os.path.join(SRC_DIR, "green_kitty_sassy_1789362016469.jpg")
IMG_CUTE = os.path.join(SRC_DIR, "green_kitty_cute_1789362052711.jpg")
IMG_WALK = os.path.join(SRC_DIR, "green_kitty_walk_1789362130537.jpg")
IMG_DRAG = os.path.join(SRC_DIR, "green_kitty_drag_1789362405754.jpg")

TARGET_W, TARGET_H = 180, 240

def key_green_screen(img_path):
    """高质量色度抠图：抑制绿边、羽化边缘"""
    img = cv2.imread(img_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 纯绿背景检测
    lower = np.array([35, 90, 80])
    upper = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    # 微小膨胀绿幕遮罩消除边缘绿毛边
    kernel = np.ones((3, 3), np.uint8)
    mask_dilated = cv2.dilate(mask, kernel, iterations=1)
    
    alpha = 255 - mask_dilated
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    
    # 绿边去色 (De-spill)
    b, g, r = cv2.split(img)
    edge_zone = (alpha > 0) & (alpha < 240)
    g_despill = np.where(edge_zone, np.minimum(g, (b.astype(int) + r.astype(int)) // 2), g).astype(np.uint8)
    
    rgba = cv2.merge([b, g_despill, r, alpha])
    pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    
    # 裁剪紧凑边界
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    return pil_img

def fit_to_canvas(img, target_w=TARGET_W, target_h=TARGET_H, oy=0, ox=0):
    """将裁切好的图像按比例缩放居中放置在透明画布上"""
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    # 计算按比例缩放，留出少量边缘
    scale = min((target_w - 16) / img.width, (target_h - 16) / img.height)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 底部稍微对齐，居中放置
    paste_x = (target_w - new_w) // 2 + ox
    paste_y = (target_h - new_h) - 6 + oy
    canvas.alpha_composite(resized, (paste_x, paste_y))
    return canvas

def make_idle():
    raw = key_green_screen(IMG_IDLE)
    folder = os.path.join(DEST_DIR, "idle")
    os.makedirs(folder, exist_ok=True)
    
    # 4 帧微呼吸
    for i, oy in enumerate([0, -2, -1, 0]):
        c = fit_to_canvas(raw, oy=oy)
        c.save(os.path.join(folder, f"idle_{i}.png"))
    print("Idle frames ready.")

def make_walk():
    # 使用正脸玩偶制作可爱的正面颠簸摇晃步态（横着走，正面对着屏幕，左右轻微倾斜踏步）
    raw_front = key_green_screen(IMG_IDLE)
    folder = os.path.join(DEST_DIR, "walk")
    os.makedirs(folder, exist_ok=True)
    
    # 帧0：微向左倾斜（1.8度，微幅起伏）
    rot_left = raw_front.rotate(-1.8, resample=Image.Resampling.BICUBIC, expand=True)
    f0 = fit_to_canvas(rot_left, ox=-1, oy=-1)
    
    # 帧1：回到中间平稳
    f1 = fit_to_canvas(raw_front, ox=0, oy=0)
    
    # 帧2：微向右倾斜（1.8度，微幅起伏）
    rot_right = raw_front.rotate(1.8, resample=Image.Resampling.BICUBIC, expand=True)
    f2 = fit_to_canvas(rot_right, ox=1, oy=-1)
    
    # 帧3：回到中间平稳
    f3 = fit_to_canvas(raw_front, ox=0, oy=0)
    
    f0.save(os.path.join(folder, "walk_0.png"))
    f1.save(os.path.join(folder, "walk_1.png"))
    f2.save(os.path.join(folder, "walk_2.png"))
    f3.save(os.path.join(folder, "walk_3.png"))
    print("Front-facing horizontal walk frames ready.")

def make_cute():
    raw = key_green_screen(IMG_CUTE)
    folder = os.path.join(DEST_DIR, "cute")
    os.makedirs(folder, exist_ok=True)
    
    # 卖萌帧：带粉红爱心动画
    for i in range(4):
        c = fit_to_canvas(raw, oy=(-2 if i in [1, 2] else 0))
        draw = ImageDraw.Draw(c)
        
        # 绘制头顶跳动的爱心
        hx = 145
        hy = 35 - i * 3
        # 粉红爱心
        PINK = (255, 60, 120, 240)
        draw.ellipse([hx - 9, hy - 7, hx - 1, hy + 1], fill=PINK)
        draw.ellipse([hx - 1, hy - 7, hx + 7, hy + 1], fill=PINK)
        draw.polygon([(hx - 9, hy - 2), (hx + 7, hy - 2), (hx - 1, hy + 8)], fill=PINK)
        
        # 闪烁小星光
        if i >= 2:
            draw.ellipse([hx - 16, hy - 10, hx - 12, hy - 6], fill=(255, 230, 80, 240))
            draw.ellipse([hx + 12, hy - 12, hx + 15, hy - 9], fill=(255, 230, 80, 240))
            
        c.save(os.path.join(folder, f"cute_{i}.png"))
    print("Cute frames ready.")

def make_middle_finger():
    raw = key_green_screen(IMG_SASSY)
    folder = os.path.join(DEST_DIR, "middle_finger")
    os.makedirs(folder, exist_ok=True)
    
    # 制作比中指/暴怒动作：
    # 强化手指中指轮廓、跳动的暴怒十字筋 (💢)
    for i in range(4):
        # 微晃抖动
        ox = -2 if i % 2 == 1 else 2
        c = fit_to_canvas(raw, ox=ox, oy=0)
        draw = ImageDraw.Draw(c)
        
        # 在抬起的白爪上精细强化修饰竖立的中指轮廓
        hand_cx = 126 + ox
        hand_cy = 112
        # 强调中指线条与指节，使其格外清晰
        draw.rounded_rectangle([hand_cx - 4, hand_cy - 20, hand_cx + 4, hand_cy], radius=3, fill=(252, 252, 252, 255), outline=(50, 50, 50, 220), width=2)
        # 旁边收拢的手指鼓包
        draw.ellipse([hand_cx - 9, hand_cy - 8, hand_cx - 3, hand_cy + 2], fill=(245, 245, 245, 255), outline=(60, 60, 60, 200), width=1)
        draw.ellipse([hand_cx + 3, hand_cy - 8, hand_cx + 9, hand_cy + 2], fill=(245, 245, 245, 255), outline=(60, 60, 60, 200), width=1)

        # 动漫暴躁怒气十字筋 (💢)
        anger_x = 42 + ox
        anger_y = 65
        anger_c = (235, 20, 20, 240)
        sz = 8 if i in [1, 3] else 6
        draw.line([anger_x - sz, anger_y - 2, anger_x + sz, anger_y - 2], fill=anger_c, width=3)
        draw.line([anger_x - sz, anger_y + 2, anger_x + sz, anger_y + 2], fill=anger_c, width=3)
        draw.line([anger_x - 2, anger_y - sz, anger_x - 2, anger_y + sz], fill=anger_c, width=3)
        draw.line([anger_x + 2, anger_y - sz, anger_x + 2, anger_y + sz], fill=anger_c, width=3)
        
        c.save(os.path.join(folder, f"finger_{i}.png"))
    print("Middle finger frames ready.")

def make_drag():
    raw = key_green_screen(IMG_DRAG)
    folder = os.path.join(DEST_DIR, "drag")
    os.makedirs(folder, exist_ok=True)
    
    # 扑腾被拎起动作
    for i in range(4):
        angle = [-4, 0, 4, 0][i]
        rot = raw.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        c = fit_to_canvas(rot, oy=-6)
        c.save(os.path.join(folder, f"drag_{i}.png"))
    print("Drag frames ready.")

if __name__ == "__main__":
    print("Processing green-screen photographic plush doll assets...")
    make_idle()
    make_walk()
    make_cute()
    make_middle_finger()
    make_drag()
    print("All plush doll assets processed successfully!")
