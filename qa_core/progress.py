"""
Módulo de indicadores de progresso para operações longas.

Este módulo fornece uma interface simples para rastrear o progresso
de operações que levam tempo, como análise de IA e geração de relatórios.
"""
import streamlit as st
from typing import List, Optional
from contextlib import contextmanager


class ProgressTracker:
    """Gerenciador de barras de progresso para operações longas."""

    def __init__(self, total_steps: int, description: str = ""):
        """
        Inicializa o rastreador de progresso.

        Args:
            total_steps: Número total de etapas da operação
            description: Descrição opcional da operação
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.progress_bar: Optional[st.delta_generator.DeltaGenerator] = None
        self.status_text: Optional[st.delta_generator.DeltaGenerator] = None

    def start(self):
        """Inicia a barra de progresso."""
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        if self.description:
            self.status_text.text(f"{self.description} (0/{self.total_steps})")

    def update(self, step_name: str):
        """
        Atualiza o progresso para a próxima etapa.

        Args:
            step_name: Nome da etapa atual
        """
        self.current_step += 1
        if self.progress_bar and self.status_text:
            progress = self.current_step / self.total_steps
            self.progress_bar.progress(progress)
            self.status_text.text(
                f"{step_name} ({self.current_step}/{self.total_steps})"
            )

    def finish(self):
        """Finaliza e remove a barra de progresso."""
        if self.progress_bar:
            self.progress_bar.empty()
        if self.status_text:
            self.status_text.empty()


@contextmanager
def track_progress(steps: List[str], description: str = ""):
    """
    Context manager para rastrear progresso de operações.

    Uso:
        with track_progress(["Passo 1", "Passo 2", "Passo 3"]) as tracker:
            tracker.update("Passo 1")
            # ... código ...
            tracker.update("Passo 2")
            # ... código ...
            tracker.update("Passo 3")

    Args:
        steps: Lista de nomes das etapas
        description: Descrição opcional da operação

    Yields:
        ProgressTracker: Instância do rastreador de progresso
    """
    tracker = ProgressTracker(len(steps), description)
    tracker.start()
    try:
        yield tracker
    finally:
        tracker.finish()
