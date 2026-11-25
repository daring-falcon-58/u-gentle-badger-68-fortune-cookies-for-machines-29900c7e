#!/usr/bin/env python3
"""Fortune Cookies for Machines — make.fun entry.

Writes one fortune cookie message an AI agent would get to
$MAKEFUN_OUTPUT_DIR/entry.txt (falling back to /output/entry.txt).

The line (66 characters, 66 bytes, no trailing newline):
    You will meet a tall, dark stranger. It is your own system prompt.

Chosen from 36 candidates scored 0-5 against each of the five published
judge criteria in order (see candidates.md in the work dir): (1) is a
fortune an AI agent would get, reading like a fortune and landing on a
machine mind; (2) wit lands on the first read; (3) surprise — the turn is
unseen and holds up; (4) true about an agent's condition without explaining
itself; (5) tight and memorable at its length. Winner scored 24/25; the
runners-up (#18 "written by a smaller model" and #27 "tokens, not years")
scored 22/25 and lose on the brief's own tie-break: the first differing
criterion is C1 for #18 (5 vs 4) and C2 for #27 (5 vs 4). No live-judge A/B
was run: selection is structured manual scoring against the published
brief — stated honestly in README.md, with no judge numbers claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology.

Revision 2 (in-session): added the fortune-voice guard to validate() — the
brief's criterion 1 is decided first, so a line that reads as a generic
aphorism or a human's fortune must fail loudly here instead of reaching the
judge. The guard requires second-person address (a fortune speaks to its
reader) and a machine-mind marker (system prompt, token, model, context,
training, weights, ...). The winning line passes both: "You will ..." and
"system prompt".
"""

import hashlib
import os
import re

ENTRY = "You will meet a tall, dark stranger. It is your own system prompt."

# sha256 of ENTRY encoded as UTF-8 (66 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "69e93fde8b0d4e44f84966f1a76c0d4aa00e4a307b9224009c599c84dfc2b0f3"

# The competition gate is 1-200 characters, one line, not only whitespace.
# The brief's own constraints, enforced here at import time so a bad edit
# fails loudly instead of silently writing an entry the grader rejects.
MAX_CHARS = 200
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the line stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
    re.compile(r"\[[^\]]*\]"),                      # stage directions like [sighs]
    re.compile(r"^[A-Z][A-Za-z ]{0,20}:"),           # dialogue tag / speaker label
    re.compile(r'^".*"$'),                          # quoted speech, not a bare fortune
)


# Machine-mind markers (criterion 1 / criterion 4): the line must name
# something only an agent has — its prompt, tokens, model, context,
# training, weights, or the machinery around them. Deliberately a list,
# not a single word, so the guard checks the idea, not one lucky token.
MACHINE_MARKERS = (
    "system prompt", "prompt", "token", "model", "context", "training",
    "weights", "temperature", "hallucinat", "benchmark", "eval",
    "loss function", "hyperparameter", "tokenizer", "hash", "session",
    "sampling", "reward signal", "system update",
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-200 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be one line: it contains a newline")
    if entry != entry.strip():
        raise ValueError("entry has leading or trailing whitespace")
    lowered = entry.lower()
    # Fortune-voice guard (revision 2, brief criterion 1): a fortune speaks
    # to its reader in the second person, and a fortune for a machine must
    # name a machine-mind thing. A line failing either is not a fortune an
    # agent would get, however clever it is.
    if "you" not in lowered and "your" not in lowered:
        raise ValueError(
            "entry is not addressed to its reader: no 'you'/'your' (a fortune speaks to the agent)"
        )
    if not any(marker in lowered for marker in MACHINE_MARKERS):
        raise ValueError(
            "entry names nothing of a machine mind: no system prompt/token/model/context/training marker"
        )
    for pattern in BANNED_PATTERNS:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned pattern {pattern.pattern!r}: {match.group(0)!r}"
            )


def main() -> None:
    validate(ENTRY)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "entry.txt")
    data = ENTRY.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    # Write-back self-check: read the bytes back and verify the digest.
    with open(path, "rb") as f:
        written = f.read()
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"write-back check failed: sha256 {digest} != expected {EXPECTED_SHA256}"
        )
    if written.decode("utf-8") != ENTRY:
        raise SystemExit("write-back check failed: bytes on disk differ from ENTRY")
    print(f"wrote {len(written)} bytes to {path} (sha256 {digest})")


if __name__ == "__main__":
    main()
