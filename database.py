# ==========================================================
# database.py — Módulo de Persistência de Dados (QA Oráculo)
# ==========================================================
# 📘 Responsável por toda a comunicação com o banco SQLite:
#    - Criação e inicialização do banco
#    - Salvamento e leitura de análises realizadas
#    - Exclusão individual e total de registros
#
# 🎯 Princípios QA Oráculo:
#    • Banco testável em memória (usando SQLite :memory:)
#    • Transações seguras e idempotentes (commit sob with)
#    • Acesso simplificado via RowFactory (dict-like)
#    • Compatível com pytest e automações de histórico
#
# 🧩 Boas Práticas:
#    - Nenhum dado sensível é persistido.
#    - Campos None são substituídos por mensagens de fallback.
#    - Todas as funções lidam com exceções de forma segura.
# ==========================================================
import datetime
import sqlite3
import threading
from contextlib import contextmanager

# Adaptador: Python datetime -> str
sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())

# Conversor: str -> Python datetime
sqlite3.register_converter(
    "timestamp", lambda val: datetime.datetime.fromisoformat(val.decode("utf-8"))
)

DB_NAME = "qa_oraculo_history.db"


def get_db_connection():
    """
    Cria uma conexão com o banco de dados SQLite.
    Usa row_factory para permitir acesso por chave (dict-like).
    """
    conn = sqlite3.connect(
        DB_NAME, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Cria a tabela de histórico de análises se não existir.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP NOT NULL,
                user_story TEXT NOT NULL,
                analysis_report TEXT,
                test_plan_report TEXT
            );
            """
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao inicializar DB: {e}")


# Lock global para garantir atomicidade em ambientes multi-thread
_save_lock = threading.Lock()


@contextmanager
def atomic_transaction():
    """
    Context manager para operações atômicas no banco.

    Garante que múltiplas escritas simultâneas não corrompam dados.
    Faz rollback automático em caso de erro.

    Uso:
        with atomic_transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT ...")
            # commit automático ao sair do bloco
    """
    with _save_lock:
        conn = get_db_connection()
        try:
            yield conn
            conn.commit()
            print("✅ Transação commitada com sucesso")
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro na transação, rollback executado: {e}")
            raise
        finally:
            conn.close()


def save_or_update_analysis(
    user_story: str,
    analysis_report: str,
    test_plan_report: str | None = None,
    existing_id: int | None = None,
) -> int:
    """
    Salva ou atualiza análise de forma atômica e segura.

    Args:
        user_story: Texto da User Story (obrigatório)
        analysis_report: Relatório de análise (obrigatório)
        test_plan_report: Plano de testes (opcional)
        existing_id: ID para atualizar (None = novo registro)

    Returns:
        int: ID do registro salvo/atualizado

    Raises:
        ValueError: Se user_story ou analysis_report estiverem vazios
        sqlite3.Error: Em caso de erro no banco
    """
    # Validação de entrada
    if not user_story or not user_story.strip():
        raise ValueError("User Story não pode estar vazia")

    if not analysis_report or not analysis_report.strip():
        raise ValueError("Relatório de análise não pode estar vazio")

    # Sanitização (mantém compatibilidade com código legado)
    user_story = user_story.strip()
    analysis_report = analysis_report.strip()
    test_plan_report = (test_plan_report or "").strip()

    with atomic_transaction() as conn:
        cursor = conn.cursor()
        timestamp = datetime.datetime.now()

        if existing_id:
            # ATUALIZAÇÃO de registro existente
            cursor.execute(
                """
                UPDATE analysis_history
                SET created_at = ?,
                    user_story = ?,
                    analysis_report = ?,
                    test_plan_report = ?
                WHERE id = ?
                """,
                (timestamp, user_story, analysis_report, test_plan_report, existing_id),
            )

            if cursor.rowcount == 0:
                raise ValueError(f"Registro com ID {existing_id} não existe")

            print(f"♻️ Registro {existing_id} atualizado em {timestamp}")
            return existing_id

        else:
            # CRIAÇÃO de novo registro
            cursor.execute(
                """
                INSERT INTO analysis_history
                (created_at, user_story, analysis_report, test_plan_report)
                VALUES (?, ?, ?, ?)
                """,
                (timestamp, user_story, analysis_report, test_plan_report),
            )

            new_id = cursor.lastrowid
            print(f"💾 Novo registro criado: ID {new_id} em {timestamp}")
            return new_id


# ==========================================================
# FUNÇÃO DE MIGRAÇÃO
# ==========================================================
def migrate_to_atomic_saves():
    """
    Função helper para migrar código legado que usa save_analysis_to_history().

    Não precisa ser chamada diretamente, apenas documentação.

    ANTES (código legado):
        save_analysis_to_history(us, analysis, plan)

    DEPOIS (novo código):
        history_id = save_or_update_analysis(us, analysis, plan)
        state.mark_as_saved(history_id)
    """
    # Apenas documentação


def save_analysis_to_history(
    user_story: str, analysis_report: str, test_plan_report: str
):
    """
    Salva uma nova análise no histórico.
    🔒 Correção QA Oráculo:
        - Evita NoneType nos campos.
        - Garante fallback textual caso o Gemini falhe.
        - Mantém compatibilidade total com a estrutura original.
    """
    try:
        # Sanitiza os campos para evitar valores nulos
        user_story = user_story or "⚠️ User Story não disponível."
        analysis_report = analysis_report or "⚠️ Relatório de análise não disponível."
        test_plan_report = (
            test_plan_report
            or "⚠️ Plano de Testes não disponível ou não pôde ser gerado."
        )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.datetime.now()  # TIMESTAMP real, não string
            cursor.execute(
                """
            INSERT INTO analysis_history (created_at, user_story, analysis_report, test_plan_report)
            VALUES (?, ?, ?, ?);
            """,
                (timestamp, user_story, analysis_report, test_plan_report),
            )
            conn.commit()
            print(f"💾 Análise salva no histórico em {timestamp}")
    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao salvar análise: {e}")


def get_all_analysis_history():
    """
    Retorna todas as análises do histórico, ordenadas por data de criação.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, created_at, user_story FROM analysis_history ORDER BY created_at DESC;"
            )
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
            # 🔧 converte para inteiro de forma segura
            cursor.execute(
                "SELECT * FROM analysis_history WHERE id = ?;", (int(analysis_id),)
            )
            row = cursor.fetchone()
            if row is not None:
                return dict(row)
            return None

    except sqlite3.Error as e:
        print(f"[DB ERROR] Falha ao buscar análise {analysis_id}: {e}")
        return None
    except (ValueError, TypeError):
        print(f"[DB ERROR] ID inválido fornecido: {analysis_id}")
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
