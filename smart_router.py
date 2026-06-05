import anthropic

client = anthropic.Anthropic()

# Stable classification instructions — cached once, reused on every call
_CLASSIFY_SYSTEM = [
    {
        "type": "text",
        "text": (
            "Classify the user's task into exactly one category.\n\n"
            "Categories:\n"
            "- 'quick': translation, summarization, rephrasing, simple questions, formatting\n"
            "- 'code': write code, debug, analyze code, explain code, architecture, data analysis\n"
            "- 'deep': research, strategy, philosophy, complex reasoning, long-form thinking\n\n"
            "Reply with ONE word only: quick, code, or deep"
        ),
        "cache_control": {"type": "ephemeral"},
    }
]

MODEL_MAP = {
    "quick": "claude-sonnet-4-6",   # translation, summaries, simple tasks
    "code":  "claude-opus-4-8",     # code, analysis, architecture
    "deep":  "claude-opus-4-8",     # deep thinking, strategy
}


def classify_task(task: str) -> str:
    result = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        system=_CLASSIFY_SYSTEM,
        messages=[{"role": "user", "content": task}],
    )
    return result.content[0].text.strip().lower()


def smart_request(task: str, messages: list | None = None) -> str:
    if messages is None:
        messages = []

    category = classify_task(task)
    model = MODEL_MAP.get(category, "claude-sonnet-4-6")

    print(f"📋 Категория: {category}")
    print(f"🤖 Модель: {model}")
    print("-" * 40)

    history = messages + [{"role": "user", "content": task}]

    # Use adaptive thinking for Opus 4.8; stream to avoid timeout on long outputs
    thinking = {"type": "adaptive"} if model == "claude-opus-4-8" else {"type": "disabled"}

    with client.messages.stream(
        model=model,
        max_tokens=16000,
        thinking=thinking,
        messages=history,
    ) as stream:
        return stream.get_final_message().content[0].text


if __name__ == "__main__":
    tasks = [
        "Переведи на английский: Привет, как дела?",
        "Напиши функцию на Python для парсинга JSON с обработкой ошибок",
        "Какова долгосрочная стратегия развития AGI и её влияние на общество?",
    ]

    for task in tasks:
        print(f"\n📝 Задача: {task}")
        answer = smart_request(task)
        print(f"✅ Ответ: {answer[:200]}...")
        print("=" * 50)
