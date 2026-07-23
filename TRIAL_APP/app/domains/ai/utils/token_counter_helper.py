import tiktoken

_encoding = tiktoken.get_encoding("cl100k_base")

def token_counter(messages) -> int:
    return sum(len(_encoding.encode(str(m.content))) for m in messages)