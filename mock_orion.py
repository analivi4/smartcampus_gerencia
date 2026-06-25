# mock_orion.py
# Simula o Orion Broker NGSIv2 para testes sem infraestrutura real.
#
# REGRA TEMPORAL IMPORTANTE:
#   - O campus opera por 15.0 unidades (start_campus_operating dura 15.0)
#   - turn_off dura 1.0 unidade
#   - Portanto: pessoas devem sair até t=14.0 no máximo
#     para o planejador ter tempo de desligar tudo antes do campus fechar
#
# Unidade de tempo padrão: 1.0 = 1 hora real (APP_TIME_UNIT_TO_HOURS=1)
#
# Exemplo de leitura:
#   time=1.0  com execução às 07:00 → evento às 08:00
#   time=6.5  com execução às 07:00 → evento às 13:30
#   time=11.0 com execução às 07:00 → evento às 18:00
#   time=14.0 com execução às 07:00 → evento às 21:00
#
# Para rodar: python mock_orion.py
# Requer:     pip install fastapi uvicorn

from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title="Mock Orion Broker NGSIv2")

# ── Estado simulado do campus ──────────────────────────────────────────────────
# Espelha o que estaria cadastrado no Orion real.
# Cada sala tem um atributo "schedule" com os eventos de ocupação do dia.


ENTIDADES = [
    {
        "id": "urn:ngsi-ld:Atuador:94bb5f8710104d1e",
        "type": "Atuador",
        "descricao": {"value": "Ar condicionado - Bloco 1, Sala 1", "type": "Text"},
        "status":    {"value": "OFF", "type": "Text"}
    },
    {
        "id": "urn:ngsi-ld:Atuador:b7985868de99e91d",
        "type": "Atuador",
        "descricao": {"value": "Luz - Bloco 1, Sala 1", "type": "Text"},
        "status":    {"value": "OFF", "type": "Text"}
    }
]


# ── Endpoints NGSIv2 ───────────────────────────────────────────────────────────

@app.get("/v2/entities")
def listar_entidades(type: str = None, limit: int = 1000):
    resultado = [e for e in ENTIDADES if type is None or e["type"] == type]
    print(f"\n[MOCK ORION] GET /v2/entities?type={type} → devolvendo {len(resultado)} entidades")
    return resultado


@app.patch("/v2/entities/{entity_id}/attrs")
async def atualizar_atributo(entity_id: str, request: Request, type: str = None):
    body = await request.json()

    if "ligar" in body:
        comando = "ligar"
        novo_status = "ON"
    elif "desligar" in body:
        comando = "desligar"
        novo_status = "OFF"
    else:
        comando = "?"
        novo_status = "?"

    valor = body.get(comando, {}).get("value", "?") if comando != "?" else "?"
    print(f"[MOCK ORION] PATCH /v2/entities/{entity_id}/attrs → comando={comando} value={valor} → status={novo_status}")

    for entidade in ENTIDADES:
        if entidade["id"] == entity_id and "status" in entidade:
            entidade["status"]["value"] = novo_status
            break

    return {"status": "ok", "entity": entity_id, "command": comando, "value": valor}


@app.get("/v2/entities/{entity_id}")
def buscar_entidade(entity_id: str):
    """Consulta individual de uma entidade pelo ID."""
    for entidade in ENTIDADES:
        if entidade["id"] == entity_id:
            return entidade
    return {"error": "entity not found", "id": entity_id}


@app.get("/v2/entities/{entity_id}/attrs")
def buscar_atributos(entity_id: str):
    """Retorna apenas os atributos de uma entidade."""
    for entidade in ENTIDADES:
        if entidade["id"] == entity_id:
            return {k: v for k, v in entidade.items() if k not in ("id", "type")}
    return {"error": "entity not found", "id": entity_id}


# ── Inicialização ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Mock Orion Broker NGSIv2")
    print("  Rodando em http://localhost:1026")
    print("=" * 55)
    print(f"  Entidades carregadas: {len(ENTIDADES)}")
    print(f"  Atuadores: {len([e for e in ENTIDADES if e['type'] == 'Atuador'])}")
    print()
    print("  Endpoints disponíveis:")
    print("  GET   /v2/entities")
    print("  GET   /v2/entities/{id}")
    print("  GET   /v2/entities/{id}/attrs")
    print("  PATCH /v2/entities/{id}/attrs")
    print("=" * 55)
    uvicorn.run(app, host="0.0.0.0", port=1026)