# LLM Guard Recommendations

## Source
/data/data/com.termux/files/home/projects/_STAGING/dreamos_incoming_unique/dream-os-hardened-v33-1/dream-os-hardened/core/llm_guard.js

## Semantic Signals

- regex: 0
- prompt_validation: 11
- denylist: 0
- allowlist: 0
- token_limits: 2
- sanitization: 36
- timeouts: 0

## Recommended Ports

- Add explicit prompt validation tests.
- Add prompt size guardrails.
- Add sanitization normalization tests.

## Recommendation

- Port semantics only.
- Keep implementation Python-native.
- Prefer small isolated guards with pytest characterization.