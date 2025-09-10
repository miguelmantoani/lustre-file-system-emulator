import sqlite3

DATABASE_NAME = 'mds.db'

def get_db_connection():
    """Cria uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados e cria a tabela de metadados se não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verifica se a tabela já existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metadata'")
    if cursor.fetchone() is None:
        print("Criando a tabela 'metadata'...")
        conn.execute('''
            CREATE TABLE metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                parent_id INTEGER,
                is_directory BOOLEAN NOT NULL,
                size_bytes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Configurações do Layout (Lustre)
                stripe_count INTEGER DEFAULT 1,
                stripe_size_bytes INTEGER DEFAULT 1048576, -- Padrão: 1MB
                
                FOREIGN KEY (parent_id) REFERENCES metadata(id)
            );
        ''')
        # Cria o diretório raiz
        conn.execute(
            "INSERT INTO metadata (filename, parent_id, is_directory) VALUES (?, ?, ?)",
            ('/', None, True)
        )
        conn.commit()
    else:
        print("Tabela 'metadata' já existe.")
        
    conn.close()

if __name__ == '__main__':
    init_db()