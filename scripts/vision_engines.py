"""Kit engines for the stock baseline: vllm-vl with thinking off in the chat template (Qwen).

Imports the kit, so it loads only on a box where decision_index is installed.
"""

import functools

from decision_index.vision.engines import VllmVisionChat


class NoThinkVl(VllmVisionChat):
    name = "vllm-vl-nothink"

    def __init__(self, model, **kw):
        super().__init__(model, **kw)
        self.llm.chat = functools.partial(self.llm.chat, chat_template_kwargs={"enable_thinking": False})
