# app.py
# Vault-Tec Terminal - Versión Guillem Edition ☢️
# Páginas separadas, cero JS, backup en background, logs limpios

from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import psutil
import os

app = Flask(__name__)
app.secret_key = 'israelnegrojajajamierdasxdbomba'  # ¡CÁMBIALA YA!

# Credenciales (cámbialas también, obviamente)
USERS = {'Guillem': '1234'}

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Command failed: {str(e)}"

def is_backup_running():
    script_name = "backupscript.sh"
    try:
        # Busca procesos que contengan el script pero no pgrep mismo
        result = subprocess.run(f"pgrep -f {script_name} | grep -v pgrep", shell=True, capture_output=True, text=True)
        pids = [p.strip() for p in result.stdout.splitlines() if p.strip()]
        return pids
    except:
        return []

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='ACCESS DENIED. TRY AGAIN, WASTELANDER.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# Raíz: acepta GET y POST para evitar 405 forever
@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('logged_in'):
        return render_template('menu.html')
    else:
        return redirect(url_for('login'))

@app.route('/disk')
@login_required
def disk():
    lsblk = run_command('lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE')
    df = run_command('df -hT')
    return render_template('disk.html', lsblk=lsblk, df=df)

@app.route('/docker')
@login_required
def docker():
    docker_ps = run_command('docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"')
    return render_template('docker.html', docker_ps=docker_ps)

@app.route('/network')
@login_required
def network():
    ip_a = run_command('ip -br a')
    route = run_command('ip route')
    return render_template('network.html', ip_a=ip_a, route=route)

@app.route('/stats')
@login_required
def stats():
    mem = psutil.virtual_memory()
    mem_info = f"Total: {mem.total / (1024**3):.2f} GB | Used: {mem.used / (1024**3):.2f} GB | Free: {mem.available / (1024**3):.2f} GB"
    cpu = psutil.cpu_percent(interval=1)
    load = ' '.join([str(x / psutil.cpu_count() * 100) for x in psutil.getloadavg()][:3])
    top_processes = run_command('ps aux --sort=-%cpu | head -n 11')
    return render_template('stats.html', mem_info=mem_info, cpu=cpu, load=load, top_processes=top_processes)

@app.route('/logs')
@login_required
def logs():
    logs = run_command('journalctl -u docker -n 300 --no-pager')
    return render_template('logs.html', logs=logs)

@app.route('/backup', methods=['GET', 'POST'])
@login_required
def backup():
    backup_pids = is_backup_running()
    running = len(backup_pids) > 0
    status = "IN PROGRESS" if running else "READY"
    color = "red" if running else "lime"
    pid_text = f"(PID: {', '.join(backup_pids)})" if running else ""

    message = None
    vaultboy_success = False
    vaultboy_fail = False

    if request.method == 'POST':
        if running:
            message = "WARNING: YA HAY UN BACKUP CORRIENDO. NO SPAMEES EL BOTÓN, OVERSEER."
            vaultboy_fail = True
        else:
            script_path = '/home/guillem/backupscript/backupscript.sh'
            log_file = '/home/guillem/backupscript/backup.log'
            if os.path.exists(script_path) and os.access(script_path, os.X_OK):
                subprocess.Popen(f'nohup {script_path} > {log_file} 2>&1 &', shell=True)
                message = "BACKUP LANZADO EN BACKGROUND. PUEDES SEGUIR USANDO EL TERMINAL."
                vaultboy_success = True
            else:
                message = "ERROR: Script no encontrado o sin permisos de ejecución."
                vaultboy_fail = True

    return render_template('backup.html',
                           status=status, color=color, pid_text=pid_text,
                           message=message, vaultboy_success=vaultboy_success,
                           vaultboy_fail=vaultboy_fail)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
