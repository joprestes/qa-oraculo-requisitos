"""
Testes unitários para o módulo de progresso.
"""

import pytest
from unittest.mock import MagicMock, patch
from qa_core.progress import ProgressTracker, track_progress


class TestProgressTracker:
    """Testes para a classe ProgressTracker."""

    def test_initialization(self):
        """Testa inicialização do tracker."""
        tracker = ProgressTracker(3, "Test Operation")
        assert tracker.total_steps == 3
        assert tracker.current_step == 0
        assert tracker.description == "Test Operation"
        assert tracker.progress_bar is None
        assert tracker.status_text is None

    @patch("qa_core.progress.st")
    def test_start(self, mock_st):
        """Testa início da barra de progresso."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        tracker = ProgressTracker(3, "Test")
        tracker.start()

        mock_st.progress.assert_called_once_with(0)
        mock_st.empty.assert_called_once()
        assert tracker.progress_bar == mock_progress
        assert tracker.status_text == mock_status
        mock_status.text.assert_called_once_with("Test (0/3)")

    @patch("qa_core.progress.st")
    def test_start_without_description(self, mock_st):
        """Testa início sem descrição."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        tracker = ProgressTracker(3)
        tracker.start()

        mock_st.progress.assert_called_once_with(0)
        mock_st.empty.assert_called_once()
        # Não deve chamar text se não há descrição
        mock_status.text.assert_not_called()

    @patch("qa_core.progress.st")
    def test_update(self, mock_st):
        """Testa atualização do progresso."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        tracker = ProgressTracker(3, "Test")
        tracker.start()
        tracker.update("Step 1")

        assert tracker.current_step == 1
        mock_progress.progress.assert_called_with(1 / 3)
        mock_status.text.assert_called_with("Step 1 (1/3)")

    @patch("qa_core.progress.st")
    def test_multiple_updates(self, mock_st):
        """Testa múltiplas atualizações."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        tracker = ProgressTracker(3, "Test")
        tracker.start()
        tracker.update("Step 1")
        tracker.update("Step 2")
        tracker.update("Step 3")

        assert tracker.current_step == 3
        # Última chamada deve ser com progresso 100%
        mock_progress.progress.assert_called_with(1.0)
        mock_status.text.assert_called_with("Step 3 (3/3)")

    @patch("qa_core.progress.st")
    def test_finish(self, mock_st):
        """Testa finalização da barra."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        tracker = ProgressTracker(3)
        tracker.start()
        tracker.finish()

        mock_progress.empty.assert_called_once()
        mock_status.empty.assert_called_once()

    @patch("qa_core.progress.st")
    def test_finish_without_start(self, mock_st):
        """Testa finalização sem ter iniciado."""
        tracker = ProgressTracker(3)
        # Não deve dar erro
        tracker.finish()


class TestTrackProgress:
    """Testes para o context manager track_progress."""

    @patch("qa_core.progress.st")
    def test_context_manager(self, mock_st):
        """Testa uso como context manager."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        steps = ["Step 1", "Step 2"]
        with track_progress(steps, "Test") as tracker:
            assert isinstance(tracker, ProgressTracker)
            assert tracker.total_steps == 2
            tracker.update("Step 1")

        # Deve ter chamado finish ao sair do contexto
        mock_progress.empty.assert_called_once()
        mock_status.empty.assert_called_once()

    @patch("qa_core.progress.st")
    def test_context_manager_with_exception(self, mock_st):
        """Testa que finish é chamado mesmo com exceção."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        steps = ["Step 1"]
        with pytest.raises(ValueError):
            with track_progress(steps) as tracker:
                tracker.update("Step 1")
                raise ValueError("Test error")

        # Finish deve ter sido chamado mesmo com erro
        mock_progress.empty.assert_called_once()
        mock_status.empty.assert_called_once()

    @patch("qa_core.progress.st")
    def test_full_workflow(self, mock_st):
        """Testa workflow completo."""
        mock_progress = MagicMock()
        mock_status = MagicMock()
        mock_st.progress.return_value = mock_progress
        mock_st.empty.return_value = mock_status

        steps = ["Analyzing", "Processing", "Finalizing"]
        with track_progress(steps, "Complete Operation") as tracker:
            tracker.update("Analyzing")
            tracker.update("Processing")
            tracker.update("Finalizing")

        # Verifica que start foi chamado
        mock_st.progress.assert_called_once_with(0)
        mock_st.empty.assert_called_once()

        # Verifica que progress foi atualizado 3 vezes
        assert mock_progress.progress.call_count == 3

        # Verifica que finish foi chamado
        mock_progress.empty.assert_called_once()
        mock_status.empty.assert_called_once()
