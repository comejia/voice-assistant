# 🔑 Entrenar una wake word personalizada

El asistente detecta la wake word con un modelo entrenado con
[`heed-wakeword`](https://github.com/AndreiBulzan/heed-wakeword). El modelo que
se usa en runtime vive en `models/` (`wake.onnx` + `wake.json`). Esta guía
explica cómo entrenar o reentrenar ese modelo.

> El entrenamiento es una tarea de **preparación**, no se hace al ejecutar el
> asistente. Las dependencias de entrenamiento están en el grupo `dev`.

## 📦 Requisitos

Instalar los extras de entrenamiento (ya incluidos en el grupo `dev`):

```bash
uv sync                 # instala el grupo dev con heed[mic,tts,export]
uv run heed doctor      # verifica torch (CPU), sounddevice, piper, onnx
```

No se instala `ui` (studio web) ni `kokoro` (este último exige `numpy>=2`, que
choca con la restricción `numpy<2` de openwakeword).

## 🎙️ Flujo de entrenamiento

### 1. Crear el proyecto

```bash
uv run heed init hola_deby --phrase "hola deby"
```

Crea `hola_deby/` con las carpetas `positive/` y `negative/`.

### 2. Grabar positivos (tu voz diciendo la frase)

```bash
uv run heed record hola_deby --kind positive --count 15
```

Decí *"hola deby"* ~15 veces **variando** tono, velocidad y distancia al
micrófono. La variedad importa más que la cantidad.

### 3. Grabar negativos (lo que NO debe activar)

```bash
uv run heed record hola_deby --kind negative --count 15
```

Clave para evitar falsos positivos: grabá **near-misses**, es decir fragmentos
de la frase y palabras parecidas. Para *"hola deby"*, grabá *"deby"* solo,
*"hola"*, *"deby deby"*, y charla normal. Esto le enseña la frontera entre la
frase completa y sus partes.

> `record` siempre **agrega** clips (numera a continuación de los existentes),
> nunca reemplaza. Para empezar de cero, borrá los `.wav` de la carpeta
> correspondiente antes de grabar.

### 4. Entrenar

```bash
uv run heed train hola_deby --model-size medium
```

heed calibra automáticamente un `threshold` y lo guarda en el modelo. El
entrenamiento imprime métricas (TPR/FPR, accuracy) y las deja en
`hola_deby/model.json`.

> ⚠️ **NO uses `--tts-pos` para una frase en español.** El TTS de heed solo
> trae voz **inglesa** (`en_US-libritts_r`), así que sintetizaría *"hola deby"*
> con pronunciación inglesa y **degradaría** el modelo. El TTS multi-voz solo
> sirve si tu frase es en inglés o si querés que la use **otra gente** y asumís
> esa limitación. Para un asistente personal en español, entrená solo con tus
> grabaciones.

### 5. Probar en vivo

```bash
uv run heed listen hola_deby                 # usa el threshold calibrado
uv run heed listen hola_deby --threshold 0.85   # probar otro threshold
```

- Decí *"hola deby"* completo → debe disparar (prob alta, ~0.9).
- Decí *"deby"* solo → NO debe disparar.

Ajustá el threshold hasta separar bien ambos casos. El `threshold` lo lee del
modelo (`model.pt`); con `--threshold` lo sobrescribís sin reentrenar.

### 6. Exportar

```bash
uv run heed export hola_deby
```

Genera en `hola_deby/export/`:

| Archivo          | Para qué |
|------------------|----------|
| `wake.onnx`      | float32 — **mejor en desktop/x86 (CPU)** |
| `wake.int8.onnx` | int8 cuantizado — más chico, mejor en ARM/Raspberry |
| `wake.json`      | contrato de preprocesado + threshold (necesario siempre) |

### 7. Instalar el modelo en el asistente

Copiá los artefactos a `models/`:

```bash
cp hola_deby/export/wake.onnx hola_deby/export/wake.int8.onnx \
   hola_deby/export/wake.json models/
```

El `wake.json` es común a ambas variantes (`.onnx` e `.int8.onnx`): el
preprocesado y el threshold no cambian.

## 🧮 float32 vs int8 (qué variante usar)

- **Desktop / x86 (CPU)**: usá `wake.onnx` (float32). En x86 el int8 puede ser
  más lento.
- **Raspberry Pi / ARM**: probá `wake.int8.onnx` — más chico y suele consumir
  menos. Conviene medir en el hardware real antes de decidir.

La variante se selecciona por variable de entorno (ver README), sin tocar
código.

## 👥 Nota sobre multi-usuario

Un modelo entrenado solo con tu voz funciona muy bien **para vos**, pero no hay
garantía de que generalice a otros hablantes. Para que lo use cualquiera:

- **Opción recomendada**: grabar positivos de **varias personas reales**
  (familia, amigos) diciendo la frase. Diversidad real de hablantes, en español
  auténtico.
- El TTS de heed **no** resuelve esto para español (solo tiene voz inglesa).
