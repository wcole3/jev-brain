# Draft upstream PR: logprob_token_ids under speculative decoding (V2 runner)

**Status:** draft, not posted. Hold until the DS-004 MTP work is complete (owner,
2026-10-06). Before posting: rebase onto vLLM `main`, add the unit test below, rerun the
e2e numbers on the rebased build, and get the owner's ok.

**Target:** `vllm-project/vllm`, `main`. The gap is still in v0.31.0
(`vllm/v1/worker/gpu/model_runner.py:1625`, "Rejection sampler does not return logprob
token ids"). Related: #42592 (open; V1 runner crash with `/generative_scoring`), #42936
(closed; V1 fix, does not touch the V2 runner).

---

## Title

[Bugfix][Spec Decode] Return logprob_token_ids from the V2 rejection sampler

## Summary

With speculative decoding on (MTP, EAGLE), a step where any request has draft tokens goes
through `RejectionSampler` instead of `Sampler`. The rejection sampler sizes logprobs from
`sampling_states.max_num_logprobs` only and calls `compute_topk_scores` without the
`logprob_token_ids` state. A request that sets `logprob_token_ids` (and so has
`logprobs=None`) gets no logprobs tensor when co-batched with a drafting request:

- if no request in the batch asked for top-k logprobs, the request's logprobs list is
  empty and `/v1/completions` raises `IndexError: list index out of range` in
  `_create_completion_logprobs` (HTTP 500);
- if another request asked for top-k, the request gets the batch's top-k tokens instead
  of the ids it asked for.

The request itself never drafts (for example `max_tokens=1` prompt scoring), so this
depends only on what it is co-batched with. Under steady chat load every such request
fails.

## Fix

Make the rejection sampler use the same logprobs path as `Sampler` (`sample/sampler.py`):

- size logprobs with `Sampler.get_logprobs_dims(idx_mapping_np)`, which returns
  `(num_logprobs, max_per_req_token_ids)`;
- pass `logprob_token_ids_state`, the chunk's slice of `input_batch.expanded_idx_mapping`
  and `max_per_req_token_ids` to `compute_topk_scores`.

The dims are computed once per batch, so every chunk in `_verify_in_chunks` has the same
column count and `LogprobsTensors.cat` still works. The `expanded_idx_mapping[lo:hi]` slice
is the same one `_verify` already uses, so it lines up row for row with `logits[lo:hi]`.
Draft positions of a request that sets `logprob_token_ids` get those ids too, as on the
non-speculative path.

`model_runner.py`: the TP gather no longer turns off token ids for rejection-sampled
batches. This leaves `get_logprobs_dims(..., include_token_ids=...)` with no caller that
passes it; the parameter is removed.

No new kernels or math: `compute_topk_scores` and `_fill_logprob_token_ids_kernel` are the
code `Sampler` already runs.

## Diff (against v0.30.0; rebase before posting)

`vllm/v1/worker/gpu/spec_decode/rejection_sampler.py`: see
`docker/spike/vllm/rejection_sampler.upstream.diff` (about 15 lines). Core change:

```diff
-        max_num_logprobs = self.sampler.sampling_states.max_num_logprobs(
-            input_batch.idx_mapping_np
-        )
+        logprobs_dims = self.sampler.get_logprobs_dims(input_batch.idx_mapping_np)
 ...
         return compute_topk_scores(
             logits,
-            max_num_logprobs,
+            num_logprobs,
             flat_sampled,
             cu_num_generated_tokens,
+            logprob_token_ids_state=self.sampler.logprob_token_ids_state,
+            expanded_idx_mapping=expanded_idx_mapping,
+            max_per_req_token_ids=max_per_req_token_ids,
```

`vllm/v1/worker/gpu/model_runner.py`: see `docker/spike/vllm/model_runner.diff`.
`vllm/v1/worker/gpu/sample/sampler.py`: drop the `include_token_ids` parameter (to do).

## Reproduction

Qwen3.6-27B, bf16, one GPU,
`--speculative-config '{"method":"mtp","num_speculative_tokens":3}'`.

1. Keep 4 streaming chat completions running (`max_tokens` 512).
2. Send prompt-only `/v1/completions` requests with `max_tokens=1`, `temperature=0`,
   `logprob_token_ids=[...]`.

Stock v0.30.0: 1,682 of 1,682 requests return HTTP 500 (`IndexError` in
`serving.py:673`). With the fix: 0 errors.

## Test plan

- **Unit (to write):** `tests/v1/worker/gpu/spec_decode/` rejection sampler with a batch
  of one drafting request (top-k or no logprobs) and one request with
  `logprob_token_ids` and no drafts; assert the second request's returned ids and values
  equal what `Sampler` returns for the same logits. Cover the chunked path (forced small
  `max_chunk_logits`) and a drafting request that itself sets `logprob_token_ids`.
- **E2E (done on v0.30.0):** 1,682 scoring requests, each run idle and under the chat load
  above. Results:

  | run | error rows | max \|Δp\| vs the same load without spec decode |
  |---|---|---|
  | stock, spec decode on | 1,682 | — |
  | patched, spec decode on, idle | 0 | 0.077 |
  | patched, spec decode on, chat load | 0 | 0.078 |

  These drifts are within restart noise: restarting the stock server without spec decode
  moves label probabilities by up to 0.079 against the first run. Within one server
  instance, results repeat bit for bit. No argmax flip had a top-two gap above 0.10.

---

## Open before posting

- [ ] Rebase onto `main`; check `rejection_sampler.py` / `model_runner.py` have not moved.
- [ ] Remove `include_token_ids` from `Sampler.get_logprobs_dims`.
- [ ] Write the unit test above; run `pytest tests/v1/worker/gpu`.
- [ ] Rerun the e2e on the rebased build.
- [ ] Search open PRs/issues again for duplicates.
- [ ] Owner's ok to post.
