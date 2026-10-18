import json
import struct

import numpy as np

from scripts.unused_embeddings import bf16_rows


def test_bf16_rows_roundtrip(tmp_path):
    matrix = np.arange(12, dtype=np.float32).reshape(4, 3) * 0.5 - 1.25
    raw = (matrix.view(np.uint32) >> 16).astype("<u2").tobytes()
    header = json.dumps({"emb": {"dtype": "BF16", "shape": [4, 3], "data_offsets": [0, len(raw)]}}).encode()
    path = tmp_path / "t.safetensors"
    path.write_bytes(struct.pack("<Q", len(header)) + header + raw)
    np.testing.assert_allclose(bf16_rows(path, "emb", [0, 2]), matrix[[0, 2]], rtol=1e-2)
