# Image resend cost, gemma-4-31b

json_ms and payload_mb: building and serializing all rows of a request (median per request).
full_ms vs uuid_ms: row 1 with the image vs uuid only, medians over same-answer requests.
same answer: uuid-only top label equals the full call's and max |dlogprob| <= 0.5 (image really reused).

| requests | uuid accepted | same answer | json_ms | payload_mb | full_ms | uuid_ms |
|---|---|---|---|---|---|---|
| 300 | 300 | 300 | 0.8 | 0.32 | 70 | 59 |
