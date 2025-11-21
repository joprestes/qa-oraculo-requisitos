# ==============================
# schemas.py - Schemas de Validação
# ==============================
# Schemas Pydantic para validação de entrada e sanitização de dados


from pydantic import BaseModel, Field, field_validator


class AnaliseUS(BaseModel):
    avaliacao_geral: str
    pontos_ambiguos: list[str] = Field(default_factory=list)
    perguntas_para_po: list[str] = Field(default_factory=list)
    sugestao_criterios_aceite: list[str] = Field(default_factory=list)
    riscos_e_dependencias: list[str] = Field(default_factory=list)


class UserStoryInput(BaseModel):
    """Schema de validação para entrada de User Story."""

    content: str = Field(
        ..., min_length=10, max_length=50000, description="Conteúdo da User Story"
    )


    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Sanitiza o conteúdo removendo caracteres potencialmente perigosos."""
        if not v or not v.strip():
            raise ValueError("User Story não pode estar vazia")

        # Remove caracteres de controle (exceto newline, tab, carriage return)
        sanitized = "".join(
            char for char in v if char.isprintable() or char in ("\n", "\t", "\r")
        )
        
        # Validação básica de keywords (opcional, mas recomendada para User Stories)
        normalized = sanitized.lower()
        if "como " not in normalized:
             # Não vamos bloquear, apenas sanitizar, pois a validação de negócio ocorre no app.py
             # Mas podemos logar ou marcar se quisermos ser estritos.
             pass

        return sanitized.strip()


class AnalysisEditInput(BaseModel):
    """Schema para validação dos campos editados da análise."""
    
    avaliacao_geral: str = Field(..., min_length=5, max_length=5000)
    pontos_ambiguos: list[str] = Field(default_factory=list)
    perguntas_para_po: list[str] = Field(default_factory=list)
    sugestao_criterios_aceite: list[str] = Field(default_factory=list)
    riscos_e_dependencias: list[str] = Field(default_factory=list)

    @field_validator("avaliacao_geral")
    @classmethod
    def sanitize_avaliacao(cls, v: str) -> str:
        return "".join(c for c in v if c.isprintable() or c in ("\n", "\t", "\r")).strip()

    @field_validator("pontos_ambiguos", "perguntas_para_po", "sugestao_criterios_aceite", "riscos_e_dependencias")
    @classmethod
    def sanitize_lists(cls, v: list[str]) -> list[str]:
        return [
            "".join(c for c in item if c.isprintable() or c in ("\n", "\t", "\r")).strip()
            for item in v
            if item and item.strip()
        ]


class AnalysisReportInput(BaseModel):
    """Schema de validação para relatórios de análise."""

    user_story: str = Field(..., min_length=10, max_length=50000)
    analysis_report: str = Field(..., min_length=1, max_length=100000)
    test_plan_report: str = Field(default="", max_length=100000)
    test_plan_summary: str | None = Field(default=None, max_length=50000)
    test_plan_df_json: str | None = Field(default=None, max_length=500000)

    @field_validator("user_story", "analysis_report", "test_plan_report")
    @classmethod
    def sanitize_text_fields(cls, v: str) -> str:
        """Sanitiza campos de texto."""
        if not v:
            return v
        return "".join(
            char for char in v if char.isprintable() or char in ("\n", "\t", "\r")
        )

