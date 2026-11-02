# Contributing to StegScope

Thanks for your interest. This project is intentionally simple; any contribution
that preserves that readability is welcome.

## Setting up the environment

```bash
git clone https://github.com/qkjhdflj/stegscope.git
cd stegscope
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Adding an analysis tool

The engine is driven by a declarative registry in `stegscope/analysis.py`. To
wire in a new tool, add a `Tool` entry to the `TOOLS` list:

```python
Tool(
    "foremost",
    "Carving",
    "foremost",
    "Recovers files by signature.",
    _simple_runner("foremost", ["-T"]),
    extensions={"png", "jpg", "bmp"},  # optional
)
```

- `available()` automatically detects a missing binary via `shutil.which`.
- Calls go through `subprocess` without a shell, with a timeout.
- For custom handling, write a `runner(path, timeout) -> Result` function
  modelled on `_strings_runner`.

## Style

- Readable code, no superfluous comments.
- No dependency added without a real need.

## Proposing a change

1. Create a dedicated branch.
2. Check that the application starts and that an analysis completes.
3. Open a pull request describing the need and the solution.
