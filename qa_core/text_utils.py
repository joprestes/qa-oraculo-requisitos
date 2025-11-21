import datetime
import json
import re
import unicodedata


# ==========================================================
# NORMALIZAÇÃO E NOMES DE ARQUIVOS
# ==========================================================


def normalizar_string(texto: str) -> str:
    """Remove acentos e caracteres especiais de uma string.

    Normaliza uma string removendo acentuação e diacríticos, mantendo
    apenas caracteres ASCII básicos. Útil para geração de nomes de arquivos
    seguros e comparações de texto.

    Args:
        texto: String a ser normalizada.

    Returns:
        String normalizada sem acentos e caracteres especiais.

    Examples:
        >>> normalizar_string("Criação de usuário")
        'Criacao de usuario'
        >>> normalizar_string("Éção")
        'Ecao'
    """
    nfkd_form = unicodedata.normalize("NFD", texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str:
    """Gera nome de arquivo limpo, seguro e único baseado na User Story.

    Cria um nome de arquivo válido a partir do texto da User Story,
    removendo caracteres especiais, limitando o tamanho e adicionando
    timestamp para garantir unicidade.

    Args:
        user_story: Texto da User Story para gerar o nome do arquivo.
        extension: Extensão do arquivo (sem ponto), ex: 'pdf', 'csv', 'md'.

    Returns:
        Nome de arquivo seguro no formato: 'nome-base_YYYYMMDD_HHMMSS.extension'
        Se user_story estiver vazia, retorna 'relatorio_qa_oraculo.extension'.

    Examples:
        >>> gerar_nome_arquivo_seguro("Como usuário, quero fazer login", "pdf")
        'como-usuario-quero-fazer-login_20251120_215500.pdf'
        >>> gerar_nome_arquivo_seguro("", "csv")
        'relatorio_qa_oraculo.csv'

    Note:
        - Usa apenas a primeira linha da User Story
        - Limita o nome base a 50 caracteres
        - Remove acentos e caracteres especiais
        - Substitui espaços e underscores por hífens
    """
    if not user_story:
        return f"relatorio_qa_oraculo.{extension}"

    primeira_linha_us = user_story.split("\n")[0].lower()
    nome_sem_acentos = normalizar_string(primeira_linha_us)
    nome_base = re.sub(r"[^\w\s-]", "", nome_sem_acentos).strip()
    nome_base = re.sub(r"[-_\s]+", "-", nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.{extension}"


# ==========================================================
#  FUNÇÕES DE SUPORTE E LIMPEZA
# ==========================================================


def get_flexible(data_dict: dict, keys: list, default_value):
    """
    Busca flexível de valores por múltiplas chaves possíveis.

    Tenta recuperar o valor de um dicionário procurando sequencialmente por
    uma lista de chaves. Retorna o primeiro valor encontrado ou o valor padrão.

    Args:
        data_dict: Dicionário onde a busca será realizada.
        keys: Lista de chaves a serem procuradas (em ordem de prioridade).
        default_value: Valor a ser retornado se nenhuma chave for encontrada.

    Returns:
        O valor encontrado ou o default_value.
    """
    if not isinstance(data_dict, dict):
        return default_value
    for key in keys:
        if key in data_dict:
            return data_dict[key]
    return default_value


def clean_markdown_report(report_text: str) -> str:
    """
    Remove blocos de código Markdown do texto.

    Remove delimitadores de código (```) do início e do fim da string,
    além de espaços em branco extras. Útil para limpar respostas de LLMs
    que retornam o conteúdo envolto em blocos de código.

    Args:
        report_text: Texto contendo possíveis blocos Markdown.

    Returns:
        Texto limpo, sem os delimitadores de código.
    """
    if not isinstance(report_text, str):
        return ""
    text = re.sub(r"^```[a-zA-Z]*\n", "", report_text.strip())
    text = re.sub(r"\n```$", "", text)
    return text.strip()


def extract_json_from_text(text: str) -> str | None:
    """Extrai JSON de uma string que pode conter formatação Markdown.

    Args:
        text: String contendo a resposta, possivelmente com JSON envolto em Markdown.

    Returns:
        String contendo apenas o JSON extraído, ou None se não encontrado.
    """
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if match:
        return match.group(0).strip()
    return None


def parse_json_strict(s: str):
    """
    Faz parsing seguro de JSON retornado pela IA.

    Tenta extrair JSON de strings que podem conter Markdown ou texto ao redor.
    Utiliza `extract_json_from_text` para pré-processamento.

    Args:
        s: String contendo o JSON (puro ou misturado com texto).

    Returns:
        Objeto Python (dict ou list) resultante do parsing.

    Raises:
        ValueError: Se não for possível decodificar um JSON válido.
    """
    s = s.strip()
    # Tenta extrair se estiver envolto em markdown
    extracted = extract_json_from_text(s)
    if extracted:
        s = extracted

    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise ValueError(f"Falha ao decodificar JSON: {e}") from e


# ==========================================================
#  Salva Gherkin após edição do usuário
# ==========================================================


def gerar_relatorio_md_dos_cenarios(df):
    """
    Gera texto Markdown consolidado com os cenários Gherkin atuais.

    Itera sobre um DataFrame de cenários e cria uma representação formatada
    em Markdown para cada um, incluindo título, prioridade, critério de aceitação
    e o próprio cenário Gherkin em um bloco de código.

    Args:
        df: DataFrame contendo colunas 'titulo', 'prioridade', 'criterio_de_aceitacao_relacionado', 'cenario'.

    Returns:
        String contendo o relatório Markdown completo.
    """
    if df is None or df.empty:
        return "⚠️ Nenhum cenário disponível para gerar relatório."

    blocos = []
    for _, row in df.iterrows():
        titulo = row.get("titulo", "Sem título")
        prioridade = row.get("prioridade", "-")
        criterio = row.get("criterio_de_aceitacao_relacionado", "")
        cenario = row.get("cenario", "")

        bloco = f"""### 🧩 {titulo}
**Prioridade:** {prioridade}  
**Critério de Aceitação:** {criterio}

```gherkin
{cenario.strip()}
```
"""
        blocos.append(bloco)
    return "\n".join(blocos)
