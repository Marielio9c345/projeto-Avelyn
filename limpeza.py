# limpeza.py

def limpar_formatacao(texto: str) -> str:
    """
    Remove caracteres de formatação que atrapalham a leitura por voz.
    """
    return (
        texto.replace("*", "")
             .replace("#", "")
             .replace("▌", "")
             .replace("**", "")
             .replace("__", "")
             .replace("##", "")
             .replace("###", "")
             .replace("```", "")
             .strip()
    )
