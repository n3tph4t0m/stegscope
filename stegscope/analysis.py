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
    return text[:MAX_OUTPUT] + f"\n... (output truncated, {len(text)} bytes total)"


def _simple_runner(binary: str, extra: list[str]):
    def run(path: Path, timeout: int) -> Result:
        start = time.perf_counter()
        try:
            code, out = _capture([binary, *extra, str(path)], timeout)
        except subprocess.TimeoutExpired:
            return Result("timeout", f"Timed out after {timeout}s.")
        status = "ok" if code == 0 or out else "empty"
        return Result(status, _trim(out) or "No output.", duration=time.perf_counter() - start)

    return run


def _strings_runner(path: Path, timeout: int) -> Result:
    start = time.perf_counter()
    try:
        code, out = _capture(["strings", "-n", "6", str(path)], timeout)
    except subprocess.TimeoutExpired:
        return Result("timeout", f"Timed out after {timeout}s.")

    lines = out.splitlines()
    flags = sorted({m.group(0) for line in lines for m in FLAG_PATTERN.finditer(line)})
    keywords = [line for line in lines if KEYWORD_PATTERN.search(line)]

    blocks = []
    if flags:
        blocks.append("### Flag-like patterns\n" + "\n".join(flags))
    if keywords:
        blocks.append(
            "### Sensitive lines\n" + "\n".join(dict.fromkeys(keywords[:200]))
        )
    if not blocks:
        blocks.append(f"No notable pattern among {len(lines)} extracted strings.")

    return Result(
        "ok",
        _trim("\n\n".join(blocks)),
        highlights=flags,
        duration=time.perf_counter() - start,
    )


TOOLS: list[Tool] = [
    Tool(
        "file",
        "File type",
        "file",
        "Identifies the real format regardless of the extension.",
        _simple_runner("file", []),
    ),
    Tool(
        "exiftool",
        "Metadata",
        "exiftool",
        "Extracts EXIF metadata, comments and hidden fields.",
        _simple_runner("exiftool", ["-a", "-u", "-g1"]),
    ),
    Tool(
        "strings",
        "Strings (CTF-filtered)",
        "strings",
        "Searches for flag-like patterns and sensitive lines.",
        _strings_runner,
    ),
    Tool(
        "binwalk",
        "Embedded files",
        "binwalk",
        "Detects signatures of hidden files or archives.",
        _simple_runner("binwalk", []),
    ),
    Tool(
        "zsteg",
        "LSB (PNG/BMP)",
        "zsteg",
        "Analyses the least-significant bit planes of PNG and BMP images.",
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
            entry.update(status="unavailable", output=f"{tool.binary} is not installed on the server.")
        elif not tool.supports(ext):
            entry.update(status="skipped", output=f"Not applicable to .{ext} files.")
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
