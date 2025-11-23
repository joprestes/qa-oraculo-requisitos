# 📊 Guia de Observabilidade - QA Oráculo

Este guia explica como habilitar e usar as funcionalidades de observabilidade do QA Oráculo, incluindo métricas Prometheus e rastreamento de performance.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Instalação](#instalação)
- [Métricas Disponíveis](#métricas-disponíveis)
- [Configuração do Prometheus](#configuração-do-prometheus)
- [Dashboards no Grafana](#dashboards-no-grafana)
- [Queries PromQL Úteis](#queries-promql-úteis)

---

## 🎯 Visão Geral

O QA Oráculo possui um sistema de métricas **opcional** baseado em Prometheus que permite monitorar:

- ✅ Quantidade de análises realizadas (sucesso/erro)
- 📦 Exportações por formato
- 🤖 Chamadas ao LLM por provedor
- ⏱️ Latência de operações
- 💾 Tamanho do cache
- 🚨 Erros por tipo

> **Nota**: As métricas são **opcionais** e só funcionam se as dependências de observabilidade estiverem instaladas.

---

## 📦 Instalação

### 1. Instalar Dependências de Observabilidade

```bash
pip install -r requirements-observability.txt
```

Isso instalará:
- `prometheus-client` - Cliente Prometheus para Python
- `opentelemetry-api` - API OpenTelemetry (futuro)
- `opentelemetry-sdk` - SDK OpenTelemetry (futuro)

### 2. Verificar Instalação

```python
from qa_core.metrics import get_metrics_collector

collector = get_metrics_collector()
print(f"Métricas habilitadas: {collector.enabled}")
```

Se retornar `True`, as métricas estão funcionando! 🎉

---

## 📊 Métricas Disponíveis

### Contadores (Counters)

| Métrica | Descrição | Labels |
|---------|-----------|--------|
| `qa_oraculo_analyses_total` | Total de análises realizadas | `status` (success, error) |
| `qa_oraculo_exports_total` | Total de exportações | `format`, `status` |
| `qa_oraculo_llm_calls_total` | Total de chamadas ao LLM | `provider`, `status` |
| `qa_oraculo_errors_total` | Total de erros | `error_type` |

### Histogramas (Histograms)

| Métrica | Descrição | Labels | Buckets |
|---------|-----------|--------|---------|
| `qa_oraculo_analysis_duration_seconds` | Tempo de análise de US | - | 1, 2, 5, 10, 20, 30, 60, 120s |
| `qa_oraculo_export_duration_seconds` | Tempo de exportação | `format` | 0.1, 0.5, 1, 2, 5, 10s |
| `qa_oraculo_llm_call_duration_seconds` | Tempo de chamada LLM | `provider` | 1, 2, 5, 10, 20, 30, 60s |

### Gauges (Valores Instantâneos)

| Métrica | Descrição |
|---------|-----------|
| `qa_oraculo_cache_size` | Número de itens no cache de LLM |
| `qa_oraculo_active_analyses` | Número de análises em andamento |

### Info (Metadados)

| Métrica | Descrição | Labels |
|---------|-----------|--------|
| `qa_oraculo_app_info` | Informações da aplicação | `version`, `python_version` |

---

## 🔧 Configuração do Prometheus

### 1. Instalar Prometheus

**Linux/Mac:**
```bash
# Download
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*
```

**Docker:**
```bash
docker run -d -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

### 2. Configurar `prometheus.yml`

Crie um arquivo `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'qa-oraculo'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### 3. Iniciar Prometheus

```bash
./prometheus --config.file=prometheus.yml
```

Acesse: http://localhost:9090

---

## 📈 Dashboards no Grafana

### 1. Instalar Grafana

**Docker:**
```bash
docker run -d -p 3000:3000 grafana/grafana
```

Acesse: http://localhost:3000 (usuário: `admin`, senha: `admin`)

### 2. Adicionar Data Source

1. Vá em **Configuration** → **Data Sources**
2. Clique em **Add data source**
3. Selecione **Prometheus**
4. URL: `http://localhost:9090`
5. Clique em **Save & Test**

### 3. Criar Dashboard

Importe o dashboard JSON abaixo ou crie manualmente:

**Painéis Sugeridos:**

1. **Taxa de Análises** (Graph)
   - Query: `rate(qa_oraculo_analyses_total[5m])`
   - Agrupa por `status`

2. **Latência P95 de Análises** (Graph)
   - Query: `histogram_quantile(0.95, rate(qa_oraculo_analysis_duration_seconds_bucket[5m]))`

3. **Exportações por Formato** (Pie Chart)
   - Query: `sum by (format) (qa_oraculo_exports_total)`

4. **Taxa de Erros** (Graph)
   - Query: `rate(qa_oraculo_errors_total[5m])`

5. **Chamadas LLM por Provedor** (Bar Chart)
   - Query: `sum by (provider) (qa_oraculo_llm_calls_total)`

6. **Tamanho do Cache** (Gauge)
   - Query: `qa_oraculo_cache_size`

---

## 🔍 Queries PromQL Úteis

### Taxa de Sucesso de Análises

```promql
sum(rate(qa_oraculo_analyses_total{status="success"}[5m])) 
/ 
sum(rate(qa_oraculo_analyses_total[5m])) * 100
```

### Latência Média de Exportações PDF

```promql
rate(qa_oraculo_export_duration_seconds_sum{format="pdf"}[5m])
/
rate(qa_oraculo_export_duration_seconds_count{format="pdf"}[5m])
```

### Top 3 Tipos de Erro

```promql
topk(3, sum by (error_type) (rate(qa_oraculo_errors_total[1h])))
```

### Chamadas LLM por Segundo (últimos 5 minutos)

```promql
sum(rate(qa_oraculo_llm_calls_total[5m])) by (provider)
```

### Percentil 99 de Latência de Análise

```promql
histogram_quantile(0.99, 
  rate(qa_oraculo_analysis_duration_seconds_bucket[5m])
)
```

### Análises Ativas no Momento

```promql
qa_oraculo_active_analyses
```

---

## 🚨 Alertas Recomendados

### Alta Taxa de Erros

```yaml
- alert: HighErrorRate
  expr: |
    sum(rate(qa_oraculo_errors_total[5m])) > 0.1
  for: 5m
  annotations:
    summary: "Taxa de erros alta no QA Oráculo"
    description: "Mais de 0.1 erros/segundo nos últimos 5 minutos"
```

### Latência Alta de Análise

```yaml
- alert: HighAnalysisLatency
  expr: |
    histogram_quantile(0.95, 
      rate(qa_oraculo_analysis_duration_seconds_bucket[5m])
    ) > 30
  for: 10m
  annotations:
    summary: "Latência de análise muito alta"
    description: "P95 de latência acima de 30 segundos"
```

### Cache Muito Grande

```yaml
- alert: CacheTooLarge
  expr: qa_oraculo_cache_size > 1000
  for: 5m
  annotations:
    summary: "Cache de LLM muito grande"
    description: "Cache com mais de 1000 itens"
```

---

## 🧪 Testando Métricas Localmente

### 1. Executar Aplicação com Métricas

```bash
# Certifique-se de ter instalado requirements-observability.txt
streamlit run qa_core/app.py
```

### 2. Realizar Algumas Operações

- Analise uma User Story
- Exporte para PDF
- Exporte para Markdown

### 3. Verificar Métricas

Se você implementou o endpoint `/metrics`, acesse:

```bash
curl http://localhost:8000/metrics
```

Você verá algo como:

```
# HELP qa_oraculo_analyses_total Total de análises de User Stories realizadas
# TYPE qa_oraculo_analyses_total counter
qa_oraculo_analyses_total{status="success"} 5.0
qa_oraculo_analyses_total{status="error"} 1.0

# HELP qa_oraculo_exports_total Total de exportações realizadas
# TYPE qa_oraculo_exports_total counter
qa_oraculo_exports_total{format="pdf",status="success"} 3.0
qa_oraculo_exports_total{format="markdown",status="success"} 2.0
```

---

## 🔐 Segurança

> **Importante**: O endpoint `/metrics` expõe informações sobre o uso da aplicação. Em produção:

1. **Proteja o endpoint** com autenticação
2. **Use firewall** para permitir apenas IPs do Prometheus
3. **Não exponha** métricas publicamente
4. **Sanitize labels** para não vazar PII

---

## 📚 Recursos Adicionais

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)

---

## 🆘 Troubleshooting

### Métricas não aparecem no Prometheus

1. Verifique se `prometheus-client` está instalado
2. Verifique se o endpoint `/metrics` está acessível
3. Verifique configuração do `prometheus.yml`
4. Verifique logs do Prometheus: `docker logs <container_id>`

### Métricas sempre em zero

1. Verifique se as operações estão sendo executadas
2. Verifique se os decorators estão aplicados corretamente
3. Verifique logs da aplicação para erros

### Grafana não conecta ao Prometheus

1. Verifique se Prometheus está rodando: `curl http://localhost:9090`
2. Verifique URL do data source no Grafana
3. Verifique se não há firewall bloqueando

---

**Última atualização**: Novembro 2025
