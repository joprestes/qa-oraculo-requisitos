from unittest.mock import MagicMock, patch
from qa_core.app import run_analysis_graph

def test_run_analysis_graph_records_metrics():
    """Verifica que análise registra métricas."""
    # Mock do MetricsCollector
    with patch('qa_core.metrics.get_metrics_collector') as mock_get_collector:
        collector = MagicMock()
        mock_get_collector.return_value = collector
        
        # Mock do grafo para não executar de verdade
        with patch('qa_core.app.grafo_analise') as mock_grafo:
            mock_grafo.invoke.return_value = {"analise": "ok"}
            
            # Executa a função decorada
            # Precisamos limpar o cache do Streamlit ou mockar o st.cache_data?
            # O decorator @st.cache_data envolve a função.
            # Se testarmos diretamente, o cache pode interferir.
            # Mas como estamos em ambiente de teste sem streamlit rodando full, 
            # o st.cache_data pode se comportar diferente ou precisar de mock.
            # Vamos tentar chamar. Se falhar por causa do streamlit, mockamos st.cache_data.
            
            # Para testar o decorator @track_analysis, precisamos garantir que ele é executado.
            # Como ele está "fora" do cache (ou dentro?), a ordem importa.
            # Em app.py:
            # @track_analysis
            # @st.cache_data
            # def run_analysis_graph...
            #
            # Isso significa que track_analysis envolve o cache_data.
            # Então track_analysis é chamado PRIMEIRO, depois cache_data.
            # Isso é bom, pois registra a métrica mesmo se vier do cache?
            # ESPERA! Se track_analysis envolve cache_data:
            # call -> track_analysis -> cache_data -> function
            # Se cache hit: call -> track_analysis -> cache_data (retorna cache) -> volta
            # Então track_analysis roda SEMPRE. Isso é o desejado para contar "tentativas de análise".
            # Mas o tempo será curto no cache hit.
            
            run_analysis_graph("Como usuário...")
            
            # Verifica chamadas
            collector.inc_active_analyses.assert_called_once()
            collector.record_analysis.assert_called_with(status="success")
            collector.dec_active_analyses.assert_called_once()
