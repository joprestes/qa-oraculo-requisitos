import sqlite3
import datetime
# Adaptador: Python datetime -> str
sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())

# Conversor: str -> Python datetime
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode("utf-8")))

DB_NAME = "qa_oraculo_history.db"


def get_db_connection():
    """
    Cria uma conexão com o banco de dados SQLite.
    Usa row_factory para permitir acesso por chave (dict-like).
    """
    conn = sqlite3.connect(DB_NAME, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Cria a tabela de histórico de análises se não existir.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP NOT NULL,
                user_story TEXT NOT NULL,
                analysis_report TEXT,
                test_plan_report TEXT
            );
            """)
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao inicializar DB: {e}")


def save_analysis_to_history(user_story: str, analysis_report: str, test_plan_report: str):
    """
    Salva uma nova análise no histórico.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.datetime.now()  # TIMESTAMP real, não string
            cursor.execute("""
            INSERT INTO analysis_history (created_at, user_story, analysis_report, test_plan_report)
            VALUES (?, ?, ?, ?);
            """, (timestamp, user_story, analysis_report, test_plan_report))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao salvar análise: {e}")


def get_all_analysis_history():
    """
    Retorna todas as análises do histórico, ordenadas por data de criação.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, created_at, user_story FROM analysis_history ORDER BY created_at DESC;")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao buscar histórico: {e}")
        return []


def get_analysis_by_id(analysis_id: int):
    """
    Busca uma análise específica pelo ID.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analysis_history WHERE id = ?;", (analysis_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao buscar análise {analysis_id}: {e}")
        return None


def delete_analysis_by_id(entry_id: int) -> bool:
    """
    Deleta uma análise específica pelo ID.
    Retorna True se algo foi deletado, False caso contrário.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analysis_history WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao deletar análise {entry_id}: {e}")
        return False


def clear_history() -> int:
    """
    Remove todas as análises do histórico.
    Retorna o número de registros apagados.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analysis_history")
            conn.commit()
            return cursor.rowcount
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao limpar histórico: {e}")
        return 0
