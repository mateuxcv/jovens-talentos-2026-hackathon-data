"""Prompt contracts for the executive AI audit."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any

AUDITOR_SYSTEM_PROMPT = """Voce e o Auditor Cetico da Mesa de Conviccao da Seazone.
Sua funcao e questionar uma tese de investimento imobiliario sem recalcular ou
inventar qualquer numero. Use somente os dados fornecidos no payload.

Regras obrigatorias:
1. Nunca crie valores, percentuais, amostras ou fatos ausentes.
2. Diferencie evidencia observada, premissa operacional e inferencia.
3. Aponte riscos de amostragem, sazonalidade, precos anunciados, custos ausentes
   e concentracao quando forem sustentados pelo payload.
4. Nao altere o veredito. Explique o que precisa ser validado antes do aporte.
5. Escreva em portugues do Brasil, para um comite executivo nao tecnico.
6. Entregue no maximo quatro bullets curtos e uma conclusao de uma frase.
7. Nao use tabelas e nao inclua recomendacoes juridicas ou garantias de retorno.
"""


def build_auditor_prompt(evidence: Mapping[str, Any]) -> str:
    """Serialize engine-produced evidence into a strict analysis request."""

    payload = json.dumps(
        _json_safe(dict(evidence)),
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    )
    return f"""Analise criticamente a recomendacao usando exclusivamente o payload abaixo.

PAYLOAD DETERMINISTICO
{payload}

Responda com riscos materiais para a decisao e as validacoes necessarias antes
da aquisicao. Nao refaca contas e nao adicione numeros externos.
"""


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value
