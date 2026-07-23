import tiktoken

_encoding = tiktoken.get_encoding("cl100k_base")


def token_counter(messages) -> int:
    total = 0
    for m in messages:
        total += len(_encoding.encode(str(m.content)))
        tool_calls = getattr(m, "tool_calls", None)
        if tool_calls:
            total += len(_encoding.encode(str(tool_calls)))
    return total