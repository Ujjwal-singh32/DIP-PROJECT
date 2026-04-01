# """
# memory_manager.py
# ─────────────────
# Manages multi-turn conversation memory.

# Two modes (configured via MEMORY_TYPE env var):
#   • 'buffer'  – ConversationBufferMemory: stores full raw history.
#   • 'summary' – ConversationSummaryMemory: summarises older turns to save tokens.

# The manager exposes a simple list-of-dicts interface that the rest of the
# pipeline can use without depending on LangChain internals.
# """

# from typing import List, Literal

# from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
# from langchain_google_genai import ChatGoogleGenerativeAI

# from backend.config import settings
# from utils.logger import logger


# class MemoryManager:
#     """
#     Conversation memory abstraction.

#     Usage:
#         memory = MemoryManager()
#         history = memory.get_history()           # before calling LLM
#         memory.add_turn(user_msg, assistant_msg) # after LLM responds
#         memory.clear()                           # reset session
#     """

#     def __init__(
#         self,
#         memory_type: Literal["buffer", "summary"] = settings.memory_type,
#     ) -> None:
#         self.memory_type = memory_type
#         self._history: List[dict] = []   # simple list for LLM client
#         self._lc_memory = self._init_lc_memory(memory_type)
#         logger.info(f"MemoryManager initialised | type={memory_type}")

#     # ── Internal setup ────────────────────────────────────────────────────

#     @staticmethod
#     def _init_lc_memory(memory_type: str):
#         """Initialise the appropriate LangChain memory backend."""
#         if memory_type == "summary":
#             # SummaryMemory needs an LLM to summarise history
#             llm = ChatGoogleGenerativeAI(
#                 model=settings.gemini_model,
#                 google_api_key=settings.gemini_api_key,
#                 temperature=0,
#             )
#             return ConversationSummaryMemory(llm=llm, return_messages=True)
#         else:
#             return ConversationBufferMemory(return_messages=True)

#     # ── Public API ────────────────────────────────────────────────────────

#     def get_history(self) -> List[dict]:
#         """
#         Return conversation history as a list of dicts:
#             [{"role": "user"|"assistant", "content": "…"}, …]
#         """
#         return list(self._history)

#     def add_turn(self, user_message: str, assistant_message: str) -> None:
#         """
#         Record a complete conversation turn.

#         Args:
#             user_message:      What the user said.
#             assistant_message: What the assistant replied.
#         """
#         self._history.append({"role": "user", "content": user_message})
#         self._history.append({"role": "assistant", "content": assistant_message})

#         # Also update LangChain memory (for summary mode tracking)
#         self._lc_memory.save_context(
#             {"input": user_message},
#             {"output": assistant_message},
#         )

#         # Token budget: trim oldest turns if history is very long
#         self._trim_history()

#         logger.debug(f"Turn recorded | history_length={len(self._history)}")

#     def clear(self) -> None:
#         """Reset conversation memory."""
#         self._history.clear()
#         self._lc_memory.clear()
#         logger.info("Conversation memory cleared")

#     def get_summary(self) -> str:
#         """
#         Return a text summary of the conversation (available in summary mode).
#         In buffer mode, returns a concatenated transcript.
#         """
#         if self.memory_type == "summary":
#             summary = self._lc_memory.load_memory_variables({}).get("history", "")
#             return str(summary)
#         # Buffer mode: build a compact transcript
#         lines = []
#         for turn in self._history:
#             role = "User" if turn["role"] == "user" else "LexAI"
#             lines.append(f"{role}: {turn['content'][:200]}")
#         return "\n".join(lines)

#     # ── Token budget management ───────────────────────────────────────────

#     def _trim_history(self) -> None:
#         """
#         Naively trim history when it grows too large.
#         Removes oldest pairs (2 items = 1 turn) until within budget.
#         """
#         # Rough char budget; 1 token ≈ 4 chars
#         char_budget = settings.max_history_tokens * 4
#         total_chars = sum(len(t["content"]) for t in self._history)

#         while total_chars > char_budget and len(self._history) >= 2:
#             removed_user = self._history.pop(0)
#             removed_asst = self._history.pop(0)
#             total_chars -= len(removed_user["content"]) + len(removed_asst["content"])

"""
memory_manager.py
─────────────────
Manages multi-turn conversation memory.

Two modes (configured via MEMORY_TYPE env var):
  • 'buffer'  – ConversationBufferMemory: stores full raw history.
  • 'summary' – ConversationSummaryMemory: summarises older turns to save tokens.

The manager exposes a simple list-of-dicts interface that the rest of the
pipeline can use without depending on LangChain internals.
"""

from typing import List, Literal

from langchain_classic.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_cohere import ChatCohere

from backend.config import settings
from utils.logger import logger


class MemoryManager:
    """
    Conversation memory abstraction.

    Usage:
        memory = MemoryManager()
        history = memory.get_history()           # before calling LLM
        memory.add_turn(user_msg, assistant_msg) # after LLM responds
        memory.clear()                           # reset session
    """

    def __init__(
        self,
        memory_type: Literal["buffer", "summary"] = settings.memory_type,
    ) -> None:
        self.memory_type = memory_type
        self._history: List[dict] = []   # simple list for LLM client
        self._lc_memory = self._init_lc_memory(memory_type)
        logger.info(f"MemoryManager initialised | type={memory_type}")

    # ── Internal setup ────────────────────────────────────────────────────

    @staticmethod
    def _init_lc_memory(memory_type: str):
        """Initialise the appropriate LangChain memory backend."""
        if memory_type == "summary":
            # SummaryMemory needs an LLM to summarise history
            llm = ChatCohere(
                cohere_api_key=settings.cohere_api_key,
                model=settings.cohere_model,
                temperature=0,
            )
            return ConversationSummaryMemory(llm=llm, return_messages=True)
        else:
            return ConversationBufferMemory(return_messages=True)

    # ── Public API ────────────────────────────────────────────────────────

    def get_history(self) -> List[dict]:
        """
        Return conversation history as a list of dicts:
            [{"role": "user"|"assistant", "content": "…"}, …]
        """
        return list(self._history)

    def add_turn(self, user_message: str, assistant_message: str) -> None:
        """
        Record a complete conversation turn.

        Args:
            user_message:      What the user said.
            assistant_message: What the assistant replied.
        """
        self._history.append({"role": "user", "content": user_message})
        self._history.append({"role": "assistant", "content": assistant_message})

        # Also update LangChain memory (for summary mode tracking)
        self._lc_memory.save_context(
            {"input": user_message},
            {"output": assistant_message},
        )

        # Token budget: trim oldest turns if history is very long
        self._trim_history()

        logger.debug(f"Turn recorded | history_length={len(self._history)}")

    def clear(self) -> None:
        """Reset conversation memory."""
        self._history.clear()
        self._lc_memory.clear()
        logger.info("Conversation memory cleared")

    def get_summary(self) -> str:
        """
        Return a text summary of the conversation (available in summary mode).
        In buffer mode, returns a concatenated transcript.
        """
        if self.memory_type == "summary":
            summary = self._lc_memory.load_memory_variables({}).get("history", "")
            return str(summary)
        # Buffer mode: build a compact transcript
        lines = []
        for turn in self._history:
            role = "User" if turn["role"] == "user" else "LexAI"
            lines.append(f"{role}: {turn['content'][:200]}")
        return "\n".join(lines)

    # ── Token budget management ───────────────────────────────────────────

    def _trim_history(self) -> None:
        """
        Naively trim history when it grows too large.
        Removes oldest pairs (2 items = 1 turn) until within budget.
        """
        # Rough char budget; 1 token ≈ 4 chars
        char_budget = settings.max_history_tokens * 4
        total_chars = sum(len(t["content"]) for t in self._history)

        while total_chars > char_budget and len(self._history) >= 2:
            removed_user = self._history.pop(0)
            removed_asst = self._history.pop(0)
            total_chars -= len(removed_user["content"]) + len(removed_asst["content"])