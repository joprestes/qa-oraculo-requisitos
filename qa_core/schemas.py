# ==============================
# schemas.py
# ==============================


from pydantic import BaseModel, Field


class AnaliseUS(BaseModel):
    avaliacao_geral: str
    pontos_ambiguos: list[str] = Field(default_factory=list)
    perguntas_para_po: list[str] = Field(default_factory=list)
    sugestao_criterios_aceite: list[str] = Field(default_factory=list)
    riscos_e_dependencias: list[str] = Field(default_factory=list)
