import sys
import os
import unittest

from PyQt5.QtWidgets import QApplication
from pet_state import StateManager, PetState
from pet_window import PetWindow

class TestDesktopPet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        cls.assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    def test_state_manager_clicks(self):
        mgr = StateManager()
        
        # 前 3 次点击为萌态
        for _ in range(3):
            state, line = mgr.register_click()
            self.assertEqual(state, PetState.CUTE)

        # 第 4 次狂点，触发暴怒比中指
        state, line = mgr.register_click()
        self.assertEqual(state, PetState.MIDDLE_FINGER)
        self.assertIn("🖕", line)

    def test_drag_logic(self):
        mgr = StateManager()
        drag_line = mgr.start_drag()
        self.assertEqual(mgr.state, PetState.DRAG)
        self.assertTrue(len(drag_line) > 0)
        mgr.stop_drag()
        self.assertEqual(mgr.state, PetState.IDLE)

    def test_window_and_assets(self):
        window = PetWindow(self.assets_dir)
        for st in [PetState.IDLE, PetState.WALK, PetState.CUTE, PetState.MIDDLE_FINGER, PetState.DRAG]:
            self.assertIn(st, window.frames)
            self.assertGreater(len(window.frames[st]), 0, f"Frames for state {st} should not be empty")

        # 验证缩放
        window.set_scale(1.5)
        self.assertEqual(window.width(), int(180 * 1.5))
        window.close_pet()

if __name__ == "__main__":
    unittest.main()
