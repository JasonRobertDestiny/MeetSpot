# Code Review Notes

## Fixed Issues
- **Accurate token accounting for image-enabled chats (`app/llm.py`)**  
  The previous implementation of `LLM.ask_with_images` only updated prompt token usage for non-streaming requests and skipped completion tokens entirely. Streaming calls also incremented prompt tokens *before* the API call and never tracked completions, so quota tracking was consistently off. The method now records both prompt and completion tokens for non-streaming calls and estimates completion usage for streaming responses before updating the counters.

## Additional Observations
- **Streaming quota bookkeeping in `LLM.ask`**  
  The streaming branch calls `update_token_count` before the request finishes. If the request fails, the prompt tokens remain counted against the cumulative budget. Consider deferring the update until after the stream completes (mirroring the image-enabled path) to keep usage metrics accurate when retries occur.
