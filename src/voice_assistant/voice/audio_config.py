from dataclasses import dataclass


@dataclass(frozen=True)
class AudioConfig:
    sample_rate: int
    channels: int
    format: int
    chunk_size: int
