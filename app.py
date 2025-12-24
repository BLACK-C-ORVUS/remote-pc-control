import threading
import webbrowser
from flask import Flask, request, render_template_string
import os
import platform
import pystray
from PIL import Image, ImageDraw

# ---------- Flask App ----------
app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Remote PC Control</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { 
        background-color: #f0f2f5; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        height: 100vh; 
        font-family: Arial, sans-serif;
    }
    .card {
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        background-color: white;
        width: 450px;
    }
    button { width: 100%; margin-top:5px;}
    #timer { font-size: 24px; text-align: center; margin-bottom: 10px; }
</style>
</head>
<body>
<div class="card">
    <h2 class="text-center mb-4">Remote PC Control</h2>

    <div id="timer">Timer: 0:00</div>
    
    <form id="shutdownForm">
        <label>Shutdown Timer (minutes):</label>
        <input type="number" class="form-control mb-2" id="shutdown_time" min="0" required>
        <button type="submit" class="btn btn-danger">Shutdown</button>
    </form>

    <form id="restartForm">
        <label>Restart Timer (minutes):</label>
        <input type="number" class="form-control mb-2" id="restart_time" min="0" required>
        <button type="submit" class="btn btn-warning">Restart</button>
    </form>

    <form id="lockForm">
        <label>Lock Timer (minutes):</label>
        <input type="number" class="form-control mb-2" id="lock_time" min="0" required>
        <button type="submit" class="btn btn-secondary">Lock</button>
    </form>

    <form id="sleepForm">
        <label>Sleep Timer (minutes):</label>
        <input type="number" class="form-control mb-2" id="sleep_time" min="0" required>
        <button type="submit" class="btn btn-info">Sleep</button>
    </form>

    <button id="cancelBtn" class="btn btn-dark">Cancel Timer</button>
</div>

<script>
let timerInterval;
let remainingSeconds = 0;
let currentAction = "";

function startTimer(seconds, action) {
    clearInterval(timerInterval);
    remainingSeconds = seconds;
    currentAction = action;
    updateTimerDisplay();

    timerInterval = setInterval(() => {
        if(remainingSeconds <= 0){
            clearInterval(timerInterval);
            fetch(`/execute?action=${action}`);
            document.getElementById('timer').innerText = "Executing " + action;
            return;
        }
        remainingSeconds--;
        updateTimerDisplay();
    }, 1000);
}

function updateTimerDisplay() {
    let min = Math.floor(remainingSeconds / 60);
    let sec = remainingSeconds % 60;
    document.getElementById('timer').innerText = `Timer: ${min}:${sec.toString().padStart(2,'0')}`;
}

document.getElementById('shutdownForm').addEventListener('submit', function(e){
    e.preventDefault();
    let minutes = parseInt(document.getElementById('shutdown_time').value) || 0;
    startTimer(minutes*60, 'shutdown');
});

document.getElementById('restartForm').addEventListener('submit', function(e){
    e.preventDefault();
    let minutes = parseInt(document.getElementById('restart_time').value) || 0;
    startTimer(minutes*60, 'restart');
});

document.getElementById('lockForm').addEventListener('submit', function(e){
    e.preventDefault();
    let minutes = parseInt(document.getElementById('lock_time').value) || 0;
    startTimer(minutes*60, 'lock');
});

document.getElementById('sleepForm').addEventListener('submit', function(e){
    e.preventDefault();
    let minutes = parseInt(document.getElementById('sleep_time').value) || 0;
    startTimer(minutes*60, 'sleep');
});

document.getElementById('cancelBtn').addEventListener('click', function(){
    clearInterval(timerInterval);
    remainingSeconds = 0;
    document.getElementById('timer').innerText = "Timer: 0:00 (Cancelled)";
});
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/execute')
def execute():
    action = request.args.get('action', '')
    os_name = platform.system()
    try:
        if os_name == "Windows":
            if action == "shutdown":
                os.system("shutdown /s /t 0")
            elif action == "restart":
                os.system("shutdown /r /t 0")
            elif action == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif action == "sleep":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif os_name == "Linux":
            if action == "shutdown":
                os.system("shutdown -h now")
            elif action == "restart":
                os.system("reboot")
            elif action == "lock":
                os.system("loginctl lock-session")
            elif action == "sleep":
                os.system("systemctl suspend")
        elif os_name == "Darwin":
            if action == "shutdown":
                os.system("sudo shutdown -h now")
            elif action == "restart":
                os.system("sudo shutdown -r now")
            elif action == "lock":
                os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
            elif action == "sleep":
                os.system("pmset sleepnow")
        return f"{action} executed"
    except Exception as e:
        return str(e)

# ---------- Tray Icon ----------
def create_image():
    image = Image.new('RGB', (64, 64), color=(0,128,255))
    d = ImageDraw.Draw(image)
    d.rectangle((0,0,64,64), fill=(0,128,255))
    return image

def on_quit(icon, item):
    icon.stop()
    os._exit(0)  # خروج کامل برنامه

def run_flask():
    webbrowser.open("http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    icon = pystray.Icon("RemotePC", create_image(), "Remote PC Control", menu=pystray.Menu(
        pystray.MenuItem("Quit", on_quit)
    ))
    icon.run()
