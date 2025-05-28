from flask import Flask, jsonify, render_template, session
from threading import Timer
import time
import random
import secrets
import stat
import os
import subprocess
import re
from dotenv import load_dotenv

load_dotenv()

DURATION = int(os.getenv('DURATION')) 
CHALL_PORT_RANGE_START = int(os.getenv('CHALL_PORT_RANGE_START'))
CHALL_PORT_RANGE_END = int(os.getenv('CHALL_PORT_RANGE_END'))
DOMAIN = os.getenv('DOMAIN')
CHALL_TITLE = os.getenv('CHALL_TITLE')
normalized_chall_title = CHALL_TITLE.lower().replace(' ', '-')

instances = {}
used_ports = set()

chall_start_path = os.path.join(os.getcwd(), 'chall/start.sh')
chall_stop_path = os.path.join(os.getcwd(), 'chall/stop.sh')

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SESSION_COOKIE_NAME'] = secrets.token_hex(32)

def cleanup_hanging_instances():
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True, check=True)
        
        container_names = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        instance_pattern = f"{normalized_chall_title}-\\d+-"
        
        hanging_projects = set()
        for container_name in container_names:
            if re.match(instance_pattern, container_name):
                match = re.match(f"({normalized_chall_title}-\\d+)-", container_name)
                if match:
                    project_name = match.group(1)
                    hanging_projects.add(project_name)
        
        # Stop and remove each hanging project
        docker_compose_path = os.path.join(os.getcwd(), 'chall/docker-compose.yml')
        for project_name in hanging_projects:
            try:
                print(f"Cleaning up hanging instance: {project_name}")
                subprocess.run(['docker-compose', '-f', docker_compose_path, '-p', project_name, 'down'], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to cleanup instance {project_name}: {e}")
                
        if hanging_projects:
            print(f"Cleaned up {len(hanging_projects)} hanging instances")
        else:
            print("No hanging instances found")
            
    except subprocess.CalledProcessError as e:
        print(f"Error during cleanup: {e}")
    except Exception as e:
        print(f"Unexpected error during cleanup: {e}")

def generate_random_port():
    while True:
        port = random.randint(CHALL_PORT_RANGE_START, CHALL_PORT_RANGE_END)
        if port not in used_ports:
            used_ports.add(port)
            return port

def release_port(port):
    used_ports.remove(port)

def start_instance(port):
    instance_id = f'{normalized_chall_title}-{port}'

    os.chmod(chall_start_path, stat.S_IRWXU)

    try:
        result = subprocess.run([chall_start_path, str(port), instance_id], 
                              check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return None, f'Failed to start new instance: {e}'

    return instance_id, None

def stop_instance(port, instance_id, user_id):
    os.chmod(chall_stop_path, stat.S_IRWXU)

    try:
        result = subprocess.run([chall_stop_path, str(port), instance_id], 
                              check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return None, f'Failed to stop instance: {e}'
        
    release_port(port)
    del instances[user_id]

    return instance_id, None

def get_session():
    user_id = session.get('user_id')

    if not user_id:
        user_id = str(random.randint(100000, 999999))
        session['user_id'] = user_id
    
    return user_id

@app.route('/')
def index():
    user_id = get_session()
    instance = instances.get(user_id)
    now = round(time.time() * 1000)

    if instance != None and instance['end_time'] <= now:
        instance = None

    return render_template('index.html', instance=instance, chall_title=CHALL_TITLE)

@app.route('/start_instance', methods=['POST'])
def start_instance_route():
    user_id = get_session()

    if user_id in instances:
        return jsonify({"error": "You already have a running instance."}), 400

    port = generate_random_port()
    instance_id, err = start_instance(port)

    if err:
        return jsonify({"error": err}), 500

    end_time = round(time.time() * 1000) + DURATION
    
    instances[user_id] = {"instance_id": instance_id, "port": port, "end_time": end_time, "url": f"{DOMAIN}:{port}"}
    Timer((float(DURATION/1000)), stop_instance, (port, instance_id, user_id)).start()
    
    return jsonify(instances[user_id])


@app.route('/stop_instance', methods=['POST'])
def stop_instance_route():
    user_id = get_session()

    if user_id not in instances:
        return jsonify({"error": "No running instance found for the user."}), 400

    instance = instances[user_id]

    port = instance['port']
    instance_id = instance['instance_id']

    _, err = stop_instance(port, instance_id, user_id)

    if err:
        return jsonify({"error": err}), 500

    return jsonify({"message": "stopped"})

if __name__ == '__main__':
    print("Starting application and cleaning up hanging instances...")
    cleanup_hanging_instances()
    app.run(host='0.0.0.0', port=80)