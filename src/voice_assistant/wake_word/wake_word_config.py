from dataclasses import dataclass


@dataclass(frozen=True)
class WakeWordConfig:
    model_path: str
    wake_word: str
    inference_framework: str
    threshold: float = 0.5
