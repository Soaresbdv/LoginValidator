import sqlite3

def init_db():
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            twofa_secret TEXT,
            twofa_enabled BOOLEAN DEFAULT 1,
            verified BOOLEAN DEFAULT 0
        )
    ''')
    
    # Tabela de códigos temporários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS twofa_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Banco de dados inicializado com sucesso!")