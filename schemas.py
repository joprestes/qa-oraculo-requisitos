from typing import List
from pydantic import BaseModel, Field

class AnaliseUS(BaseModel):
    avaliacao_geral: str
    pontos_ambiguos: List[str] = Field(default_factory=list)
    perguntas_para_po: List[str] = Field(default_factory=list)
    sugestao_criterios_aceite: List[str] = Field(default_factory=list)
    riscos_e_dependencias: List[str] = Field(default_factory=list)
