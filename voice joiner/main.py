import sys
import os
import ctypes
import json
import asyncio
import random
import time
import shutil
import psutil
import datetime
import requests
import discord
import traceback
from discord.ext import commands
import nacl
import nacl.secret
import nacl.utils

if hasattr(sys, '_MEIPASS'):
    os.environ['PATH'] += os.pathsep + sys._MEIPASS

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QScrollArea, 
                             QFrame, QTextEdit, QSystemTrayIcon, QFileDialog, QCheckBox, 
                             QProgressBar, QStyle, QSpinBox, QSplashScreen, QMessageBox, 
                             QMenu, QDoubleSpinBox, QGraphicsOpacityEffect, QGridLayout, QSizePolicy, QDialog, QTextBrowser)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRectF, QPointF
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont, QPainterPath, QPen, QBrush, QLinearGradient

MAX_BOTS = 20

THEME = {
    "bg": "#050505",
    "card_bg": "#0f0f0f",
    "border": "#1f1f1f",
    "accent": "#00f2ea",   
    "accent_dim": "#009994",
    "danger": "#ff0055",    
    "text": "#ffffff",
    "text_dim": "#888888",
    "success": "#00ff9d",
    "primary": "#7000ff"
}

class ApexButton(QPushButton):
    def __init__(self, icon_type, text="", parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.btn_text = text
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(38)
        self.hover_progress = 0.0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        
        if text:
            self.setMinimumWidth(110)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(38)
            
    def enterEvent(self, event):
        self.timer.start(16)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.timer.start(16)
        super().leaveEvent(event)
        
    def animate(self):
        if self.underMouse():
            self.hover_progress += 0.15
            if self.hover_progress >= 1.0:
                self.hover_progress = 1.0
                self.timer.stop()
        else:
            self.hover_progress -= 0.15
            if self.hover_progress <= 0.0:
                self.hover_progress = 0.0
                self.timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        base_bg = QColor("#141414")
        
        if self.icon_type in ["play", "start_all", "bolt", "wifi", "save", "add", "help"]:
            target_bg = QColor(THEME["accent_dim"])
        elif self.icon_type in ["stop", "panic", "delete", "trash"]:
            target_bg = QColor(THEME["danger"])
        else:
            target_bg = QColor("#2a2a2a")

        r = base_bg.red() + (target_bg.red() - base_bg.red()) * self.hover_progress
        g = base_bg.green() + (target_bg.green() - base_bg.green()) * self.hover_progress
        b = base_bg.blue() + (target_bg.blue() - base_bg.blue()) * self.hover_progress
        final_bg = QColor(int(r), int(g), int(b))
        
        border_col = QColor(THEME["border"])
        if self.hover_progress > 0:
            border_col = target_bg.lighter(130)

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect).adjusted(1,1,-1,-1), 6, 6)
        
        painter.setBrush(final_bg)
        painter.setPen(QPen(border_col, 1))
        painter.drawPath(path)
        
        icon_col = QColor("#aaaaaa")
        if self.icon_type in ["delete", "panic", "trash"]: icon_col = QColor(THEME["danger"])
        if self.icon_type in ["play", "start_all", "wifi", "bolt", "help"]: icon_col = QColor(THEME["accent"])
        
        if self.hover_progress > 0.5:
            icon_col = QColor("#ffffff")

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(icon_col)
        painter.setPen(QPen(icon_col, 2))
        
        icon_size = 14
        if self.btn_text:
            icon_rect = QRectF(12, (rect.height() - icon_size) / 2, icon_size, icon_size)
            text_rect = QRectF(icon_rect.right() + 10, 0, rect.width() - icon_rect.right() - 10, rect.height())
        else:
            icon_rect = QRectF((rect.width() - icon_size) / 2, (rect.height() - icon_size) / 2, icon_size, icon_size)
            text_rect = QRectF()

        cx, cy = int(icon_rect.center().x()), int(icon_rect.center().y())
        
        if self.icon_type == "play":
            painter.setPen(Qt.PenStyle.NoPen)
            p = QPainterPath()
            p.moveTo(cx-3, cy-5)
            p.lineTo(cx+5, cy)
            p.lineTo(cx-3, cy+5)
            p.closeSubpath()
            painter.fillPath(p, icon_col)
        elif self.icon_type == "stop":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(cx-4, cy-4, 8, 8, 2, 2)
        elif self.icon_type == "add":
            painter.drawLine(int(cx-5), int(cy), int(cx+5), int(cy))
            painter.drawLine(int(cx), int(cy-5), int(cx), int(cy+5))
        elif self.icon_type == "folder":
            painter.setPen(QPen(icon_col, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(int(cx-6), int(cy-4), 12, 8)
            painter.drawLine(int(cx-6), int(cy-4), int(cx-3), int(cy-7))
            painter.drawLine(int(cx-3), int(cy-7), int(cx+2), int(cy-7))
            painter.drawLine(int(cx+2), int(cy-7), int(cx+2), int(cy-4))
        elif self.icon_type == "settings":
             painter.setPen(QPen(icon_col, 2))
             painter.setBrush(Qt.BrushStyle.NoBrush)
             painter.drawEllipse(QPointF(cx, cy), 5, 5)
        elif self.icon_type == "delete":
             painter.drawLine(int(cx-4), int(cy-4), int(cx+4), int(cy+4))
             painter.drawLine(int(cx+4), int(cy-4), int(cx-4), int(cy+4))
        elif self.icon_type == "clone":
             painter.setPen(QPen(icon_col, 1.5))
             painter.setBrush(Qt.BrushStyle.NoBrush)
             painter.drawRect(int(cx-3), int(cy-3), 7, 7)
             painter.drawPolyline([QPointF(cx-3, cy), QPointF(cx-6, cy), QPointF(cx-6, cy+6), QPointF(cx, cy+6)])
        elif self.icon_type == "trash":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(int(cx-4), int(cy-3), 8, 8)
            painter.drawLine(int(cx-5), int(cy-3), int(cx+5), int(cy-3))
            painter.drawLine(int(cx-2), int(cy-3), int(cx-2), int(cy-5))
            painter.drawLine(int(cx+2), int(cy-3), int(cx+2), int(cy-5))
            painter.drawLine(int(cx-2), int(cy-5), int(cx+2), int(cy-5))
        elif self.icon_type == "bolt":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(icon_col)
            path = QPainterPath()
            path.moveTo(cx+2, cy-6)
            path.lineTo(cx-2, cy)
            path.lineTo(cx+1, cy)
            path.lineTo(cx-2, cy+6)
            path.lineTo(cx+3, cy)
            path.lineTo(cx-1, cy)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.icon_type == "wifi":
            painter.setPen(QPen(icon_col, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(int(cx-6), int(cy-6), 12, 12, 45*16, 90*16)
            painter.drawArc(int(cx-3), int(cy-3), 6, 6, 45*16, 90*16)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(icon_col)
            painter.drawEllipse(QPointF(cx, cy+3), 1, 1)
        elif self.icon_type == "panic":
            painter.setPen(QPen(icon_col, 2))
            painter.drawLine(int(cx), int(cy-6), int(cx), int(cy+2))
            painter.drawPoint(int(cx), int(cy+5))
        elif self.icon_type == "help":
            painter.setPen(QPen(icon_col, 2))
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRectF(cx-6, cy-8, 12, 16), Qt.AlignmentFlag.AlignCenter, "?")

        if self.btn_text:
            painter.setPen(icon_col)
            f = painter.font()
            f.setBold(True)
            painter.setFont(f)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.btn_text)

class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kullanım Kılavuzu")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Picadorso2 Rehberi")
        title.setObjectName("guideTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        content = QTextBrowser()
        content.setHtml("""
        <h3 style='color:#00f2ea'>1. Bot Ekleme</h3>
        <p><b>Token:</b> Discord Developer Portal'dan aldığınız bot tokeni.</p>
        <p><b>Kanal ID:</b> Botun girmesini istediğiniz ses kanalının ID'si.</p>
        <h3 style='color:#00f2ea'>2. Medya ve Ses (ÖNEMLİ)</h3>
        <p><b>FFmpeg:</b> <code>ffmpeg.exe</code> bu uygulamanın yanında durmalıdır.</p>
        <p><b>Opus:</b> <code>libopus-0.x64.dll</code> bu uygulamanın yanında durmalıdır.</p>
        <p><b>Dosya:</b> Çalınacak müzik dosyası.</p>
        <h3 style='color:#00f2ea'>3. Kontroller</h3>
        <p><b>Deaf/Mute:</b> Sağırlaştırma ve Susturma seçenekleri.</p>
        <p><b>Klonla:</b> Ayarları kopyalayarak yeni bot oluşturur.</p>
        """)
        layout.addWidget(content)
        btn_close = ApexButton("delete", "Kapat")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

class SystemMonitor(QThread):
    stats_signal = pyqtSignal(float, float)
    def run(self):
        while True:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                self.stats_signal.emit(cpu, ram)
            except: pass

class BotWorker(QThread):
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str)
    
    def __init__(self, config, manager):
        super().__init__()
        self.cfg = config
        self.manager = manager
        self.bot = None
        self.loop = None
        self.voice_client = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        intents = discord.Intents.default()
        intents.voice_states = True
        
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            self.status_signal.emit("online")
            self.log("SUCCESS", f"{self.bot.user.name} online.")
            
            if not discord.opus.is_loaded():
                try:
                    opus_libs = ['libopus-0.x64.dll', 'libopus-0.dll', 'libopus.dll']
                    loaded = False
                    for lib in opus_libs:
                        try:
                            discord.opus.load_opus(lib)
                            self.log("INFO", f"Opus yüklendi: {lib}")
                            loaded = True
                            break
                        except: pass
                    
                    if not loaded:
                        self.log("WARN", "Opus DLL bulunamadı!")
                except Exception as e:
                    self.log("WARN", f"Opus hatası: {e}")

            act_type = discord.ActivityType.playing
            atype = self.cfg.get("type", "Oynuyor")
            if atype == "İzliyor": act_type = discord.ActivityType.watching
            elif atype == "Dinliyor": act_type = discord.ActivityType.listening
            elif atype == "Yayınlıyor": act_type = discord.ActivityType.streaming
            
            await self.bot.change_presence(activity=discord.Activity(type=act_type, name=self.cfg.get("text", "")))
            
            cid = self.cfg.get("channel")
            if cid and cid.isdigit():
                ch = self.bot.get_channel(int(cid))
                if ch and isinstance(ch, discord.VoiceChannel):
                    try:
                        self.voice_client = await ch.connect(self_deaf=self.cfg.get("deaf", True), self_mute=self.cfg.get("mute", False))
                        self.log("INFO", f"Kanal: {ch.name} (Bağlandı)")
                        
                        mp4 = self.cfg.get("mp4")
                        if mp4 and os.path.exists(mp4):
                            self.loop.create_task(self.play_audio_loop(mp4))
                        else:
                            self.log("ERROR", f"Dosya Bulunamadı: {mp4}")
                            
                    except Exception as e:
                        self.log("ERROR", f"Bağlantı Hatası: {e}")
                        self.status_signal.emit("error")

        try:
            self.loop.run_until_complete(self.bot.start(self.cfg.get("token")))
        except Exception as e:
            self.status_signal.emit("error")
            self.log("CRITICAL", f"Token Hatası: {str(e)[:40]}")

    async def play_audio_loop(self, path):
        ffmpeg_exe = "ffmpeg.exe"
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            full_ffmpeg_path = os.path.join(base_path, ffmpeg_exe)
        else:
            full_ffmpeg_path = ffmpeg_exe

        if not os.path.exists(full_ffmpeg_path) and not shutil.which(ffmpeg_exe):
             self.log("CRITICAL", f"FFMPEG BULUNAMADI! Lütfen ffmpeg.exe'yi uygulamanın yanına koyun.")
             return

        executable_arg = full_ffmpeg_path if os.path.exists(full_ffmpeg_path) else "ffmpeg"

        while self.bot and not self.bot.is_closed():
            if self.voice_client and self.voice_client.is_connected():
                if not self.voice_client.is_playing():
                    try:
                        vol = self.cfg.get("volume", 1.0)
                        ffmpeg_opts = {'options': '-vn -loglevel quiet -re'}
                        
                        source = discord.FFmpegPCMAudio(
                            source=path, 
                            executable=executable_arg,
                            **ffmpeg_opts
                        )
                        
                        transformer = discord.PCMVolumeTransformer(source, volume=vol)
                        self.voice_client.play(transformer)
                        self.log("INFO", "Ses çalınıyor...")
                        
                        while self.voice_client.is_playing(): 
                            await asyncio.sleep(1)
                        
                        await asyncio.sleep(self.cfg.get("interval", 5))
                    except Exception as e:
                        self.log("AUDIO_ERR", f"Ses Hatası: {e}")
                        await asyncio.sleep(5)
                else: await asyncio.sleep(1)
            else: await asyncio.sleep(1)

    def log(self, level, msg):
        self.log_signal.emit(level, msg)
        self.manager.webhook_log(level, msg)

    def stop(self):
        if self.bot: asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)
        self.quit()

class BotCardWidget(QFrame):
    def __init__(self, parent_manager, data=None):
        super().__init__()
        self.manager = parent_manager
        self.worker = None
        self.setObjectName("cardFrame")
        self.loading_val = 0
        self.is_running = False
        self.init_ui(data)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_anim)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_running or self.loading_val > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            color = QColor(THEME["success"]) if self.is_running else QColor(THEME["accent"])
            if not self.is_running: color.setAlpha(150)
            w = self.width() * (self.loading_val / 100)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, self.height()-3, int(w), 3, 0, 0)
            if self.is_running:
                painter.setBrush(Qt.BrushStyle.NoBrush)
                pen = QPen(color)
                pen.setWidth(1)
                color.setAlpha(40)
                painter.setPen(pen)
                painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 10, 10)

    def init_ui(self, data):
        grid = QGridLayout(self)
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 20)
        
        self.status_lbl = QLabel("OFFLINE")
        self.status_lbl.setObjectName("statusOffline")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setFixedWidth(70)
        
        self.inp_token = QLineEdit()
        self.inp_token.setPlaceholderText("Discord Token")
        self.inp_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_token.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.btn_clone = ApexButton("clone")
        self.btn_clone.clicked.connect(self.clone_me)
        
        self.btn_del = ApexButton("delete")
        self.btn_del.clicked.connect(self.delete_me)
        
        grid.addWidget(self.status_lbl, 0, 0)
        grid.addWidget(self.inp_token, 0, 1)
        grid.addWidget(self.btn_clone, 0, 2)
        grid.addWidget(self.btn_del, 0, 3)
        
        grid.setColumnStretch(1, 1) 
        
        self.inp_channel = QLineEdit()
        self.inp_channel.setPlaceholderText("Kanal ID (Ses Kanalı)")
        
        grid.addWidget(self.inp_channel, 1, 0, 1, 4) 
        
        self.inp_mp4 = QLineEdit()
        self.inp_mp4.setPlaceholderText("Dosya Yolu (MP3/MP4)")
        
        self.btn_file = ApexButton("folder")
        self.btn_file.clicked.connect(self.select_file)
        
        self.spin_vol = QDoubleSpinBox()
        self.spin_vol.setRange(0.0, 2.0)
        self.spin_vol.setSingleStep(0.1)
        self.spin_vol.setValue(1.0)
        self.spin_vol.setToolTip("Volume")
        self.spin_vol.setFixedWidth(50)
        
        self.inp_interval = QSpinBox()
        self.inp_interval.setRange(0, 9999)
        self.inp_interval.setValue(5)
        self.inp_interval.setSuffix("s")
        self.inp_interval.setToolTip("Interval")
        self.inp_interval.setFixedWidth(60)
        
        grid.addWidget(self.inp_mp4, 2, 0, 1, 1)
        grid.addWidget(self.btn_file, 2, 1)
        grid.addWidget(self.spin_vol, 2, 2)
        grid.addWidget(self.inp_interval, 2, 3)
        
        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["Oynuyor", "İzliyor", "Dinliyor", "Yayınlıyor"])
        
        self.inp_text = QLineEdit()
        self.inp_text.setPlaceholderText("Durum Mesajı")
        
        self.chk_deaf = QCheckBox("D")
        self.chk_deaf.setChecked(True)
        self.chk_deaf.setToolTip("Deaf")
        
        self.chk_mute = QCheckBox("M")
        self.chk_mute.setToolTip("Mute")
        
        grid.addWidget(self.cmb_type, 3, 0)
        grid.addWidget(self.inp_text, 3, 1)
        grid.addWidget(self.chk_deaf, 3, 2)
        grid.addWidget(self.chk_mute, 3, 3)
        
        self.btn_toggle = ApexButton("play", "BAŞLAT")
        self.btn_toggle.clicked.connect(self.toggle_bot)
        grid.addWidget(self.btn_toggle, 4, 0, 1, 4) 

        if data:
            self.inp_token.setText(data.get("token", ""))
            self.inp_channel.setText(data.get("channel", ""))
            self.inp_mp4.setText(data.get("mp4", ""))
            self.inp_interval.setValue(data.get("interval", 5))
            self.spin_vol.setValue(data.get("volume", 1.0))
            self.cmb_type.setCurrentText(data.get("type", "Oynuyor"))
            self.inp_text.setText(data.get("text", ""))
            self.chk_deaf.setChecked(data.get("deaf", True))
            self.chk_mute.setChecked(data.get("mute", False))

    def clone_me(self):
        self.manager.add_card(self.get_data())

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Dosya", "", "Media (*.mp4 *.mp3 *.wav)")
        if fname: self.inp_mp4.setText(fname)

    def toggle_bot(self):
        if self.worker is None:
            if not self.inp_token.text(): return
            self.btn_toggle.setEnabled(False)
            self.loading_val = 0
            self.is_running = False
            self.anim_timer.start(20) 
            QTimer.singleShot(random.randint(500, 2000), self._start_process)
        else:
            self.worker.stop()
            self.worker = None
            self.update_status("offline")

    def update_anim(self):
        if not self.is_running:
            self.loading_val += 2
            if self.loading_val > 95: self.loading_val = 95
        self.update()

    def _start_process(self):
        cfg = self.get_data()
        self.worker = BotWorker(cfg, self.manager)
        self.worker.log_signal.connect(self.manager.log)
        self.worker.status_signal.connect(self.update_status)
        self.worker.start()
        self.btn_toggle.setEnabled(True)

    def update_status(self, status):
        self.is_running = False 
        if status == "online":
            self.is_running = True
            self.loading_val = 100
            self.status_lbl.setObjectName("statusOnline")
            self.status_lbl.setText("ON")
            self.btn_toggle.icon_type = "stop"
            self.btn_toggle.btn_text = "DURDUR"
        elif status == "error":
            self.loading_val = 0
            self.status_lbl.setObjectName("statusError")
            self.status_lbl.setText("ERR")
            self.worker = None
            self.btn_toggle.icon_type = "play"
            self.btn_toggle.btn_text = "BAŞLAT"
            self.anim_timer.stop()
        else:
            self.loading_val = 0
            self.status_lbl.setObjectName("statusOffline")
            self.status_lbl.setText("OFF")
            self.btn_toggle.icon_type = "play"
            self.btn_toggle.btn_text = "BAŞLAT"
            self.anim_timer.stop()
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)
        self.btn_toggle.update()
        self.update() 

    def delete_me(self):
        if self.worker: self.worker.stop()
        self.manager.remove_card(self)

    def get_data(self):
        return {
            "token": self.inp_token.text(), "channel": self.inp_channel.text(),
            "type": self.cmb_type.currentText(),
            "text": self.inp_text.text(), "deaf": self.chk_deaf.isChecked(),
            "mute": self.chk_mute.isChecked(), "mp4": self.inp_mp4.text(),
            "interval": self.inp_interval.value(), "volume": self.spin_vol.value()
        }
    
    def match_filter(self, text):
        return text.lower() in self.inp_token.text().lower() or text in self.inp_channel.text()

class ApexSplash(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(640, 360)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.progress = 0
        self.paint_ui("System Boot...")

    def paint_ui(self, status):
        pixmap = QPixmap(640, 360)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(10, 10, 620, 340, 15, 15)
        grad = QLinearGradient(0, 0, 640, 360)
        grad.setColorAt(0, QColor("#050505"))
        grad.setColorAt(1, QColor("#111111"))
        painter.setBrush(grad)
        painter.setPen(QPen(QColor("#333"), 2))
        painter.drawPath(path)

        painter.setPen(QColor(THEME["accent"]))
        font = painter.font()
        font.setPixelSize(48)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, 120, 640, 60, Qt.AlignmentFlag.AlignCenter, "PICADORSO2")

        font.setPixelSize(14)
        font.setBold(False)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 6)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(0, 170, 640, 30, Qt.AlignmentFlag.AlignCenter, "VOICE JOINER")

        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0)
        painter.setFont(font)
        painter.setPen(QColor("#888"))
        painter.drawText(0, 260, 640, 30, Qt.AlignmentFlag.AlignCenter, status)

        painter.setBrush(QColor("#222"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(170, 300, 300, 6, 3, 3)

        prog_grad = QLinearGradient(170, 300, 470, 300)
        prog_grad.setColorAt(0, QColor(THEME["accent"]))
        prog_grad.setColorAt(1, QColor(THEME["success"]))
        painter.setBrush(prog_grad)
        painter.drawRoundedRect(170, 300, int(300 * (self.progress / 100)), 6, 3, 3)

        painter.end()
        self.setPixmap(pixmap)
        QApplication.processEvents()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Picadorso2 Voice Joiner")
        self.resize(1200, 800)
        self.cards = []
        self.custom_bg = None
        self.webhook_url = ""
        self.auto_start = False
        
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.show()
        
        self.setup_ui()
        self.load_styles()
        self.load_settings()
        self.load_config()
        self.update_limit_label()
        
        self.sys_mon = SystemMonitor()
        self.sys_mon.stats_signal.connect(self.update_sys_stats)
        self.sys_mon.start()
        
        if self.auto_start:
            QTimer.singleShot(2000, self.start_all)

    def load_styles(self):
        path = os.path.join(os.path.dirname(__file__), "ui/style.qss")
        if os.path.exists(path):
            with open(path, "r") as f: self.base_style = f.read()
            self.setStyleSheet(self.base_style)

    def apply_bg(self):
        if self.custom_bg and os.path.exists(self.custom_bg):
            path = self.custom_bg.replace("\\", "/")
            self.setStyleSheet(self.base_style + f"""
            QMainWindow {{
                background-image: url('{path}');
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            QFrame#sidebar {{ background-color: rgba(5, 5, 5, 0.95); }}
            QFrame#cardFrame {{ background-color: rgba(15, 15, 15, 0.9); }}
            """)
        else:
            self.setStyleSheet(self.base_style)

    def setup_ui(self):
        main_w = QWidget()
        self.setCentralWidget(main_w)
        layout = QHBoxLayout(main_w)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(20, 40, 20, 20)
        side_lay.setSpacing(10)
        
        title = QLabel("PICADORSO2")
        title.setObjectName("titleLabel")
        sub = QLabel("VOICE JOINER")
        sub.setObjectName("subLabel")
        side_lay.addWidget(title)
        side_lay.addWidget(sub)
        
        self.lbl_stats = QLabel("Loading Stats...")
        self.lbl_stats.setObjectName("statsLabel")
        self.lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_lay.addWidget(self.lbl_stats)
        
        side_lay.addStretch()
        
        btn_guide = ApexButton("help", "Nasıl Kullanılır?")
        btn_guide.clicked.connect(self.open_guide)
        side_lay.addWidget(btn_guide)
        
        side_lay.addWidget(QLabel("Sistem"))
        
        btn_ram = ApexButton("bolt", "RAM Temizle")
        btn_ram.clicked.connect(self.clear_ram)
        side_lay.addWidget(btn_ram)
        
        btn_bg_reset = ApexButton("trash", "Arkaplan Sıfırla")
        btn_bg_reset.clicked.connect(self.reset_background)
        side_lay.addWidget(btn_bg_reset)
        
        side_lay.addWidget(QLabel("Ayarlar"))
        
        btn_bg = ApexButton("settings", "Arkaplan Seç")
        btn_bg.clicked.connect(self.change_background)
        side_lay.addWidget(btn_bg)
        
        self.inp_webhook = QLineEdit()
        self.inp_webhook.setPlaceholderText("Webhook URL")
        self.inp_webhook.setEchoMode(QLineEdit.EchoMode.Password)
        side_lay.addWidget(self.inp_webhook)
        
        self.chk_auto = QCheckBox("Oto-Başlat")
        self.chk_auto.toggled.connect(self.set_autostart)
        side_lay.addWidget(self.chk_auto)
        
        btn_import = ApexButton("folder", "İçe Aktar")
        btn_import.clicked.connect(self.import_tokens)
        side_lay.addWidget(btn_import)
        
        btn_save = ApexButton("folder", "Kaydet")
        btn_save.clicked.connect(self.save_all)
        side_lay.addWidget(btn_save)
        
        layout.addWidget(sidebar)

        content = QWidget()
        cont_lay = QVBoxLayout(content)
        cont_lay.setContentsMargins(20, 20, 20, 20)
        cont_lay.setSpacing(15)
        
        header = QHBoxLayout()
        self.lbl_limit = QLabel(f"Botlar: 0 / {MAX_BOTS}")
        self.lbl_limit.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        
        btn_add = ApexButton("add", "Yeni Bot")
        btn_add.clicked.connect(lambda: self.add_card())
        
        btn_start_all = ApexButton("start_all", "Hepsini Başlat")
        btn_start_all.clicked.connect(self.start_all)
        
        btn_panic = ApexButton("panic", "ACİL DURDUR")
        btn_panic.clicked.connect(self.panic_button)
        
        header.addWidget(self.lbl_limit)
        header.addStretch()
        header.addWidget(btn_add)
        header.addWidget(btn_start_all)
        header.addWidget(btn_panic)
        cont_lay.addLayout(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_lay = QVBoxLayout(self.scroll_content)
        self.scroll_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_lay.setSpacing(15)
        self.scroll.setWidget(self.scroll_content)
        cont_lay.addWidget(self.scroll)
        
        self.console = QTextEdit()
        self.console.setFixedHeight(120)
        self.console.setReadOnly(True)
        cont_lay.addWidget(self.console)
        
        layout.addWidget(content)

    def open_guide(self):
        dlg = GuideDialog(self)
        dlg.exec()

    def change_background(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Resim", "", "Img (*.png *.jpg)")
        if fname:
            dest = "custom_bg.jpg"
            shutil.copy(fname, dest)
            self.custom_bg = os.path.abspath(dest)
            self.apply_bg()
            
    def reset_background(self):
        self.custom_bg = None
        if os.path.exists("custom_bg.jpg"): os.remove("custom_bg.jpg")
        self.apply_bg()
        
    def clear_ram(self):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024
        import gc
        gc.collect()
        mem_after = process.memory_info().rss / 1024 / 1024
        self.log("SUCCESS", f"RAM Temizlendi: {mem_before:.1f}MB -> {mem_after:.1f}MB")
        
    def set_autostart(self, val):
        self.auto_start = val

    def add_card(self, data=None):
        if len(self.cards) >= MAX_BOTS:
            return
        card = BotCardWidget(self, data)
        self.cards.append(card)
        self.scroll_lay.addWidget(card)
        self.update_limit_label()

    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            card.deleteLater()
            self.update_limit_label()

    def import_tokens(self):
        if len(self.cards) >= MAX_BOTS: return
        fname, _ = QFileDialog.getOpenFileName(self, "Token", "", "Txt (*.txt)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if len(self.cards) >= MAX_BOTS: break
                    if line.strip(): self.add_card({"token": line.strip()})
            self.log("SUCCESS", "Tokenler eklendi.")

    def start_all(self):
        if len(self.cards) == 0:
            QMessageBox.warning(self, "Uyarı", "Listede hiç bot yok!")
            return
            
        count = 0
        for idx, card in enumerate(self.cards):
            if not card.worker and not card.is_running:
                QTimer.singleShot(count * 2000, card.toggle_bot)
                count += 1
                
    def panic_button(self):
        if len(self.cards) == 0:
            QMessageBox.warning(self, "Uyarı", "Listede durdurulacak bot yok!")
            return
            
        for card in self.cards:
            if card.worker: 
                card.worker.stop()
                card.update_status("offline")
        self.log("WARN", "ACİL DURDURMA!")

    def update_sys_stats(self, cpu, ram):
        self.lbl_stats.setText(f"CPU: {int(cpu)}%  |  RAM: {int(ram)}%")

    def log(self, level, msg):
        color = THEME["success"] if level == "SUCCESS" else THEME["danger"] if level == "ERROR" else "#ffffff"
        self.console.append(f'<span style="color:#666;">[{datetime.datetime.now().strftime("%H:%M:%S")}]</span> <span style="color:{color}; font-weight:bold;">{level}</span> {msg}')
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def webhook_log(self, level, msg):
        if self.webhook_url:
            try:
                requests.post(self.webhook_url, json={"content": f"**[{level}]** {msg}"})
            except: pass

    def update_limit_label(self):
        self.lbl_limit.setText(f"Botlar: {len(self.cards)} / {MAX_BOTS}")
    
    def save_all(self):
        settings = {"bg": self.custom_bg, "webhook": self.inp_webhook.text(), "autostart": self.auto_start}
        with open("settings.json", "w") as f: json.dump(settings, f)
        with open("config.json", "w") as f: json.dump([c.get_data() for c in self.cards], f, indent=4)
        self.log("SUCCESS", "Kaydedildi.")

    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    data = json.load(f)
                    self.custom_bg = data.get("bg", None)
                    self.inp_webhook.setText(data.get("webhook", ""))
                    self.auto_start = data.get("autostart", False)
                    self.chk_auto.setChecked(self.auto_start)
                    self.apply_bg()
            except: pass

    def load_config(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    for d in json.load(f): self.add_card(d)
            except: pass
            
    def closeEvent(self, event):
        self.save_all()
        for c in self.cards: 
            if c.worker: c.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    splash = ApexSplash()
    splash.show()
    
    splash.paint_ui("Python Kernel Loading...")
    time.sleep(0.5)
    splash.progress = 50
    
    if not os.path.exists("ffmpeg.exe"):
        splash.paint_ui("Checking Audio Drivers...")
        time.sleep(1)
    splash.progress = 100
    
    window = MainWindow()
    window.show()
    splash.finish(window)
    
    sys.exit(app.exec())