import sys
import time
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout,
    QMessageBox, QDialog, QCheckBox, QDialogButtonBox, QComboBox, QSlider,
    QFormLayout, QSpinBox, QFileDialog
)
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtMultimedia import QSoundEffect
from mpmath import mp, mpf

mp.dps = 80  

PLANCK_TIME = mpf('5.391247e-44')
YOCTOSECOND = mpf('1e-24')
ZEPTOSECOND = mpf('1e-21')
ATTOSECOND = mpf('1e-18')
FEMTOSECOND = mpf('1e-15')
PICOSECOND = mpf('1e-12')


# Absolute path for sound files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHIME_PATH = os.path.join(SCRIPT_DIR, 'chime.wav')
CLICK_PATH = os.path.join(SCRIPT_DIR, 'click.wav')

DEFAULT_THEME = "Hacker"
THEMES = {
    "Light": {"bg": "#f4f4f4", "fg": "#23272a", "highlight": "#007bff"},
    "Dark": {"bg": "#181a1b", "fg": "#f4f4f4", "highlight": "#ffcc00"},
    "Hacker": {"bg": "#181a1b", "fg": "#39ff14", "highlight": "#00ffcc"}
}


class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)

        if settings['theme'] == "Hacker":
            fg = "#39ff14"
            bg = "#181a1b"
        elif settings['theme'] == "Dark":
            fg = "#f4f4f4"
            bg = "#181a1b"
        else:
            fg = "#23272a"
            bg = "#f4f4f4"
        self.setStyleSheet(f"""
            QDialog {{
                background: {bg};
                color: {fg};
            }}
            QLabel, QCheckBox, QComboBox, QSpinBox, QSlider {{
                color: {fg};
                background: {bg};
                selection-background-color: {fg};
                selection-color: {bg};
            }}
            QComboBox QAbstractItemView {{
                background: {bg};
                color: {fg};
            }}
        """)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 400)
        layout = QVBoxLayout()
        form = QFormLayout()

        # Always on top
        self.aot_checkbox = QCheckBox("Always on Top")
        self.aot_checkbox.setChecked(settings['always_on_top'])
        form.addRow(self.aot_checkbox)

        # Planck time
        self.planck_checkbox = QCheckBox("Estimate down to Planck time (fun mode!)")
        self.planck_checkbox.setChecked(settings['planck_mode'])
        form.addRow(self.planck_checkbox)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.setCurrentText(settings['theme'])
        form.addRow("Theme:", self.theme_combo)

        # Font size
        self.fontsize_combo = QComboBox()
        self.fontsize_combo.addItems([
            "SUPER SMALL (Planck mode)", 
            "Pretty Small",
            "Small",
            "Medium",
            "Large",
            "BIG (why tho-)"
        ])
        self.fontsize_combo.setCurrentText(settings['font_size'])
        form.addRow("Font Size:", self.fontsize_combo)


        # Planck Digits
        self.planck_digits_spin = QSpinBox()
        self.planck_digits_spin.setRange(0, 40)
        self.planck_digits_spin.setValue(settings['planck_digits'])
        form.addRow("Planck Digits:", self.planck_digits_spin)

        # Show ms/us/ns
        self.show_ms_checkbox = QCheckBox("Show ms")
        self.show_ms_checkbox.setChecked(settings['show_ms'])
        form.addRow(self.show_ms_checkbox)
        self.show_us_checkbox = QCheckBox("Show μs")
        self.show_us_checkbox.setChecked(settings['show_us'])
        form.addRow(self.show_us_checkbox)
        self.show_ns_checkbox = QCheckBox("Show ns")
        self.show_ns_checkbox.setChecked(settings['show_ns'])
        form.addRow(self.show_ns_checkbox)

        # Transparency
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setMinimum(50)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(int(settings['opacity'] * 100))
        form.addRow("Window Opacity:", self.transparency_slider)

        # Sound type
        self.sound_combo = QComboBox()
        self.sound_combo.addItems(['None', 'Beep', 'Chime', 'Click', 'Custom'])
        self.sound_combo.setCurrentText(settings.get('sound_type', 'Beep'))
        form.addRow("Sound type:", self.sound_combo)
        self.custom_sound_path = settings.get('custom_sound', '')

        # Custom sound picker
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_sound)
        if self.sound_combo.currentText() != "Custom":
            self.browse_btn.hide()
        form.addRow(self.browse_btn)
        self.sound_combo.currentTextChanged.connect(self.update_browse_btn)

        # Display format
        self.display_format_combo = QComboBox()
        self.display_format_combo.addItems(["Classic", "Digital", "Scientific"])
        self.display_format_combo.setCurrentText(settings['display_format'])
        form.addRow("Display Format:", self.display_format_combo)

        # Button style
        self.button_style_combo = QComboBox()
        self.button_style_combo.addItems(["Classic", "Toggle"])
        self.button_style_combo.setCurrentText(settings.get('button_style', 'Classic'))
        form.addRow("Button Style:", self.button_style_combo)

        layout.addLayout(form)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def update_browse_btn(self, txt):
        if txt == "Custom":
            self.browse_btn.show()
        else:
            self.browse_btn.hide()

    def browse_sound(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose Sound File", "", "WAV Files (*.wav)")
        if path:
            self.custom_sound_path = path

    def get_settings(self):
        return {
            'always_on_top': self.aot_checkbox.isChecked(),
            'planck_mode': self.planck_checkbox.isChecked(),
            'theme': self.theme_combo.currentText(),
            'font_size': self.fontsize_combo.currentText(),
            'planck_digits': self.planck_digits_spin.value(),
            'show_ms': self.show_ms_checkbox.isChecked(),
            'show_us': self.show_us_checkbox.isChecked(),
            'show_ns': self.show_ns_checkbox.isChecked(),
            'opacity': self.transparency_slider.value() / 100.0,
            'sound_type': self.sound_combo.currentText(),
            'custom_sound': self.custom_sound_path,
            'display_format': self.display_format_combo.currentText(),
            'button_style': self.button_style_combo.currentText()
        }

class NanoStopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {
            'always_on_top': False,
            'planck_mode': False,
            'theme': DEFAULT_THEME,
            'font_size': "Medium",
            'planck_digits': 35,
            'show_ms': True,
            'show_us': True,
            'show_ns': True,
            'opacity': 1.0,
            'sound_type': 'Beep',
            'custom_sound': '',
            'display_format': "Classic",
            'button_style': "Classic"
        }
        self.initUI()
        self.running = False
        self.start_time = 0
        self.elapsed_ns = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.sound = QSoundEffect()
        self.sound.setVolume(0.8)

    def initUI(self):
        self.setWindowTitle('Ultimate Nano+Planck Stopwatch V1.1.0')
        self.setGeometry(300, 300, 410, 240)
        self.apply_theme()
        self.label = QLabel(self.make_time_str(0), self)
        self.set_font()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"color: {THEMES[self.settings['theme']]['fg']}; background-color: transparent; border-radius: 8px;")
        self.build_buttons()
        self.main_layout = QVBoxLayout()
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)
        self.setWindowOpacity(self.settings['opacity'])
        self.set_always_on_top(self.settings['always_on_top'])

    def build_buttons(self):
        try:
            if hasattr(self, 'btn_layout'):
                QWidget().setLayout(self.btn_layout)
        except:
            pass
        self.btn_layout = QHBoxLayout()
        btn_font = QFont("Segoe UI", 12, QFont.Bold)
        theme = self.settings['theme']
        btn_style = (
            f"QPushButton {{ background-color: {THEMES[theme]['bg']}; color: {THEMES[theme]['fg']}; border-radius: 8px; padding: 8px; }}"
            f"QPushButton:hover {{ background-color: {THEMES[theme]['highlight']}; color: {THEMES[theme]['bg']}; }}"
        )

        if self.settings.get('button_style', 'Classic') == "Toggle":
            # Single toggle button
            self.toggle_btn = QPushButton('▶ Start')
            self.toggle_btn.setFont(btn_font)
            self.toggle_btn.setStyleSheet(btn_style)
            self.toggle_btn.setFixedWidth(120)
            self.toggle_btn.clicked.connect(self.toggle_start_stop)
            self.reset_btn = QPushButton('⏹ Reset')
            self.reset_btn.setFont(btn_font)
            self.reset_btn.setStyleSheet(btn_style)
            self.reset_btn.clicked.connect(self.reset)
            self.copy_btn = QPushButton('📋 Copy Time')
            self.copy_btn.setFont(btn_font)
            self.copy_btn.setStyleSheet(btn_style)
            self.copy_btn.clicked.connect(self.copy_time)
            self.settings_btn = QPushButton('⚙️')
            self.settings_btn.setFixedWidth(40)
            self.settings_btn.setFont(btn_font)
            self.settings_btn.setStyleSheet(btn_style)
            self.settings_btn.clicked.connect(self.open_settings)
            self.btn_layout.addWidget(self.toggle_btn)
            self.btn_layout.addWidget(self.reset_btn)
            self.btn_layout.addWidget(self.copy_btn)
            self.btn_layout.addWidget(self.settings_btn)
        else:
            # Classic separate buttons
            self.start_btn = QPushButton('▶ Start')
            self.start_btn.setFont(btn_font)
            self.start_btn.setStyleSheet(btn_style)
            self.start_btn.clicked.connect(self.start)
            self.stop_btn = QPushButton('⏸ Stop')
            self.stop_btn.setFont(btn_font)
            self.stop_btn.setStyleSheet(btn_style)
            self.stop_btn.clicked.connect(self.stop)
            self.reset_btn = QPushButton('⏹ Reset')
            self.reset_btn.setFont(btn_font)
            self.reset_btn.setStyleSheet(btn_style)
            self.reset_btn.clicked.connect(self.reset)
            self.copy_btn = QPushButton('📋 Copy Time')
            self.copy_btn.setFont(btn_font)
            self.copy_btn.setStyleSheet(btn_style)
            self.copy_btn.clicked.connect(self.copy_time)
            self.settings_btn = QPushButton('⚙️')
            self.settings_btn.setFixedWidth(40)
            self.settings_btn.setFont(btn_font)
            self.settings_btn.setStyleSheet(btn_style)
            self.settings_btn.clicked.connect(self.open_settings)
            self.btn_layout.addWidget(self.start_btn)
            self.btn_layout.addWidget(self.stop_btn)
            self.btn_layout.addWidget(self.reset_btn)
            self.btn_layout.addWidget(self.copy_btn)
            self.btn_layout.addWidget(self.settings_btn)

    def set_font(self):
        font_map = {
            "SUPER SMALL (Planck mode)": 8,
            "Pretty Small": 12,
            "Small": 16,
            "Medium": 22,
            "Large": 32,
            "BIG (why tho-)": 48,
        }
        # If Planck mode, always use super small, otherwise use user’s selection
        if self.settings.get('planck_mode'):
            use_size = "SUPER SMALL (Planck mode)"
        else:
            use_size = self.settings['font_size']
        font = QFont("Consolas", font_map[use_size], QFont.Bold)
        self.label.setFont(font)



    def apply_theme(self):
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(THEMES[self.settings['theme']]['bg']))
        pal.setColor(QPalette.WindowText, QColor(THEMES[self.settings['theme']]['fg']))
        self.setPalette(pal)
        self.setStyleSheet(f"background-color: {THEMES[self.settings['theme']]['bg']};")

    def play_sound(self):
        st = self.settings.get('sound_type', 'Beep')
        if st == 'None':
            return
        elif st == 'Beep':
            QApplication.beep()
        elif st == 'Chime':
            self.sound.setSource(QUrl.fromLocalFile(CHIME_PATH))
            self.sound.play()
        elif st == 'Click':
            self.sound.setSource(QUrl.fromLocalFile(CLICK_PATH))
            self.sound.play()
        elif st == 'Custom':
            path = self.settings.get('custom_sound', '')
            if path:
                self.sound.setSource(QUrl.fromLocalFile(path))
                self.sound.play()

    def toggle_start_stop(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter_ns() - self.elapsed_ns
            self.timer.start(1)
            self.toggle_btn.setText('⏸ Pause')
            self.play_sound()
        else:
            self.running = False
            self.timer.stop()
            self.elapsed_ns = time.perf_counter_ns() - self.start_time
            self.toggle_btn.setText('▶ Start')
            self.play_sound()

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter_ns() - self.elapsed_ns
            self.timer.start(1)
            self.play_sound()
            # For toggle button UI sync
            if hasattr(self, 'toggle_btn'):
                self.toggle_btn.setText('⏸ Pause')

    def stop(self):
        if self.running:
            self.running = False
            self.timer.stop()
            self.elapsed_ns = time.perf_counter_ns() - self.start_time
            self.play_sound()
            if hasattr(self, 'toggle_btn'):
                self.toggle_btn.setText('▶ Start')

    def reset(self):
        self.running = False
        self.timer.stop()
        self.elapsed_ns = 0
        self.update_display()
        self.play_sound()
        if hasattr(self, 'toggle_btn'):
            self.toggle_btn.setText('▶ Start')

    def copy_time(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.label.text())
        QMessageBox.information(self, "Copied!", "Elapsed time copied to clipboard.")

    def open_settings(self):
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_():
            self.settings = dialog.get_settings()
            self.apply_theme()
            self.set_font()
            self.label.setStyleSheet(f"color: {THEMES[self.settings['theme']]['fg']}; background-color: transparent; border-radius: 8px;")
            self.setWindowOpacity(self.settings['opacity'])
            self.set_always_on_top(self.settings['always_on_top'])
            self.clear_button_layout()
            self.build_buttons()
            old_layout_item = self.main_layout.itemAt(1)
            if old_layout_item is not None:
                old_layout = old_layout_item.layout()
                if old_layout is not None:
                    while old_layout.count():
                        item = old_layout.takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.setParent(None)
                    self.main_layout.removeItem(old_layout)
            self.main_layout.insertLayout(1, self.btn_layout)
            self.update_display()

    def maybe_super_small(self, state):
        if state:  # Checked
            self.fontsize_combo.setCurrentText("SUPER SMALL (Planck mode)")



    def clear_button_layout(self):
        if hasattr(self, 'btn_layout'):
            while self.btn_layout.count():
                item = self.btn_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def set_always_on_top(self, enabled):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, enabled)
        self.show()  # Necessary to apply the flag :P

    def make_time_str(self, elapsed):
        hours = elapsed // 3_600_000_000_000
        minutes = (elapsed // 60_000_000_000) % 60
        seconds = (elapsed // 1_000_000_000) % 60
        ms = (elapsed // 1_000_000) % 1000
        us = (elapsed // 1_000) % 1000
        ns = elapsed % 1000
        units = []
        if self.settings['show_ms']:
            units.append(f"{ms:03}")
        if self.settings['show_us']:
            units.append(f"{us:03}")
        if self.settings['show_ns']:
            units.append(f"{ns:03}")

        # Display format
        if self.settings['display_format'] == "Classic":
            basic = f"{hours:02}:{minutes:02}:{seconds:02}." + " ".join(units)
        elif self.settings['display_format'] == "Digital":
            basic = f"{hours:02}:{minutes:02}:{seconds:02}:" + ":".join(units)
        else: # Scientific btw
            basic = f"{hours:02}h {minutes:02}m {seconds:02}s"
            if self.settings['show_ms']:
                basic += f" {ms}ms"
            if self.settings['show_us']:
                basic += f" {us}μs"
            if self.settings['show_ns']:
                basic += f" {ns}ns"

        if not self.settings['planck_mode']:
            return basic

        # Convert to seconds as high-precision
        elapsed_s = mpf(elapsed) / mpf('1e9')

        # Now show the actual number of sub-nanosecond units
        pico = int(elapsed_s / PICOSECOND)
        femto = int(elapsed_s / FEMTOSECOND)
        atto = int(elapsed_s / ATTOSECOND)
        zepto = int(elapsed_s / ZEPTOSECOND)
        yocto = int(elapsed_s / YOCTOSECOND)
        planck = int(elapsed_s / PLANCK_TIME)

        # Format as crazy digits D:
        return (f"{basic} |"
                f" {pico}p"
                f" {femto}f"
                f" {atto}a"
                f" {zepto}z"
                f" {yocto}y"
                f" {planck}ℓ")


    def update_display(self):
        if self.running:
            elapsed = time.perf_counter_ns() - self.start_time
        else:
            elapsed = self.elapsed_ns
        self.label.setText(self.make_time_str(elapsed))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = NanoStopwatch()
    win.show()
    sys.exit(app.exec_())
