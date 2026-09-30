"""Pad the shared prefix to a whole prefix-cache block (DS-008): hybrid Qwen reuses cached prefixes only in blocks."""

from dataclasses import dataclass, replace

from gateway.config import Settings

MODES = ("off", "end", "front", "middle")


@dataclass(frozen=True)
class Padding:
    mode: str = "off"  # where the pad goes: end | front | middle (see prompts.pad_site)
    block: int = 0  # the prefix-cache block in tokens; 0 never pads
    always: bool = False  # pad even when it does not pay (fidelity experiments)
    token: int = -1  # the tokenizer's one token for "\n", inserted as an id so nothing merges

    @property
    def enabled(self) -> bool:
        return self.mode != "off" and self.block > 0

    def size(self, prefix_len: int) -> int:
        """Pad tokens that end a prefix of this length on a block boundary."""
        return -prefix_len % self.block

    def pays(self, rows: int, unpadded_len: int, pad: int) -> bool:
        """Every row after the first stops recomputing the unpadded prefix's partial block; the pad is computed once."""
        return self.always or (rows > 1 and (rows - 1) * (unpadded_len % self.block) > pad)


OFF = Padding()


def newline_token(tok) -> int:
    ids = tok.encode("\n", add_special_tokens=False)
    if len(ids) != 1:
        raise ValueError(f'prefix padding needs "\\n" to be one token; this tokenizer makes {ids}')
    return ids[0]


def load_padding(s: Settings, tok) -> Padding:
    """The configured padding. Refuses unknown modes, and a "\\n" that is not one token when padding is on."""
    if s.prefix_pad not in MODES or s.prefix_block < 0:
        raise ValueError(f"PREFIX_PAD must be one of {MODES} and PREFIX_BLOCK >= 0")
    padding = Padding(s.prefix_pad, s.prefix_block, s.prefix_pad_always)
    return replace(padding, token=newline_token(tok)) if padding.enabled else padding
