# AGENTS.md

Instrucciones para agentes de IA que trabajen en este repositorio. El README está
dirigido a personas; este archivo contiene lo que un agente necesita y no puede inferir
del código. Escribí código, comentarios y documentación en **español**.

## Resumen del proyecto

Asistente de voz local en Python. Pipeline secuencial:

```
Micrófono → Wake word → Captura → Speech-to-Text → LLM/Agente → (Herramientas/MCP: pendiente) → Text-to-Speech
```

El punto de entrada es `voice_assistant.app:main`; `run()` arma cada etapa con un
builder `_build_*()` que lee variables de entorno y las ensambla en el loop principal.

## Entorno y comandos

El proyecto usa **uv**. Ejecutá todo a través de `uv run` (nunca `python`/`pytest`
pelados: no corren en el venv del proyecto).

```bash
uv sync                      # instalar dependencias (incluye grupo dev)
uv run voice-assistant       # ejecutar el asistente (= python -m voice_assistant)
uv run pytest                # tests unitarios
uv run pytest -m integration # tests de integración (requieren micrófono/audio real)
uv run ruff format .         # formatear
uv run ruff check . --fix    # lint
uv run pyright               # chequeo de tipos
```

Antes de dar una tarea por terminada, dejá en verde: `uv run ruff format .`,
`uv run ruff check .`, `uv run pyright` y `uv run pytest`. Son los mismos checks que
corre `pre-commit` (ruff + pyright + `uv-export` de `requirements.txt`).

## Restricciones que no se negocian

- **Python 3.11 exclusivamente** (`>=3.11,<3.12`). `openwakeword` no soporta 3.12+. No
  subas el pin.
- **`numpy<2`**: restricción de `openwakeword`. Antes de agregar una dependencia,
  verificá que no exija `numpy>=2` (ya descartó a `kokoro-onnx` por esto).
- **PyTorch solo CPU**: `torch` está forzado a la variante CPU vía
  `[[tool.uv.index]]` + `[tool.uv.sources]` en `pyproject.toml` para evitar bajar el
  stack CUDA (~2 GB). No lo reviertas.
- Todo el stack de inferencia es **local y CPU** (wake word, STT, TTS). Mantené ese
  criterio al elegir librerías o modelos: liviano y sin GPU.

## Arquitectura: patrón por módulo

Cada etapa del pipeline es un paquete bajo `src/voice_assistant/` con la misma
estructura de tres piezas. Seguila al agregar o modificar motores:

1. **Interfaz abstracta** (`ABC`) que define el contrato — p. ej. `TextToSpeech`,
   `SpeechToText`, `LLMProvider`. El resto de la app depende de la interfaz, no de la
   implementación.
2. **Config** `@dataclass(frozen=True)` con defaults — p. ej. `TextToSpeechConfig`.
3. **Implementación concreta** que recibe la config en `__init__` — p. ej. `PiperTTS`,
   `FasterWhisperSTT`.

El `__init__.py` del paquete reexporta las tres con `__all__`. La selección de motor y
la lectura de entorno viven en los builders `_build_*()` de `app.py`, no dentro de los
módulos. Ejemplo de referencia completo: `src/voice_assistant/tts/`.

```
src/voice_assistant/
├── app.py          # builders _build_*() + loop principal
└── tts/            # una etapa; el resto sigue el mismo patrón
    ├── text_to_speech.py         # interfaz (ABC)
    ├── text_to_speech_config.py  # config (dataclass frozen)
    └── piper_tts.py              # implementación
```

Paquetes: `wake_word/`, `speech_to_text/`, `llm/`, `agent/`, `tts/`, `voice/`
(micrófono). Audio en todo el pipeline: PCM int16 mono (el micrófono captura a 16 kHz).

## Estilo de código

- **El formato lo decide `ruff format`** (`line-length = 100`). No ajustes el ancho del
  código a mano: ruff junta o parte las líneas según corresponda.
- **Docstrings y comentarios SÍ son manuales**: ruff no reflowea prosa. Ajustá a ~100
  columnas a mano, estilo Google (`Args:`, `Attributes:`), con referencias a código en
  reST (`` ``valor`` ``). Mirá `llm/llm_config.py` como referencia.
- Comentá el *porqué* no obvio, no lo que el código ya dice.
- Atributos internos de clase con guion bajo (`self._voice`); la config suele quedar
  pública (`self.config`) siguiendo a los motores existentes.
- Type hints en todo. `pyright` en modo `standard` debe pasar sin errores.

## Tests

- `pytest`, un archivo por módulo en `tests/` (`test_<modulo>.py`). Mockeá la librería
  externa (`WhisperModel`, `PiperVoice`, `PyAudio`, cliente OpenAI) y testeá solo la
  lógica propia. Referencia: `tests/test_piper_tts.py`.
- Las pruebas que requieren hardware/audio real van marcadas con `@pytest.mark.integration`
  y quedan excluidas por defecto (`addopts = -m 'not integration'`).
- Agregá o actualizá tests para la lógica no trivial que toques.

## Gotchas

- **El micrófono NO es configurable por entorno.** `AudioConfig` está fijo en `run()`
  (16 kHz, mono) porque wake word y STT lo exigen. No inventes variables `MIC_*`.
- **Los modelos no se versionan.** `models/whisper/` y `models/piper/` están en
  `.gitignore`; se descargan con sus comandos (ver README). En un entorno limpio, la
  voz TTS por defecto (`es_AR-daniela-high`) debe descargarse antes del primer arranque.
- `requirements.txt` es **generado** por el hook `uv-export`; no lo edites a mano.
- **No cambies `version` en `pyproject.toml` a mano.** La maneja `semantic-release` en
  CI (`.github/workflows/release.yml`) al mergear en `main`, a partir de los mensajes de
  commit; por eso importan los Conventional Commits.
- Dos instancias `PyAudio` coexisten (micrófono y TTS). No hay conflicto: el uso es
  half-duplex (o escucha, o habla). No las unifiques sin motivo.

## Troubleshooting

- Al reproducir audio en Linux, ALSA imprime warnings (`Unknown PCM`, `Invalid card`,
  etc.) en stderr. Son **ruido esperado** de la enumeración de dispositivos, no errores:
  si el audio suena, ignoralos. El TTS necesita un dispositivo de salida configurado;
  en entornos headless puede no haberlo.

## Seguridad

- **Nunca commitees `.env`** (puede contener datos sensibles, como una API key). El
  template versionado es `.env.example`; si agregás una variable, actualizá ambos y la
  tabla del README.
- No imprimas ni loguees valores de secrets (API keys, tokens). Referenciálos por
  nombre de variable, no por valor.
- Las credenciales del LLM llegan solo por entorno (`LLM_API_KEY`); no las hardcodees
  en el código ni en tests.

## Commits

Seguí la convención de Conventional Commits definida en
`.kiro/steering/conventional-commits.md` (fuente de verdad). No ejecutes `git push`
ni comandos destructivos sin autorización explícita.
