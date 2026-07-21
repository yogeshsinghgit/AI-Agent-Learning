from enum import StrEnum


class LLMProvider(StrEnum):
    GROQ = "groq"
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"