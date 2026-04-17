# ASR hard-set comparison — Breeze whisper.cpp q5_k vs whisper.cpp large-v3-turbo — 2026-04-17

## Scope

This is the first direct hard-set comparison between:

1. current live baseline
- `whisper.cpp large-v3-turbo`

2. challenger
- `Breeze-ASR-25 whisper.cpp q5_k`

Both were run on the same 10 real Telegram clips selected from the recent 15-sample pool.

## Why these 10 clips

This is not a random slice.

The hard set intentionally prioritizes clips containing:
- English workflow terms
- product / project / repo names
- agent names
- code-switching
- places where the old baseline is already known to drift

Manifest:
- `outputs/asr-bakeoff/hardset-manifest-10.jsonl`

Compared outputs:
- `outputs/asr-bakeoff/baseline-large-v3-turbo-hardset-10.jsonl`
- `outputs/asr-bakeoff/breeze-whispercpp-q5k-hardset-10.jsonl`

## Latency

### whisper.cpp large-v3-turbo
- average: 1.438s
- median: 1.288s
- min: 1.215s
- max: 1.905s

### Breeze whisper.cpp q5_k
- average: 2.367s
- median: 2.212s
- min: 1.893s
- max: 3.211s

## Speed judgment

Baseline is still faster.

On this hard set, Breeze q5_k is roughly:
- about 0.93s slower on average
- about 1.65x the latency of large-v3-turbo

That is a real cost, but much smaller than the PyTorch CPU penalty.

## Quality judgment

Conclusion first:
- Breeze wins the hard set on quality
- baseline wins on speed
- Breeze is now credible enough to be promoted from audit-only candidate to primary local challenger

## Per-sample verdicts

### 1. `audio_41e20cb531c7`
Baseline:
- `比较好的模型你有Candidate吗?现在这个GPT5.4可以吗?还是有什么建议?`

Breeze:
- `比較好的模型你有 candidate 嗎現在這個 gpt 5.4 可以嗎還是有什麼建議`

Verdict:
- Breeze win
- better Traditional Chinese style
- more natural code-switch handling
- cleaner preservation of `candidate` and `gpt 5.4`

### 2. `audio_078d2addf907`
Baseline:
- simplified-Chinese style, `text档`, `loop` kept but overall less Taiwan-aligned

Breeze:
- Traditional Chinese throughout
- `text` and `loop` preserved cleanly

Verdict:
- Breeze win

### 3. `audio_bc65e9dd8cfe`
Baseline:
- `像现在这样我从Telegram传给你的那个语音的档案你都有留着吗?`

Breeze:
- `像現在這樣我從 telegram 傳給你的那個語音的檔案你都有留著嗎`

Verdict:
- Breeze win
- same meaning, better output style for Steve

### 4. `audio_ef7dc861f3e2`
Baseline:
- `现在中阴夹杂...`

Breeze:
- `現在中英夾雜...`

Verdict:
- decisive Breeze win
- this is the single most important hard-set result
- semantic repair matters more than punctuation or speed

### 5. `audio_acf132e5d373`
Baseline:
- `...这个部分有implement吗?`

Breeze:
- `...這個部分有 implement 嗎`

Verdict:
- Breeze win
- same content, better Traditional Chinese and code-switch rendering

### 6. `audio_108114165639`
Baseline:
- `Hermes Agent本地改動不用Push上去沒關係這樣我了解了`

Breeze:
- `Hermes agent 本地改動不用 push 上去沒關係這樣我了解了`

Verdict:
- slight Breeze win
- meaning is the same
- Breeze separates the English terms more naturally inside the sentence

### 7. `audio_1b95c614876f`
Baseline:
- `修改真正Hermis Agent的部分`

Breeze:
- `修改真正 Hermes agent 的部分`

Verdict:
- Breeze win
- baseline keeps the `Hermis` spelling drift
- Breeze repairs `Hermes`

### 8. `audio_dd8f1fc944e7`
Baseline:
- `本地的Hermis Ripple没有push有什么特别的原因吗?`

Breeze:
- `本地的 Hermes ripple mail push 有什麼特別的原因嗎`

Verdict:
- baseline win
- Breeze repaired `Hermes` but hallucinated `mail`
- this is the clearest current Breeze regression

### 9. `audio_e442942cc244`
Baseline:
- `...另外一个agent看文件就能照着follow`

Breeze:
- `...另外一個 agent 看文件就能照著 follow`

Verdict:
- Breeze win
- much better mixed-language formatting and Traditional Chinese style

### 10. `audio_e9a56bda1384`
Baseline:
- simplified-Chinese style, `push`, `github`, `agent` all crammed into a flatter output

Breeze:
- Traditional Chinese throughout
- English terms preserved naturally in-context

Verdict:
- Breeze win

## Scorecard

Quality score on this hard set:
- Breeze wins: 9
- baseline wins: 1
- ties: 0

Speed score:
- baseline wins: 10/10

## What this means

This hard set resolves the main strategic question.

### Before this run
The conservative position was:
- Breeze is promising
- but maybe only good enough for second-pass audit

### After this run
The stronger position is:
- Breeze q5_k is materially better than the current live large-v3-turbo baseline on Steve's real mixed-language speech
- the quality gain is not subtle
- the latency penalty is real but not prohibitive

In plain terms:
- large-v3-turbo is faster
- Breeze is more Steve-aligned

## Decision recommendation

### Recommended default direction
Promote `Breeze-ASR-25 whisper.cpp q5_k` to the lead candidate for the local production path.

### But do not switch blindly yet
Before final production cutover, do one more targeted pass:
- collect additional hard clips where repo / agent / product names appear
- specifically probe the `mail push` regression pattern
- verify whether prompt terms or decoding flags can suppress that hallucination

## Operational recommendation right now

If forced to choose based on current evidence:
- choose `Breeze-ASR-25 whisper.cpp q5_k` for better transcript quality
- keep `large-v3-turbo` available as rollback / speed-first fallback

## Bottom line

This was the question that mattered:
- does Breeze still win when compared directly against the current live whisper.cpp baseline on the hardest real clips?

Answer:
- yes
- clearly on quality
- with a manageable latency penalty
- but with one real hallucination that must be watched
