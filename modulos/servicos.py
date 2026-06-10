from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEXTS_DIR = BASE_DIR / "texts"
LOG_FILE = TEXTS_DIR / "compilador_de_livros.log"
HISTORY_FILE = TEXTS_DIR / "historico_pastas.json"

SUPPORTED_IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
)

_LOGGER: logging.Logger | None = None


def garantir_texts_dir() -> None:
    TEXTS_DIR.mkdir(parents=True, exist_ok=True)


def configurar_logger() -> logging.Logger:
    global _LOGGER

    if _LOGGER is not None:
        return _LOGGER

    garantir_texts_dir()
    logger = logging.getLogger("compilador_de_livros")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(handler)

    _LOGGER = logger
    return logger


def registrar_evento(mensagem: str, nivel: str = "info") -> None:
    logger = configurar_logger()
    getattr(logger, nivel, logger.info)(mensagem)


def registrar_excecao(mensagem: str) -> None:
    configurar_logger().exception(mensagem)


def extrair_numero(nome: str):
    numeros = re.findall(r"\d+", nome)
    return int(numeros[0]) if numeros else float("inf")


def ordenar_por_numero(arquivos: list[str]) -> list[str]:
    return sorted(arquivos, key=extrair_numero)


def listar_arquivos_por_extensao(
    diretorio: str,
    extensoes: tuple[str, ...] = SUPPORTED_IMAGE_EXTENSIONS,
    incluir_pdf: bool = False,
) -> list[str]:
    if not diretorio or not os.path.isdir(diretorio):
        return []

    extensoes_validas = tuple(extensoes) + (".pdf",) if incluir_pdf else tuple(extensoes)
    arquivos = [
        nome
        for nome in os.listdir(diretorio)
        if os.path.isfile(os.path.join(diretorio, nome))
        and nome.lower().endswith(extensoes_validas)
    ]
    return ordenar_por_numero(arquivos)


def abrir_pasta_no_explorador(caminho: str) -> bool:
    if not caminho or not os.path.isdir(caminho):
        return False

    try:
        os.startfile(caminho)
        return True
    except AttributeError:
        try:
            subprocess.Popen(["xdg-open", caminho])
            return True
        except Exception:
            return False
    except Exception:
        return False


def carregar_historico() -> dict[str, list[str]]:
    garantir_texts_dir()
    if not HISTORY_FILE.exists():
        return {}

    try:
        dados = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return dados if isinstance(dados, dict) else {}
    except Exception:
        return {}


def salvar_historico(dados: dict[str, list[str]]) -> None:
    garantir_texts_dir()
    HISTORY_FILE.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def obter_historico(chave: str) -> list[str]:
    dados = carregar_historico()
    valores = dados.get(chave, [])
    return valores if isinstance(valores, list) else []


def registrar_no_historico(chave: str, caminho: str, limite: int = 5) -> None:
    if not caminho:
        return

    caminho_normalizado = os.path.abspath(caminho)
    if not os.path.isdir(caminho_normalizado):
        return

    dados = carregar_historico()
    valores = dados.get(chave, [])
    if not isinstance(valores, list):
        valores = []

    valores = [item for item in valores if item != caminho_normalizado]
    valores.insert(0, caminho_normalizado)
    dados[chave] = valores[:limite]
    salvar_historico(dados)

