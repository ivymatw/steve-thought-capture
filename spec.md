# Telegram-first, local-ASR, Steve-aware thought capture and routing system

Date: 2026-04-17

## Goal

Create a Telegram-first voice input system for Steve that turns spoken thoughts into usable work without breaking conversational flow.

The system should let Steve speak naturally in Telegram, transcribe locally, preserve conversational speed, and route the resulting thought into the right destination: reply, note, task, project artifact, or knowledge capture.

## Core thesis

This is not a "voice typing" tool.

It is a thought capture and routing layer for Steve's real working style:
- voice-first instead of typing-first
- local-first instead of cloud-first when possible
- low-friction instead of review-heavy
- Steve-aware instead of generic assistant behavior

The system's job is not merely to convert audio to text.
Its job is to capture intent, preserve momentum, and place the output into the correct downstream workflow.

## Primary user

Steve Ma

Relevant traits:
- thinks out loud in high-context, cross-domain bursts
- frequently code-switches between Chinese and English
- uses AI/product/company/model names that generic ASR often mishears
- dislikes transcript review as a default interaction because it interrupts the conversation
- accepts occasional clarification turns from the LLM when ambiguity materially matters

## Product position

This system is a Steve-aware cognitive input layer.

It sits between:
- Telegram voice messages as the capture interface
- local ASR as the transcription engine
- Hermes/Max as the interpretation, routing, and response layer

## Non-goals

Not in v1:
- full duplex realtime voice assistant
- wake word
- always-on listening
- mandatory transcript review before send
- training a custom speech model from scratch
- polished mobile app beyond Telegram
- perfect zero-error transcription

## User experience

### Default flow

1. Steve records and sends a Telegram voice message.
2. Hermes receives the audio file and keeps it local.
3. Local ASR transcribes the audio.
4. Transcript is normalized for Steve's language habits:
   - mixed Chinese/English preserved
   - Taiwan Traditional Chinese preferred
   - known proper nouns corrected when confidence is high
5. Hermes interprets the message and chooses the right action.
6. Hermes responds naturally in the same Telegram thread.

### Important UX principle

No transcript review by default.

If the system is uncertain about a detail that changes meaning materially, Hermes should ask a short clarification question in conversation.
That is preferable to forcing review on every utterance.

## Routing model

Each incoming spoken thought should be classified into one or more of these buckets:

1. Conversational reply
- Steve is talking to Max and expects an answer.

2. Note capture
- Steve is thinking aloud and wants the thought preserved.
- Usually routes to Obsidian Conversations or another note target.

3. Task/action capture
- Steve is issuing an action, reminder, follow-up, or delegated work item.

4. Project artifact input
- Steve is dictating content for an existing project spec, plan, memo, or draft.

5. Knowledge capture
- Steve is stating an insight, pattern, or conceptual distinction worth turning into candidate knowledge.

Routing can be explicit or inferred.
If confidence is low, Hermes should ask a clarification question rather than silently misroute.

## Steve-aware layer

The differentiator is not ASR alone. It is the Steve-aware interpretation layer.

That layer should gradually accumulate:
- proper nouns and preferred spellings
- recurring project names
- model/tool vocabulary
- preferred Chinese/Taiwan wording
- common ASR mistakes and their corrections
- routing preferences by utterance type

This should be implemented first as lightweight, editable artifacts:
- personal lexicon
- correction map
- normalization rules
- routing heuristics

Not as full model fine-tuning in v1.

## Architecture

### Input layer
- Telegram voice message
- Hermes gateway receives message and stores local audio path

### Transcription layer
- local whisper.cpp-based transcription
- no OpenAI cloud dependency in the default path
- support Telegram audio formats directly or via local conversion when needed

### Normalization layer
- whitespace cleanup
- Simplified -> Traditional Chinese conversion
- proper noun normalization
- Steve-specific lexical corrections

### Interpretation layer
- determine user intent
- decide whether to answer, ask a clarification question, store, route, or act

### Routing layer
- send to Telegram reply
- append to note/project artifact
- create task/reminder/job
- emit candidate knowledge capture

### Learning layer
- observe recurring misrecognitions
- accumulate corrections over time
- improve lexicon and normalization rules without adding friction to the default flow

## Success criteria

The system is successful when all are true:
- Steve can use it from Telegram on desktop or phone
- default interaction requires no terminal and no review step
- local ASR is the normal path
- mixed Chinese/English is usable in practice
- Taiwan Traditional Chinese is the default output form
- proper noun accuracy improves over time
- Hermes asks clarifying questions only when needed
- spoken input can be routed into conversation, notes, tasks, and project artifacts
- the system feels faster than typing for real daily use

## Failure modes to avoid

- forcing transcript confirmation every time
- routing every voice message only as chat when some are really notes/tasks
- overfitting on ASR accuracy while ignoring routing and downstream usefulness
- introducing cloud dependence into the default path
- creating a system that works only on desktop but not from Telegram on phone

## v1 implementation priority

1. Telegram voice -> local audio path -> local ASR
2. remove mandatory review flow
3. add normalization for mixed language and Traditional Chinese
4. add Steve lexicon and correction map
5. add intent/routing classifier
6. support note/task/project routing
7. add passive correction learning

## Product statement

This project is best understood as:

A Telegram-first, local-ASR, Steve-aware thought capture and routing system that turns spoken ideas into useful conversational, operational, and knowledge outputs without interrupting Steve's flow.
