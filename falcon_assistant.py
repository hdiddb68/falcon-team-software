#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FALCON ASSISTANT v3.0 — STARK EDITION
# Управление системой, мониторинг, самоуничтожение

import os
import sys
import webbrowser
import subprocess
import json
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from datetime import datetime
import psutil  # для мониторинга системы
import shutil

# ========== ПРОВЕРКА БИБЛИОТЕК ==========
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

# ========== КОНФИГУРАЦИЯ ==========
CONFIG_FILE = "falcon_config.json"
DEFAULT_CONFIG = {
    "assistant_name": "Скул",
    "voice_rate": 150,
    "voice_volume": 0.9,
    "auto_start": False,
    "monitoring_enabled": True,
    "preferences": {}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# ========== КОМАНДЫ ==========
COMMANDS = {
    # Система
    "выключи": {"action": "shutdown", "reply": "Выключаю компьютер"},
    "перезагрузка": {"action": "restart", "reply": "Перезагружаю компьютер"},
    "спящий режим": {"action": "sleep", "reply": "Перехожу в спящий режим"},
    "блокировка": {"action": "lock", "reply": "Блокирую экран"},
    
    # Мониторинг
    "статус": {"action": "status", "reply": "Проверяю состояние системы"},
    "процессы": {"action": "processes", "reply": "Показываю активные процессы"},
    "угрозы": {"action": "threats", "reply": "Проверяю систему на угрозы"},
    
    # Самоуничтожение
    "уничтожить данные": {"action": "self_destruct", "reply": "Уничтожаю конфигурацию"},
    
    # Приложения
    "блокнот": {"action": "notepad", "reply": "Открываю блокнот"},
    "калькулятор": {"action": "calc", "reply": "Открываю калькулятор"},
    "фалькон": {"action": "falcon", "reply": "Запускаю Falcon Team"},
    
    # Файлы
    "ноутбук": {"action": "laptop", "reply": "Открываю этот компьютер"},
    "файлов": {"action": "explorer", "reply": "Открываю проводник"},
    "диск": {"action": "drive", "reply": "Открываю диск C:"},
    
    # Информация
    "время": {"action": "time", "reply": "Смотрю время"},
    "дата": {"action": "date", "reply": "Смотрю дату"},
    
    # Браузер
    "браузер": {"action": "browser", "url": "https://google.com", "reply": "Открываю браузер"},
    "ютуб": {"action": "browser", "url": "https://youtube.com", "reply": "Открываю YouTube"},
    "музыка": {"action": "browser", "url": "https://music.youtube.com", "reply": "Включаю музыку"},
    
    # Помощь
    "помощь": {"action": "help", "reply": "Показываю помощь"},
    "стоп": {"action": "exit", "reply": "До связи, капитан"},
}

class FalconAssistant:
    def __init__(self):
        self.config = load_config()
        self.name = self.config.get("assistant_name", "Скул")
        self.running = True
        self.monitoring_enabled = self.config.get("monitoring_enabled", True)
        
        # Инициализация голоса
        if TTS_AVAILABLE:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.config.get("voice_rate", 150))
            self.engine.setProperty('volume', self.config.get("voice_volume", 0.9))
        else:
            self.engine = None
        
        # Инициализация распознавания
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
                self.mode = "voice"
            except:
                self.mode = "text"
        else:
            self.mode = "text"
        
        self.setup_gui()
        
        # Запуск фонового мониторинга
        if self.monitoring_enabled:
            self.start_monitoring()
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(f"Falcon Assistant — {self.name} [STARK EDITION]")
        self.root.geometry("700x850")
        self.root.configure(bg='#050510')
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Канвас
        self.canvas = tk.Canvas(self.root, bg='#050510', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Аватар
        self.avatar_label = tk.Label(self.canvas, text=f"""
╔══════════════════════════════════════════╗
║                                          ║
║         🦅  {self.name.upper()}  🦅              ║
║      STARK EDITION — IRON ASSISTANT      ║
║                                          ║
╚══════════════════════════════════════════╝
        """, font=("Courier", 9), bg='#050510', fg='#ff3300', justify='center')
        self.avatar_label.place(x=350, y=80, anchor='center')
        
        # Статус
        self.status_label = tk.Label(self.canvas, text="СТАТУС: ОЖИДАНИЕ", 
                                      font=("Courier", 10, "bold"), 
                                      bg='#050510', fg='#ff6600')
        self.status_label.place(x=350, y=200, anchor='center')
        
        # Мониторинг
        self.monitor_label = tk.Label(self.canvas, text="🟢 МОНИТОРИНГ АКТИВЕН", 
                                       font=("Courier", 8), bg='#050510', fg='#00ff00')
        self.monitor_label.place(x=350, y=230, anchor='center')
        
        # Кнопка голосового ввода
        if self.mode == "voice":
            self.listen_btn = tk.Button(self.canvas, text="🎤 СКАЗАТЬ КОМАНДУ", 
                                        command=self.voice_listen_thread,
                                        bg='#0a0a2a', fg='#ff3300', font=("Courier", 12, "bold"),
                                        relief='flat', activebackground='#ff3300')
            self.listen_btn.place(x=350, y=280, anchor='center', width=200, height=40)
        
        # Поле ввода
        if self.mode == "text":
            self.input_entry = tk.Entry(self.canvas, font=("Courier", 12), 
                                        bg='#0a0a2a', fg='#ff3300', insertbackground='#ff3300',
                                        relief='flat', highlightthickness=1,
                                        highlightcolor='#ff3300', highlightbackground='#ff3300')
            self.input_entry.place(x=350, y=280, anchor='center', width=400, height=30)
            self.input_entry.bind('<Return>', self.execute_text_command)
        
        # Лог
        self.log_text = scrolledtext.ScrolledText(self.canvas, height=20, 
                                                   bg='#0a0a2a', fg='#ff3300',
                                                   font=("Courier", 9), wrap=tk.WORD,
                                                   relief='flat', highlightthickness=0)
        self.log_text.place(x=350, y=550, anchor='center', width=620, height=400)
        self.log_text.config(state=tk.DISABLED)
        
        # Приветствие
        self.add_log(f"🦅 {self.name.upper()} STARK EDITION АКТИВИРОВАН", "system")
        self.add_log("🏢 Управление системой: ОК", "system")
        self.add_log("🛡️ Защита от угроз: АКТИВНА", "system")
        self.add_log("🤖 Режим: " + ("Голосовой" if self.mode == "voice" else "Текстовый"), "info")
        
        if self.mode == "voice":
            self.speak(f"{self.name} активирован. Система под контролем, капитан.")
    
    def speak(self, text):
        self.add_log(f"{self.name}: {text}", "system")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def add_log(self, message, msg_type="user"):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == "user":
            self.log_text.insert(tk.END, f"[{timestamp}] 👤 Вы: {message}\n", "user")
            self.log_text.tag_config("user", foreground="#88ff88")
        elif msg_type == "system":
            self.log_text.insert(tk.END, f"[{timestamp}] 🦅 {message}\n", "system")
            self.log_text.tag_config("system", foreground="#ffaa00")
        else:
            self.log_text.insert(tk.END, f"[{timestamp}] ℹ️ {message}\n", "info")
            self.log_text.tag_config("info", foreground="#aaaaaa")
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_monitoring(self):
        """Фоновый мониторинг системы"""
        def monitor():
            while self.running:
                # Проверка CPU
                cpu = psutil.cpu_percent(interval=1)
                if cpu > 90:
                    self.add_log(f"⚠️ ВНИМАНИЕ! Высокая нагрузка CPU: {cpu}%", "info")
                    self.speak(f"Капитан, нагрузка на процессор {cpu} процентов.")
                
                # Проверка RAM
                ram = psutil.virtual_memory()
                if ram.percent > 90:
                    self.add_log(f"⚠️ ВНИМАНИЕ! Мало оперативной памяти: {ram.percent}%", "info")
                    self.speak(f"Капитан, заканчивается оперативная память.")
                
                # Обновление статуса
                self.monitor_label.config(text=f"🟢 CPU: {cpu}% | RAM: {ram.percent}%")
                
                time.sleep(10)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def voice_listen_thread(self):
        threading.Thread(target=self.voice_listen, daemon=True).start()
    
    def voice_listen(self):
        self.status_label.config(text="СТАТУС: 🎤 СЛУШАЮ...")
        self.listen_btn.config(state=tk.DISABLED)
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            self.status_label.config(text="СТАТУС: 🔄 РАСПОЗНАЮ...")
            command = self.recognizer.recognize_google(audio, language="ru-RU")
            self.add_log(command, "user")
            self.execute_command(command)
            
        except sr.UnknownValueError:
            self.speak("Не расслышал, капитан.")
        except sr.RequestError:
            self.speak("Нет интернета для распознавания.")
        except Exception as e:
            self.add_log(f"Ошибка: {e}", "info")
        
        self.status_label.config(text="СТАТУС: ОЖИДАНИЕ")
        self.listen_btn.config(state=tk.NORMAL)
    
    def execute_text_command(self, event=None):
        command = self.input_entry.get().strip().lower()
        if not command:
            return
        self.add_log(command, "user")
        self.input_entry.delete(0, tk.END)
        self.execute_command(command)
    
    def execute_command(self, command):
        for keyword, cmd_info in COMMANDS.items():
            if keyword in command:
                reply = cmd_info.get("reply", "Выполняю")
                self.speak(reply)
                action = cmd_info["action"]
                
                if action == "shutdown":
                    os.system("shutdown /s /t 10")
                elif action == "restart":
                    os.system("shutdown /r /t 5")
                elif action == "sleep":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                elif action == "lock":
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                elif action == "status":
                    self.show_system_status()
                elif action == "processes":
                    self.show_processes()
                elif action == "threats":
                    self.check_threats()
                elif action == "self_destruct":
                    self.self_destruct()
                elif action == "notepad":
                    os.system("notepad")
                elif action == "calc":
                    os.system("calc")
                elif action == "falcon":
                    os.system("start python falcon_pc_final.py")
                elif action == "laptop":
                    os.system("explorer shell:MyComputerFolder")
                elif action == "explorer":
                    os.system("explorer")
                elif action == "drive":
                    os.system("explorer C:\\")
                elif action == "browser":
                    webbrowser.open(cmd_info["url"])
                elif action == "time":
                    now = datetime.now().strftime("%H:%M")
                    self.speak(f"Сейчас {now}")
                elif action == "date":
                    today = datetime.now().strftime("%d.%m.%Y")
                    self.speak(f"Сегодня {today}")
                elif action == "help":
                    self.show_help()
                elif action == "exit":
                    self.stop()
                return
        
        self.speak(f"Не знаю команду '{command}'. Скажи 'помощь'.")
    
    def show_system_status(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        self.add_log(f"📊 СТАТУС СИСТЕМЫ:\n  CPU: {cpu}%\n  RAM: {ram.percent}% ({ram.used//1024**3}/{ram.total//1024**3} GB)\n  Диск C: {disk.percent}% ({disk.free//1024**3} GB свободно)", "system")
        self.speak(f"Процессор загружен на {cpu} процентов. Оперативная память на {ram.percent} процентов. На диске C свободно {disk.free//1024**3} гигабайт.")
    
    def show_processes(self):
        processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
        
        self.add_log("📋 ТОП-10 ПРОЦЕССОВ ПО CPU:", "system")
        for p in processes:
            self.add_log(f"  {p['name']}: CPU {p.get('cpu_percent', 0)}%", "info")
    
    def check_threats(self):
        suspicious = []
        known_threats = ["hack", "crack", "keygen", "exploit", "malware"]
        
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                for threat in known_threats:
                    if threat in name:
                        suspicious.append(name)
            except:
                pass
        
        if suspicious:
            self.add_log(f"⚠️ ОБНАРУЖЕНЫ ПОДОЗРИТЕЛЬНЫЕ ПРОЦЕССЫ: {', '.join(suspicious)}", "system")
            self.speak(f"Обнаружены подозрительные процессы. Рекомендую проверить.")
        else:
            self.add_log("✅ УГРОЗ НЕ ОБНАРУЖЕНО", "system")
            self.speak("Угроз не обнаружено. Система чиста.")
    
    def self_destruct(self):
        confirm = messagebox.askyesno("САМОУНИЧТОЖЕНИЕ", 
                                       "Уничтожить конфигурацию и данные помощника? Это действие необратимо.")
        if confirm:
            self.add_log("⚠️ ЗАПУЩЕНА ПРОЦЕДУРА САМОУНИЧТОЖЕНИЯ", "system")
            self.speak("Процедура самоуничтожения активирована.")
            
            # Удаление конфига
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            
            # Удаление заметок
            for f in os.listdir('.'):
                if f.startswith('note_') and f.endswith('.txt'):
                    os.remove(f)
            
            self.add_log("💀 КОНФИГУРАЦИЯ УНИЧТОЖЕНА", "system")
            self.speak("Конфигурация уничтожена. Прощайте, капитан.")
            self.stop()
    
    def show_help(self):
        help_text = """
        ╔══════════════════════════════════════════════════════════════╗
        ║  🦅  FALCON ASSISTANT — STARK EDITION  🦅                     ║
        ╠══════════════════════════════════════════════════════════════╣
        ║  УПРАВЛЕНИЕ СИСТЕМОЙ:                                        ║
        ║    выключи, перезагрузка, спящий режим, блокировка          ║
        ║                                                              ║
        ║  МОНИТОРИНГ:                                                 ║
        ║    статус, процессы, угрозы                                 ║
        ║                                                              ║
        ║  ЗАЩИТА:                                                     ║
        ║    уничтожить данные                                        ║
        ║                                                              ║
        ║  ПРИЛОЖЕНИЯ:                                                 ║
        ║    блокнот, калькулятор, фалькон, браузер, ютуб, музыка     ║
        ║                                                              ║
        ║  ФАЙЛЫ:                                                      ║
        ║    ноутбук, файлов, диск, документы, загрузки, изображения  ║
        ║                                                              ║
        ║  ИНФОРМАЦИЯ:                                                 ║
        ║    время, дата                                              ║
        ║                                                              ║
        ║  ОБЩИЕ:                                                      ║
        ║    помощь, стоп                                             ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        self.add_log(help_text, "system")
        self.speak("Помощь отображена в логе.")
    
    def stop(self):
        self.speak("До связи, капитан. Система переходит в режим ожидания.")
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    assistant = FalconAssistant()
    assistant.run()