import time
import random

class PetState:
    IDLE = "idle"
    WALK = "walk"
    CUTE = "cute"
    MIDDLE_FINGER = "middle_finger"
    DRAG = "drag"

CUTE_LINES = [
    "喵呜~ 摸摸头！(o゜▽゜)o☆",
    "今天也要保持好心情呀~ 💕",
    "你一直在看我吗？嘻嘻~ ✨",
    "工作辛苦啦！要多喝水哦~ 🍵",
    "我是全宇宙最可爱的 Kitty！🎀",
]

GRUMPY_LINES = [
    "🖕 别戳了！没完了是吧？！",
    "🖕 爬！手真欠！💢",
    "🖕 素质不详，遇强则强！💥",
    "🖕 看什么看？再戳给你一拳！",
    "🖕 烦死了！小猫咪也是有脾气的！",
    "🖕 信不信我踩你键盘？！",
]

DRAG_LINES = [
    "呀！快放我下来！💦",
    "救命！有人绑架可爱小猫啦！😱",
    "呜呜！后颈皮要被揪秃了！",
    "放手放手！背带裤要掉了！",
]

class StateManager:
    def __init__(self):
        self.state = PetState.WALK
        self.direction = 1  # 1 为向右, -1 为向左
        self.click_history = []
        self.lock_until = 0.0  # 在特定动作（如卖萌/比中指）结束前的锁定时间
        self.auto_roam = True

    def register_click(self):
        """
        记录点击并判断是否触发‘连续狂戳暴怒’（比中指）
        如果在 2.5 秒内点击达到 4 次以上，必定暴怒！
        """
        now = time.time()
        self.click_history.append(now)
        # 只保留最近 2.5 秒内的点击
        self.click_history = [t for t in self.click_history if now - t <= 2.5]

        if len(self.click_history) >= 4:
            self.click_history.clear()
            self.set_state(PetState.MIDDLE_FINGER, lock_duration=3.5)
            line = random.choice(GRUMPY_LINES)
            return PetState.MIDDLE_FINGER, line
        else:
            # 单次点击：卖萌互动
            self.set_state(PetState.CUTE, lock_duration=2.5)
            line = random.choice(CUTE_LINES)
            return PetState.CUTE, line

    def set_state(self, new_state, lock_duration=0.0):
        self.state = new_state
        if lock_duration > 0:
            self.lock_until = time.time() + lock_duration
        else:
            self.lock_until = 0.0

    def is_locked(self):
        return time.time() < self.lock_until

    def start_drag(self):
        self.state = PetState.DRAG
        self.lock_until = float("inf")
        return random.choice(DRAG_LINES)

    def stop_drag(self):
        self.lock_until = 0.0
        self.state = PetState.IDLE

    def decide_next_roam(self):
        """随机漫步决策：保持高频活跃漫步，伴随极短自然呼吸停顿"""
        if not self.auto_roam:
            self.state = PetState.IDLE
            return self.state

        if self.is_locked():
            return self.state

        # 如果之前停下了，85% 几率立刻重新开步漫步
        if self.state != PetState.WALK:
            self.state = PetState.WALK
            if random.random() < 0.4:
                self.direction *= -1
            return self.state

        # 当前已经在走动中：
        r = random.random()
        if r < 0.70:
            # 70% 几率继续前进
            if random.random() < 0.25:
                self.direction *= -1
        elif r < 0.88:
            # 18% 短暂原地停留 2 秒喘口气呼吸
            self.state = PetState.IDLE
        elif r < 0.96:
            # 8% 自发卖萌眨眼
            self.set_state(PetState.CUTE, lock_duration=2.2)
        else:
            # 4% 摸鱼随机比个中指
            self.set_state(PetState.MIDDLE_FINGER, lock_duration=2.8)

        return self.state
