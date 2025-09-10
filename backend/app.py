import os
import sqlite3
import math
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_db_connection, init_db

# --- Configuração ---
STORAGE_PATH = os.path.join(os.path.dirname(__file__), 'storage')
NUM_OSTS = 4
OST_PATHS = [os.path.join(STORAGE_PATH, f'ost{i+1}') for i in range(NUM_OSTS)]

# --- Inicialização da Aplicação ---
app = Flask(__name__)
CORS(app)

# --- Funções Auxiliares (sem alterações) ---
def get_path_id(path, conn):
    if path == '/': return 1
    parts = path.strip('/').split('/')
    current_id = 1
    for part in parts:
        if not part: continue
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM metadata WHERE filename = ? AND parent_id = ?", (part, current_id))
        result = cursor.fetchone()
        if result is None: return None
        current_id = result['id']
    return current_id

def write_striped_file(file_id, file_data, stripe_count, stripe_size):
    total_size = len(file_data)
    num_chunks = math.ceil(total_size / stripe_size)
    for i in range(num_chunks):
        start, end = i * stripe_size, start + stripe_size
        chunk_data = file_data[start:end]
        ost_index = i % stripe_count
        ost_path = OST_PATHS[ost_index]
        chunk_filepath = os.path.join(ost_path, f"{file_id}_chunk_{i}")
        with open(chunk_filepath, 'wb') as f:
            f.write(chunk_data)

def read_striped_file(file_id, total_size, stripe_count, stripe_size):
    file_data = bytearray()
    num_chunks = math.ceil(total_size / stripe_size)
    for i in range(num_chunks):
        ost_index = i % stripe_count
        ost_path = OST_PATHS[ost_index]
        chunk_filepath = os.path.join(ost_path, f"{file_id}_chunk_{i}")
        try:
            with open(chunk_filepath, 'rb') as f:
                file_data.extend(f.read())
        except FileNotFoundError:
            return None
    return bytes(file_data)

# --- Endpoints da API ---

# --- NOVO ENDPOINT DE VISUALIZAÇÃO ---
@app.route('/api/files/visualize', methods=['GET'])
def visualize_file_stripes():
    """Calcula e retorna a distribuição de chunks de um arquivo pelos OSTs."""
    path = request.args.get('path', '/')
    conn = get_db_connection()
    
    file_id = get_path_id(path, conn)
    if file_id is None:
        conn.close()
        return jsonify({"error": "Arquivo não encontrado"}), 404
        
    cursor = conn.cursor()
    cursor.execute("SELECT size_bytes, stripe_count, stripe_size_bytes, is_directory FROM metadata WHERE id = ?", (file_id,))
    meta = cursor.fetchone()
    conn.close()

    if meta is None or meta['is_directory']:
        return jsonify({}), 200 # Retorna objeto vazio para diretórios

    # Calcula a localização de cada chunk
    num_chunks = math.ceil(meta['size_bytes'] / meta['stripe_size_bytes'])
    stripe_count = meta['stripe_count']
    
    # Inicializa um dicionário para o resultado
    distribution = {f'ost{i+1}': [] for i in range(NUM_OSTS)}

    for i in range(num_chunks):
        ost_index = i % stripe_count
        ost_name = f'ost{ost_index + 1}'
        distribution[ost_name].append(i) # Adiciona o índice do chunk ao OST correspondente
    
    return jsonify(distribution)

# O resto do arquivo app.py continua igual...
@app.route('/api/files', methods=['GET'])
def list_files():
    path = request.args.get('path', '/')
    conn = get_db_connection()
    parent_id = get_path_id(path, conn)
    if parent_id is None: conn.close(); return jsonify({"error": "Diretório não encontrado"}), 404
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, is_directory, size_bytes FROM metadata WHERE parent_id = ?", (parent_id,))
    files = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(files)

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"error": "Nenhum arquivo enviado"}), 400
    file = request.files['file']
    path = request.form.get('path', '/')
    filename = file.filename
    file_data = file.read()
    file_size = len(file_data)
    conn = get_db_connection()
    parent_id = get_path_id(path, conn)
    if parent_id is None: conn.close(); return jsonify({"error": "Diretório de destino não encontrado"}), 404
    cursor = conn.cursor()
    cursor.execute("SELECT stripe_count, stripe_size_bytes FROM metadata WHERE id = ?", (parent_id,))
    parent_layout = cursor.fetchone()
    stripe_count = parent_layout['stripe_count']
    stripe_size = parent_layout['stripe_size_bytes']
    cursor.execute("INSERT INTO metadata (filename, parent_id, is_directory, size_bytes, stripe_count, stripe_size_bytes) VALUES (?, ?, ?, ?, ?, ?)",(filename, parent_id, False, file_size, stripe_count, stripe_size))
    conn.commit()
    new_file_id = cursor.lastrowid
    write_striped_file(new_file_id, file_data, stripe_count, stripe_size)
    conn.close()
    return jsonify({"message": f"Arquivo '{filename}' enviado com sucesso!", "id": new_file_id}), 201

@app.route('/api/files/create', methods=['POST'])
def create_text_file():
    data = request.json
    path, filename, content = data.get('path'), data.get('filename'), data.get('content', '')
    if not filename: return jsonify({"error": "Nome do arquivo é obrigatório"}), 400
    file_data = content.encode('utf-8')
    file_size = len(file_data)
    conn = get_db_connection()
    parent_id = get_path_id(path, conn)
    if parent_id is None: conn.close(); return jsonify({"error": "Diretório de destino não encontrado"}), 404
    cursor = conn.cursor()
    cursor.execute("SELECT stripe_count, stripe_size_bytes FROM metadata WHERE id = ?", (parent_id,))
    parent_layout = cursor.fetchone()
    stripe_count, stripe_size = parent_layout['stripe_count'], parent_layout['stripe_size_bytes']
    cursor.execute("INSERT INTO metadata (filename, parent_id, is_directory, size_bytes, stripe_count, stripe_size_bytes) VALUES (?, ?, ?, ?, ?, ?)", (filename, parent_id, False, file_size, stripe_count, stripe_size))
    conn.commit()
    new_file_id = cursor.lastrowid
    write_striped_file(new_file_id, file_data, stripe_count, stripe_size)
    conn.close()
    return jsonify({"message": f"Arquivo de texto '{filename}' criado com sucesso!", "id": new_file_id}), 201

@app.route('/api/layout', methods=['GET'])
def get_layout():
    path = request.args.get('path', '/')
    conn = get_db_connection()
    file_id = get_path_id(path, conn)
    if file_id is None: conn.close(); return jsonify({"error": "Arquivo ou diretório não encontrado"}), 404
    cursor = conn.cursor()
    cursor.execute("SELECT stripe_count, stripe_size_bytes FROM metadata WHERE id = ?", (file_id,))
    layout = cursor.fetchone()
    conn.close()
    if layout is None: return jsonify({"error": "Layout não encontrado"}), 404
    return jsonify(dict(layout))

@app.route('/api/layout', methods=['POST'])
def set_layout():
    data = request.json
    path, stripe_count, stripe_size_mb = data.get('path'), int(data.get('stripe_count', 1)), int(data.get('stripe_size_mb', 1))
    stripe_size_bytes = stripe_size_mb * 1024 * 1024
    if stripe_count > NUM_OSTS: return jsonify({"error": f"Stripe count não pode ser maior que o número de OSTs ({NUM_OSTS})"}), 400
    conn = get_db_connection()
    file_id = get_path_id(path, conn)
    if file_id is None: conn.close(); return jsonify({"error": "Arquivo ou diretório não encontrado"}), 404
    cursor = conn.cursor()
    cursor.execute("UPDATE metadata SET stripe_count = ?, stripe_size_bytes = ? WHERE id = ?", (stripe_count, stripe_size_bytes, file_id))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Layout para '{path}' atualizado com sucesso."})

@app.route('/api/files/download/<int:file_id>')
def download_file(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metadata WHERE id = ? AND is_directory = 0", (file_id,))
    file_meta = cursor.fetchone()
    conn.close()
    if file_meta is None: return jsonify({"error": "Arquivo não encontrado"}), 404
    file_bytes = read_striped_file(file_meta['id'], file_meta['size_bytes'], file_meta['stripe_count'], file_meta['stripe_size_bytes'])
    if file_bytes is None: return jsonify({"error": "Falha ao remontar o arquivo."}), 500
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file_meta['filename'])
    with open(temp_path, 'wb') as f: f.write(file_bytes)
    return send_from_directory(temp_dir, file_meta['filename'], as_attachment=True)

if __name__ == '__main__':
    init_db()
    for path in OST_PATHS: os.makedirs(path, exist_ok=True)
    app.run(debug=True, port=5000)