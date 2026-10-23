# CHANGELOG

<!-- version list -->

## v0.6.0 (2026-10-23)

### Chores

- Versionar config de Kiro (lsp y mcp)
  ([`05379ac`](https://github.com/comejia/voice-assistant/commit/05379ac8e9c359b5180fd158f47c13c2d6c9e0f0))

### Documentation

- Agregar agents.md para asistentes de ia
  ([`8fcca47`](https://github.com/comejia/voice-assistant/commit/8fcca47cbeba09d047e85b16ebe6d7124cd4f4cb))

- Reestructurar readme y documentar el tts
  ([`fa4bd51`](https://github.com/comejia/voice-assistant/commit/fa4bd51457807ea3e90add546e09eac43bdbd2ad))

### Features

- **tts**: Integrar piper como motor de text-to-speech
  ([`50ee320`](https://github.com/comejia/voice-assistant/commit/50ee3200e3956d36ae8ccc8fb9f2fa7a9e798b2b))


## v0.5.0 (2026-10-23)

### Bug Fixes

- Resolver errores de tipos de pyright
  ([`8a5399f`](https://github.com/comejia/voice-assistant/commit/8a5399ffe8c97a9666056293fc8d34c5b7df5430))

### Chores

- Añadir pyright como hook de pre-commit
  ([`cfa70ca`](https://github.com/comejia/voice-assistant/commit/cfa70cafa64aa400e00c48190a5e1d29ca16f7d2))

- Configurar pyright para el proyecto
  ([`5c3e181`](https://github.com/comejia/voice-assistant/commit/5c3e181a22a1ce1fc1e4c7bd4bd1ac3b38830de9))

### Documentation

- Añadir steering ponytail y corregir frontmatter
  ([`ea9c718`](https://github.com/comejia/voice-assistant/commit/ea9c718c5fb887344cb370f69e5d79bc70203773))

### Features

- Integrar LLM y agente en el pipeline
  ([`c2c0e68`](https://github.com/comejia/voice-assistant/commit/c2c0e6886727da37ace8accd73ee6de65d1e0032))


## v0.4.0 (2026-10-22)

### Features

- **stt**: Añadir transcripción local con faster-whisper
  ([`372430c`](https://github.com/comejia/voice-assistant/commit/372430c76e2e93d95f959e0dee67b920ccbc7f6e))


## v0.3.0 (2026-10-16)

### Chores

- **deps**: Añadir heed-wakeword con torch CPU
  ([`2baaf0a`](https://github.com/comejia/voice-assistant/commit/2baaf0a8f4e5cc4beebb5ad3d932ccf701ebe1b4))

### Features

- **wake-word**: Añadir modelo custom "hola deby"
  ([`da016cc`](https://github.com/comejia/voice-assistant/commit/da016cc35764fb38e2b5cbfb0692d609eef2d34e))

- **wake-word**: Integrar motor heed
  ([`f1002c6`](https://github.com/comejia/voice-assistant/commit/f1002c63f2746d334266a1e42701525bd96dbf25))

### Refactoring

- **tests**: Fixture de micrófono con teardown
  ([`93ba531`](https://github.com/comejia/voice-assistant/commit/93ba531658b2c9b7298fb3e1cb19ade1aba2e33b))

- **wake-word**: Unificar config en WakeWordConfig
  ([`42107f8`](https://github.com/comejia/voice-assistant/commit/42107f84b20592a6f7dbecf326d37d7677c1cc3a))


## v0.2.0 (2026-10-14)

### Features

- **wake-word**: Configurar modelo desde entorno
  ([`b50d68f`](https://github.com/comejia/voice-assistant/commit/b50d68f32d5fc5beb6ff7e507b46e77cd5d48355))


## v0.1.2 (2026-10-06)

### Bug Fixes

- **scripts**: Guardar audio en la raíz del repo
  ([`56e20c8`](https://github.com/comejia/voice-assistant/commit/56e20c82cbb359a001fe510be527e08faf618e5a))

### Continuous Integration

- **release**: Simplificar checkout del workflow
  ([`052afda`](https://github.com/comejia/voice-assistant/commit/052afda07178cb502fc009694f571a95aa954a16))


## v0.1.1 (2026-10-06)

### Bug Fixes

- **release**: Mantener versiones 0.x en PSR
  ([`accd48b`](https://github.com/comejia/voice-assistant/commit/accd48becbd2cf65ced94a4351d21c108efb4173))

- **scripts**: Cerrar micrófono siempre al grabar
  ([`b4f36e4`](https://github.com/comejia/voice-assistant/commit/b4f36e4a062ffbe6c6dacd402a4b1b732dd893bf))

### Continuous Integration

- **release**: Configurar semantic-release
  ([`8527501`](https://github.com/comejia/voice-assistant/commit/852750177121353bca0669ad5e9b35d47bfc518a))

- **release**: Traer tags con fetch explícito
  ([`8080f11`](https://github.com/comejia/voice-assistant/commit/8080f11888a04701b824be82ed12ded8f94610d6))

- **release**: Traer tags en checkout para PSR
  ([`d4da7e6`](https://github.com/comejia/voice-assistant/commit/d4da7e6d70ae7f66d3742cd126b7831298ce0c09))


## v0.1.0 (2026-10-05)

- Initial Release
