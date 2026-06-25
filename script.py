import time
import json
import requests
import schedule
import logging
from datetime import datetime, timedelta
from pathlib import Path

import os

# Para testar localmente sem afetar o Orion real, defina a variável de
# ambiente ORION_URL antes de rodar o script:
#   export ORION_URL=http://localhost:1026   ( aponta pro mock local)
# Se a variável não for definida, usa o Orion real por padrão.
ORION_URL = os.getenv("ORION_URL", "ocutado para o git")

SERVICE_URL      = "http://localhost:8000"
HORARIO_EXECUCAO = "07:00"   # horário do agendamento automático diário

.
FIWARE_SERVICE     = "smartufc"
FIWARE_SERVICEPATH = "/campusquixada"

CONFIG_PATH = Path(os.getenv("CAMPUS_CONFIG", "config_campus.json"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("smartcampus_client.log"),
        logging.StreamHandler()
    ]
)

DIAS_SEMANA_EN = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday"
]

# Duração mínima de uma aula em horas, igual à duração da ação turn_on
# no domain.pddl. Usada para validar consistência da grade.
DURACAO_MINIMA_TURN_ON = 1.0


# ─── Carregar configuração externa ────────────────────────────────────────────
def carregar_configuracao():
    try:
        if not CONFIG_PATH.exists():
            logging.error(f"Arquivo de configuração não encontrado: {CONFIG_PATH}")
            return None, None

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        mapeamento = config.get("mapeamento_dispositivos", {})
        grade      = config.get("grade_semanal", {})

        if not mapeamento:
            logging.warning("mapeamento_dispositivos vazio no arquivo de configuração.")
        if not grade:
            logging.warning("grade_semanal vazia no arquivo de configuração.")

        return mapeamento, grade

    except json.JSONDecodeError as e:
        logging.error(f"Erro de sintaxe no {CONFIG_PATH}: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Erro ao carregar configuração: {e}")
        return None, None


# ─── Conversão de horário absoluto para tempo relativo PDDL ───────────────────
def horario_para_tempo_relativo(horario_str, momento_referencia):
    """
    Converte um horário absoluto ("HH:MM") em unidades de tempo PDDL
    relativas ao momento em que o script está rodando agora.

    O resultado é arredondado para o minuto mais próximo (1/60 de hora).

    Exemplo: se agora são 07:00 e o evento é "08:00", retorna 1.0
             se agora são 12:14 e o evento é "12:20", retorna 0.1
             se agora são 14:00 e o evento é "08:00", retorna -6.0 (já passou)
    """
    h, m = map(int, horario_str.split(":"))
    horario_evento = momento_referencia.replace(
        hour=h, minute=m, second=0, microsecond=0
    )
    diferenca_horas = (horario_evento - momento_referencia).total_seconds() / 3600

    # arredonda para o minuto mais próximo (evita flutuações de sub-segundo)
    diferenca_arredondada = round(diferenca_horas * 60) / 60
    return diferenca_arredondada


# ─── Passo 1: buscar entidades reais do Orion ─────────────────────────────────
def buscar_entidades_orion():
    logging.info("Buscando estado atual dos atuadores no Orion Broker...")
    try:
        resposta = requests.get(
            f"{ORION_URL}/v2/entities",
            headers={
                "Accept": "application/json",
                "fiware-service": FIWARE_SERVICE,
                "fiware-servicepath": FIWARE_SERVICEPATH
            },
            params={"type": "Atuador", "limit": 1000}
        )
        resposta.raise_for_status()
        entidades = resposta.json()
        logging.info(f"{len(entidades)} entidades encontradas no Orion.")
        return entidades
    except Exception as e:
        logging.error(f"Erro ao buscar entidades no Orion: {e}")
        return None


def validar_dispositivos_mapeados(mapeamento_dispositivos, entidades_orion):
    """
    Compara o mapeamento manual (config_campus.json) com o que de fato
    existe no Orion agora. Dispositivos mapeados mas ausentes no Orion
    são reportados explicitamente e excluídos do plano dessa execução,
    evitando que o script tente enviar comandos para uma entidade
    inexistente (o que resultaria em 404 no momento da atuação).

    Retorna um novo dicionário de mapeamento contendo apenas os
    dispositivos confirmados como existentes.
    """
    ids_existentes = {e["id"] for e in entidades_orion}
    mapeamento_validado = {}
    ausentes = []

    for urn, info in mapeamento_dispositivos.items():
        if urn in ids_existentes:
            mapeamento_validado[urn] = info
        else:
            ausentes.append(urn)

    if ausentes:
        logging.warning(
            f"{len(ausentes)} dispositivo(s) mapeado(s) não encontrado(s) "
            f"no Orion e serão ignorados nesta execução:"
        )
        for urn in ausentes:
            info = mapeamento_dispositivos[urn]
            logging.warning(
                f"    {urn} (sala={info['room']}, tipo={info['tipo']}) — "
                f"verificar se foi removido/expirado no Orion"
            )

    return mapeamento_validado


# ─── Passo 2: montar o ProblemDefinitionDTO a partir da grade do dia ──────────
def montar_payload_do_dia(mapeamento_dispositivos, grade_semanal):
    agora      = datetime.now()
    dia_atual  = DIAS_SEMANA_EN[agora.weekday()]

    logging.info(
        f"Montando problema PDDL para {dia_atual}, "
        f"a partir de {agora.strftime('%H:%M')}"
    )

    grade_hoje = grade_semanal.get(dia_atual, {})

    if not grade_hoje:
        logging.info(f"Sem aulas previstas para {dia_atual}. Ciclo não será enviado.")
        return None

    # Agrupar dispositivos mapeados por sala e tipo
    rooms_map = {}
    for urn, info in mapeamento_dispositivos.items():
        sala = info["room"]
        tipo = info["tipo"]

        if sala not in rooms_map:
            rooms_map[sala] = {"acs": [], "lights": []}

        if tipo == "air_conditioner":
            rooms_map[sala]["acs"].append(urn)
        elif tipo == "light":
            rooms_map[sala]["lights"].append(urn)

    salas = list(rooms_map.keys())
    acs   = [ac  for info in rooms_map.values() for ac  in info["acs"]]
    luzes = [luz for info in rooms_map.values() for luz in info["lights"]]

    def _alias(urn): return urn.replace(":", "_").lower()
    device_map = {_alias(dev_id): dev_id for dev_id in acs + luzes}
    acs   = [_alias(d) for d in acs]
    luzes = [_alias(d) for d in luzes]


    # people_in_room inicial: por padrão 0, mas se uma aula já estiver
    # em andamento no momento da execução, a sala começa OCUPADA
    # (assume que já está ligado, só desliga no horário de saída)
    people_in_room_inicial = {sala: 0 for sala in salas}
    ac_temperature_inicial = {_alias(ac): 0 for info in rooms_map.values() for ac in info["acs"]}

    timed_events = [
        {"time": 0.0, "type": "predicate", "predicate": "operating_hour"}
    ]

    # Estado inicial: todos os dispositivos começam ociosos (prontos para ligar)
    for sala_id, info in rooms_map.items():
        for ac in info["acs"]:
            timed_events.append({
                "time": 0.0, "type": "predicate",
                "predicate": "ac_idle", "args": [sala_id, _alias(ac)]
            })
        for luz in info["lights"]:
            timed_events.append({
                "time": 0.0, "type": "predicate",
                "predicate": "light_idle", "args": [sala_id, _alias(luz)]
            })

    salas_com_aula_relevante = set()
    slot_counter = {}   # sala_id -> índice do próximo slot futuro
    slot_objects = []   # nomes dos objetos PDDL do tipo slot
    slot_goals   = []   # goals class_acknowledged a adicionar no final

    for sala_id, aulas in grade_hoje.items():
        if sala_id not in rooms_map:
            logging.warning(f"Sala {sala_id} na grade mas sem dispositivos mapeados, ignorada.")
            continue

        # Ordena por horário de início e pré-calcula tempos relativos
        aulas_com_tempo = [
            (aula, horario_para_tempo_relativo(aula["start"], agora),
                   horario_para_tempo_relativo(aula["end"],   agora))
            for aula in sorted(aulas, key=lambda a: a["start"])
        ]

        sala_ja_teve_aula = False
        anterior_foi_back_to_back = False

        for i, (aula, t_inicio, t_fim) in enumerate(aulas_com_tempo):
            pessoas = int(aula["people"])

            # Detecta back-to-back: próxima aula começa exatamente quando esta termina.
            # Nesse caso o evento people=0 não é emitido para evitar conflito de
            # timed literals no mesmo instante.
            proxima = aulas_com_tempo[i + 1] if i + 1 < len(aulas_com_tempo) else None
            back_to_back = proxima is not None and abs(proxima[1] - t_fim) < 0.01

            # Caso 1: aula totalmente no futuro → evento normal de entrada (e saída se não back-to-back)
            if t_inicio >= 0:
                # Cria slot PDDL para esta aula (garante que o planner sirva cada aula)
                slot_index = slot_counter.get(sala_id, 0)
                slot_counter[sala_id] = slot_index + 1
                slot_name = f"{sala_id}_s{slot_index}"
                slot_objects.append(slot_name)

                # Janela da aula: abre no início, fecha no fim
                timed_events.append({
                    "time": t_inicio, "type": "predicate",
                    "predicate": "class_window_open", "args": [sala_id, slot_name]
                })
                timed_events.append({
                    "time": t_fim, "type": "negated_predicate",
                    "predicate": "class_window_open", "args": [sala_id, slot_name]
                })

                # Goal: o planner deve confirmar que serviu esta aula com AC+luz ligados
                slot_goals.append({"predicate": "class_acknowledged", "args": [sala_id, slot_name]})

                if sala_ja_teve_aula and not anterior_foi_back_to_back:
                    info = rooms_map[sala_id]
                    for ac in info["acs"]:
                        timed_events.append({
                            "time": t_inicio, "type": "negated_predicate",
                            "predicate": "ac_on", "args": [sala_id, _alias(ac)]
                        })
                        timed_events.append({
                            "time": t_inicio, "type": "negated_predicate",
                            "predicate": "ac_off", "args": [sala_id, _alias(ac)]
                        })
                    for luz in info["lights"]:
                        timed_events.append({
                            "time": t_inicio, "type": "negated_predicate",
                            "predicate": "light_on", "args": [sala_id, _alias(luz)]
                        })
                        timed_events.append({
                            "time": t_inicio, "type": "negated_predicate",
                            "predicate": "light_off", "args": [sala_id, _alias(luz)]
                        })
                    logging.info(
                        f"  {sala_id}: reset de ac_on/ac_off/light_on/light_off em t={t_inicio:.2f} "
                        f"(aula {aula['start']}–{aula['end']}) para forçar novo ciclo"
                    )

                timed_events.append({
                    "time": t_inicio, "type": "fluent",
                    "fluent": "people_in_room", "args": [sala_id], "value": pessoas
                })
                if back_to_back:
                    logging.info(
                        f"  {sala_id}: aula futura {aula['start']}–{aula['end']} "
                        f"(t={t_inicio:.2f} a t={t_fim:.2f}) [back-to-back → sem evento de saída]"
                    )
                else:
                    timed_events.append({
                        "time": t_fim, "type": "fluent",
                        "fluent": "people_in_room", "args": [sala_id], "value": 0
                    })
                    logging.info(
                        f"  {sala_id}: aula futura {aula['start']}–{aula['end']} "
                        f"(t={t_inicio:.2f} a t={t_fim:.2f})"
                    )
                salas_com_aula_relevante.add(sala_id)
                sala_ja_teve_aula = True
                anterior_foi_back_to_back = back_to_back

            # Caso 2: aula em andamento agora (já começou, ainda não terminou)
            elif t_inicio < 0 <= t_fim:
                people_in_room_inicial[sala_id] = pessoas
                if back_to_back:
                    logging.info(
                        f"  {sala_id}: aula EM ANDAMENTO {aula['start']}–{aula['end']} "
                        f"— sala inicia ocupada [back-to-back → sem evento de saída em t={t_fim:.2f}]"
                    )
                else:
                    timed_events.append({
                        "time": t_fim, "type": "fluent",
                        "fluent": "people_in_room", "args": [sala_id], "value": 0
                    })
                    logging.info(
                        f"  {sala_id}: aula EM ANDAMENTO {aula['start']}–{aula['end']} "
                        f"— sala inicia ocupada, desliga em t={t_fim:.2f}"
                    )
                salas_com_aula_relevante.add(sala_id)
                sala_ja_teve_aula = True
                anterior_foi_back_to_back = back_to_back

            # Caso 3: aula já terminou totalmente → ignorada
            else:
                anterior_foi_back_to_back = False
                logging.info(
                    f"  {sala_id}: aula já encerrada {aula['start']}–{aula['end']}, ignorada"
                )

    if not salas_com_aula_relevante:
        logging.info("Nenhuma aula relevante restante para hoje. Ciclo não será enviado.")
        return None

    fluentes = {
        "people_in_room":    people_in_room_inicial,
        "ac_temperature":    ac_temperature_inicial,
        "metric_total_cost": 0
    }

    # horário de ponta: 17:30, calculado de forma absoluta também
    t_peak = horario_para_tempo_relativo("17:30", agora)
    if t_peak >= 0:
        timed_events.append(
            {"time": t_peak, "type": "predicate", "predicate": "peak_hours"}
        )

    predicados_goal = []
    for sala_id in salas_com_aula_relevante:
        info = rooms_map[sala_id]
        for ac in info["acs"]:
            predicados_goal.append({"predicate": "ac_off",    "args": [sala_id, _alias(ac)]})
        for luz in info["lights"]:
            predicados_goal.append({"predicate": "light_off", "args": [sala_id, _alias(luz)]})
    predicados_goal.extend(slot_goals)
    predicados_goal.append({"predicate": "out_work_time"})

    payload = {
        "name":   f"smart-campus-plan-{dia_atual}-{agora.strftime('%H%M')}",
        "domain": "smart_campus",
        "objects": {
            "rooms":            salas,
            "air_conditioners": acs,
            "lights":           luzes,
            "slots":            slot_objects
        },
        "init": {
            "fluents":      fluentes,
            "timed_events": timed_events
        },
        "goal":       {"predicates": predicados_goal},
        "metric":     "minimize (metric_total_cost)",
        "device_map": device_map
    }

    logging.info(
        f"Payload montado: {len(salas)} salas | {len(acs)} ACs | "
        f"{len(luzes)} luzes | {len(salas_com_aula_relevante)} salas com aula relevante"
    )
    return payload


# ─── Passo 3: enviar ao serviço ────────────────────────────────────────────────
def solicitar_planejamento(payload):
    logging.info("Enviando problema PDDL para a Camada de Serviço...")
    try:
        resposta = requests.post(
            f"{SERVICE_URL}/planner/run",
            json=payload,
            timeout=300
        )
        resposta.raise_for_status()

        resultado = resposta.json()
        job_id = resultado.get("job_id")
        acoes  = resultado.get("scheduled_actions_count", 0)

        logging.info(
            f"Plano gerado e agendado com sucesso! "
            f"Job ID: {job_id} | Ações: {acoes}"
        )
        return True

    except requests.exceptions.HTTPError as e:
        logging.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
        return False
    except Exception as e:
        logging.error(f"Erro ao solicitar planejamento: {e}")
        return False


# ─── Fluxo completo ───────────────────────────────────────────────────────────
def ciclo_completo():
    logging.info("=" * 50)
    logging.info(
        f"Iniciando ciclo de planejamento - "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    mapeamento, grade = carregar_configuracao()
    if mapeamento is None or grade is None:
        logging.warning("Ciclo interrompido: falha ao carregar configuração.")
        return

    entidades = buscar_entidades_orion()
    if not entidades:
        logging.warning("Ciclo interrompido: falha ao conectar com o Orion.")
        return

    mapeamento_validado = validar_dispositivos_mapeados(mapeamento, entidades)

    if not mapeamento_validado:
        logging.error(
            "Ciclo interrompido: nenhum dispositivo mapeado existe "
            "atualmente no Orion."
        )
        return

    payload = montar_payload_do_dia(mapeamento_validado, grade)
    if not payload:
        logging.info("Ciclo concluído sem geração de plano.")
        return

    solicitar_planejamento(payload)
    logging.info("Ciclo concluído.")


# ─── Agendador ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.info("Orquestrador SmartCampus iniciado (modo: grade horária com horário absoluto).")

    ciclo_completo()  # executa imediatamente, na hora atual real

    schedule.every().day.at(HORARIO_EXECUCAO).do(ciclo_completo)
    logging.info(f"Próxima execução automática agendada para {HORARIO_EXECUCAO} todos os dias.")
    logging.info("O script também pode ser executado manualmente em qualquer horário.")

    while True:
        schedule.run_pending()
        time.sleep(60)