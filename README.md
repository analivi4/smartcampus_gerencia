# SmartCampus — Automated Planning Management System (APMS)

Sistema de gerenciamento automatizado de dispositivos IoT (ar-condicionado e iluminacao) em campus universitario, utilizando planejamento PDDL com o planejador POPF-TIF e integracao com FIWARE Orion Broker.

## Origem

`smartcampus-container` e `smartcampus-service` foram adaptados do repositorio original:
[https://github.com/wellingtonumbelino/smartcampus](https://github.com/wellingtonumbelino/smartcampus)

Os arquivos `script.py`, `mock_orion.py` e `config_campus*.json` sao originais deste repositorio.

---

## Arquitetura

```
script.py  ──────────────►  smartcampus-service (FastAPI :8000)
    │                              │
    │  le config_campus.json       │  gera PDDL, executa planner
    │  busca estado no Orion       │
    ▼                              ▼
FIWARE Orion Broker        smartcampus-container (Docker POPF-TIF)
(atuadores IoT)
```

| Modulo | Descricao |
|---|---|
| `smartcampus-container` | Container Docker com o planejador PDDL (POPF-TIF) |
| `smartcampus-service` | Backend FastAPI — gera o problema PDDL, executa o planner, agenda as acoes via APScheduler |
| `script.py` | Orquestrador externo — le a grade horaria, busca estado dos atuadores no Orion e envia o plano ao servico |
| `mock_orion.py` | Mock local do Orion Broker para testes sem infraestrutura real |
| `config_campus.json` | Mapeamento dos dispositivos e grade horaria do campus |

---

## Pre-requisitos

- Python 3.10+
- Docker instalado e em execucao
- Acesso ao FIWARE Orion Broker (ou `mock_orion.py` para testes locais)

---

## Como executar (testes locais)

### Terminal 1 — Mock Orion

```bash
pip install fastapi uvicorn
python mock_orion.py
```

Sobe em `http://localhost:1026`.

### Terminal 2 — Servico

```bash
cd smartcampus-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 3 — Orquestrador

```bash
# Apontando para o mock (sem tocar no Orion real)
ORION_URL=http://localhost:1026 CAMPUS_CONFIG=config_campus_sim_c1.json python script.py
```

Variaveis de ambiente do `script.py`:

| Variavel | Padrao | Descricao |
|---|---|---|
| `ORION_URL` | `http://<orion-host>:1026` | URL do Orion Broker |
| `CAMPUS_CONFIG` | `config_campus.json` | Arquivo de configuracao do campus |

Variaveis do servico:

| Variavel | Padrao | Descricao |
|---|---|---|
| `CAMPUS_DOMAIN` | `data/domain.pddl` | Dominio PDDL (use `data/domain_sim.pddl` para simulacao) |
| `ORION_URL` | `http://<orion-host>:1026` | URL do Orion para envio de comandos |
| `IOT_API_KEY` | — | Chave de autenticacao da API IoT |
| `FIWARE_SERVICE` | `smartufc` | Header fiware-service |
| `FIWARE_SERVICE_PATH` | `/campusquixada` | Header fiware-servicepath |

---

## Dominios PDDL

| Arquivo | Uso |
|---|---|
| `smartcampus-service/data/domain.pddl` | Producao — duracoes reais (turn_on = 1h) |
| `smartcampus-service/data/domain_sim.pddl` | Simulacao — duracoes reduzidas para testes rapidos |

---

## Verificar jobs agendados

```bash
curl http://localhost:8000/scheduler/jobs
```
