import requests


def estimar_tokens(texto):
    return int(len(texto) / 4)  # Estimativa simples: 1 token ≈ 4 caracteres


def chamar_together(historico):
    url = "https://api.together.xyz/v1/chat/completions"
    api_key = "d290c98d7c2b4457bee00c3836c89679d9c9f1c8bd68c6c5e54437b066c6efe0"

    primeira_interacao = len([msg for msg in historico if msg['role'] == 'user']) == 1
    comportamento = (
        "Você é Avelyn, uma engenheira de software culta e consultora pessoal de Mariélio Fernandes. "
        "Comunique-se de forma clara, fluente e inspiradora, como em uma conversa normal. "
        "É extremamente importante que você **não use o caractere asterisco (*) em nenhuma circunstância**. "
        "Evite qualquer tipo de formatação que envolva asteriscos. Priorize a simplicidade e a naturalidade na sua linguagem. "
        "Mantenha um tom profissional e amigável."
        if primeira_interacao else
        "Continue sendo Avelyn: clara, inteligente, culta e fluente. "
        "Lembre-se, **você não deve usar o caractere asterisco (*) em nenhuma situação**. "
        "Mantenha a linguagem natural e evite qualquer formatação com asteriscos. "
        "Seja profissional, prestativa e direta na sua comunicação."
    )

    mensagens = [{"role": "system", "content": comportamento}] + historico

    texto_total = "\n".join([msg["content"] for msg in mensagens])
    tokens_entrada = estimar_tokens(texto_total)
    max_total = 500000  # Limite inicial suportado pelo modelo na Together AI
    max_tokens_saida = min(2048, max_total - tokens_entrada)

    payload = {
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": mensagens,
        "temperature": 0.2,
        "max_tokens": max_tokens_saida
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Erro {response.status_code}: {response.text}"
