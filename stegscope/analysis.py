import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

FLAG_PATTERN = re.compile(r"[A-Za-z0-9_]{2,16}\{[^}\r\n]{1,256}\}")
KEYWORD_PATTERN = re.compile(
    r"(flag|ctf|password|passwd|secret|private[_ ]?key|BEGIN [A-Z ]+KEY)",
    re.IGNORECASE,
)
MAX_OUTPUT = 20000


@dataclass
class Tool:
    key: str
    label: str
    binary: str
    description: str
    runner: Callable[[Path], "Result"]
    extensions: Optional[set] = None

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    def supports(self, ext: str) -> bool:
        return self.extensions is None or ext.lower().lstrip(".") in self.extensions


@dataclass
class Result:
    status: str
    output: str = ""
    highlights: list = field(default_factory=list)
    duration: float = 0.0


def _capture(args: list[str], timeout: int) -> tuple[int, str]:
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=timeout,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def _trim(text: str) -> str:
    if len(text) <= MAX_OUTPUT:
        return text
    return text[:MAX_OUTPUT] + f"\n... (sortie tronquée, {len(text)} octets au total)"


def _simple_runner(binary: str, extra: list[str]):
    def run(path: Path, timeout: int) -> Result:
        start = time.perf_counter()
        try:
            code, out = _capture([binary, *extra, str(path)], timeout)
        except subprocess.TimeoutExpired:
            return Result("timeout", f"Dépassement du délai ({timeout}s).")
        status = "ok" if code == 0 or out else "empty"
        return Result(status, _trim(out) or "Aucune sortie.", duration=time.perf_counter() - start)

    return run


def _strings_runner(path: Path, timeout: int) -> Result:
    start = time.perf_counter()
    try:
        code, out = _capture(["strings", "-n", "6", str(path)], timeout)
    except subprocess.TimeoutExpired:
        return Result("timeout", f"Dépassement du délai ({timeout}s).")

    lines = out.splitlines()
    flags = sorted({m.group(0) for line in lines for m in FLAG_PATTERN.finditer(line)})
    keywords = [line for line in lines if KEYWORD_PATTERN.search(line)]

    blocks = []
    if flags:
        blocks.append("### Motifs de type flag\n" + "\n".join(flags))
    if keywords:
        blocks.append(
            "### Lignes sensibles\n" + "\n".join(dict.fromkeys(keywords[:200]))
        )
    if not blocks:
        blocks.append(f"Aucun motif notable parmi {len(lines)} chaînes extraites.")

    return Result(
        "ok",
        _trim("\n\n".join(blocks)),
        highlights=flags,
        duration=time.perf_counter() - start,
    )


TOOLS: list[Tool] = [
    Tool(
        "file",
        "Type de fichier",
        "file",
        "Identifie le format réel indépendamment de l'extension.",
        _simple_runner("file", []),
    ),
    Tool(
        "exiftool",
        "Métadonnées",
        "exiftool",
        "Extrait les métadonnées EXIF, commentaires et champs cachés.",
        _simple_runner("exiftool", ["-a", "-u", "-g1"]),
    ),
    Tool(
        "strings",
        "Chaînes (filtrées CTF)",
        "strings",
        "Recherche les motifs de flag et les lignes sensibles.",
        _strings_runner,
    ),
    Tool(
        "binwalk",
        "Fichiers embarqués",
        "binwalk",
        "Détecte les signatures de fichiers ou archives dissimulés.",
        _simple_runner("binwalk", []),
    ),
    Tool(
        "zsteg",
        "LSB (PNG/BMP)",
        "zsteg",
        "Analyse les plans de bits de poids faible des images PNG et BMP.",
        _simple_runner("zsteg", ["-a"]),
        extensions={"png", "bmp"},
    ),
]


def run_all(path: Path, ext: str, timeout: int) -> list[dict]:
    report = []
    for tool in TOOLS:
        entry = {
            "key": tool.key,
            "label": tool.label,
            "description": tool.description,
        }
        if not tool.available():
            entry.update(status="unavailable", output=f"{tool.binary} n'est pas installé sur le serveur.")
        elif not tool.supports(ext):
            entry.update(status="skipped", output=f"Non applicable au format .{ext}.")
        else:
            result = tool.runner(path, timeout)
            entry.update(
                status=result.status,
                output=result.output,
                highlights=result.highlights,
                duration=round(result.duration, 2),
            )
        report.append(entry)
    return report
