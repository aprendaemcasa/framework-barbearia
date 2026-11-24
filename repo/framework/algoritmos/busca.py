"""
Métodos de busca.

  * busca_linear   O(n)      - funciona em qualquer lista (referência/baseline)
  * busca_binaria  O(log n)  - exige lista ORDENADA pela mesma chave
  * limite_inferior / limite_superior - variações da busca binária que
    devolvem posições; com elas obtém-se TODAS as ocorrências de uma
    chave repetida ou todos os itens de um intervalo em O(log n + k).
"""


def _ident(x):
    return x


def busca_linear(dados, alvo, chave=_ident):
    """Devolve o índice do primeiro item com chave == alvo, ou -1."""
    for i, item in enumerate(dados):
        if chave(item) == alvo:
            return i
    return -1


def limite_inferior(dados, alvo, chave=_ident):
    """Primeira posição i tal que chave(dados[i]) >= alvo."""
    ini, fim = 0, len(dados)
    while ini < fim:
        meio = (ini + fim) // 2
        if chave(dados[meio]) < alvo:
            ini = meio + 1
        else:
            fim = meio
    return ini


def limite_superior(dados, alvo, chave=_ident):
    """Primeira posição i tal que chave(dados[i]) > alvo."""
    ini, fim = 0, len(dados)
    while ini < fim:
        meio = (ini + fim) // 2
        if chave(dados[meio]) <= alvo:
            ini = meio + 1
        else:
            fim = meio
    return ini


def busca_binaria(dados, alvo, chave=_ident):
    """Índice de um item com chave == alvo em lista ordenada, ou -1."""
    i = limite_inferior(dados, alvo, chave)
    if i < len(dados) and chave(dados[i]) == alvo:
        return i
    return -1


def busca_binaria_todos(dados, alvo, chave=_ident):
    """Todos os itens com chave == alvo (lista ordenada)."""
    return dados[limite_inferior(dados, alvo, chave):limite_superior(dados, alvo, chave)]


def busca_binaria_intervalo(dados, inicio, fim, chave=_ident):
    """Itens com inicio <= chave <= fim (lista ordenada)."""
    return dados[limite_inferior(dados, inicio, chave):limite_superior(dados, fim, chave)]
