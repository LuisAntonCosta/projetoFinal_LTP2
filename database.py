import sqlite3

class Database:
    def __init__(self, db_file="tarefas.db"):
        """Inicializa a conexão com o banco de dados e cria as tabelas se não existirem."""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria as tabelas 'projetos' e 'tarefas' com o relacionamento de chave estrangeira."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projetos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente',
                projeto_id INTEGER NOT NULL,
                FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    # --- Funções CRUD para Projetos ---
    def adicionar_projeto(self, nome):
        try:
            self.cursor.execute("INSERT INTO projetos (nome) VALUES (?)", (nome,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Ocorre se o nome do projeto já existir (devido à restrição UNIQUE)
            return False

    def listar_projetos(self):
        self.cursor.execute("SELECT * FROM projetos ORDER BY nome")
        return self.cursor.fetchall()

    def atualizar_projeto(self, id_projeto, novo_nome):
        try:
            self.cursor.execute("UPDATE projetos SET nome = ? WHERE id = ?", (novo_nome, id_projeto))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def excluir_projeto(self, id_projeto):
        self.cursor.execute("DELETE FROM projetos WHERE id = ?", (id_projeto,))
        self.conn.commit()

    # --- Funções CRUD para Tarefas ---
    def adicionar_tarefa(self, descricao, projeto_id):
        self.cursor.execute("INSERT INTO tarefas (descricao, projeto_id) VALUES (?, ?)", (descricao, projeto_id))
        self.conn.commit()

    def listar_tarefas_por_projeto(self, projeto_id):
        self.cursor.execute("SELECT * FROM tarefas WHERE projeto_id = ? ORDER BY status, descricao", (projeto_id,))
        return self.cursor.fetchall()

    def atualizar_status_tarefa(self, id_tarefa, novo_status):
        self.cursor.execute("UPDATE tarefas SET status = ? WHERE id = ?", (novo_status, id_tarefa))
        self.conn.commit()

    def excluir_tarefa(self, id_tarefa):
        self.cursor.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))
        self.conn.commit()

    def fechar_conexao(self):
        self.conn.close()
