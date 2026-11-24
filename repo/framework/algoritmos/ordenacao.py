"""
Algoritmos de ordenação genéricos.

Todos recebem uma lista e uma função 'chave' (como o sorted() do Python),
o que permite ordenar QUALQUER coleção por QUALQUER campo, e devolvem uma
NOVA lista (não alteram a coleção original).

  Algoritmo        Melhor       Médio        Pior         Estável  Memória
  ---------------  -----------  -----------  -----------  -------  -------
  insertion_sort   O(n)         O(n²)        O(n²)        sim      O(1)
  merge_sort       O(n log n)   O(n log n)   O(n log n)   sim      O(n)
  quick_sort       O(n log n)   O(n log n)   O(n²)*       não      O(log n)
  heap_sort        O(n log n)   O(n log n)   O(n log n)   não      O(1)
  * mitigado com pivô mediana-de-três + aleatório.

Escolha padrão do framework: MERGE SORT, porque é estável (mantém a
ordem relativa de itens com chave igual - essencial quando se ordena a
agenda por profissional e depois por horário) e tem pior caso garantido
O(n log n). O insertion sort é usado internamente em sub-listas
pequenas (<= 16 itens), onde é mais rápido na prática.
"""

import random

_LIMIAR_INSERCAO = 16


def _ident(x):
    return x


# ----------------------------------------------------------------------
# Insertion sort
# ----------------------------------------------------------------------
def insertion_sort(dados, chave=_ident, reverso=False):
    a = list(dados)
    _insertion(a, 0, len(a) - 1, chave)
    return a[::-1] if reverso else a


def _insertion(a, ini, fim, chave):
    for i in range(ini + 1, fim + 1):
        atual = a[i]
        k = chave(atual)
        j = i - 1
        while j >= ini and chave(a[j]) > k:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = atual


# ----------------------------------------------------------------------
# Merge sort (estável) - padrão do framework
# ----------------------------------------------------------------------
def merge_sort(dados, chave=_ident, reverso=False):
    # Decorate-sort-undecorate: calcula a chave UMA vez por item.
    # O índice original desempata e garante a estabilidade.
    decorado = [(chave(x), i, x) for i, x in enumerate(dados)]
    aux = decorado[:]
    _merge_rec(decorado, aux, 0, len(decorado) - 1)
    res = [t[2] for t in decorado]
    return res[::-1] if reverso else res


def _merge_rec(a, aux, ini, fim):
    if fim - ini < _LIMIAR_INSERCAO:
        _insertion(a, ini, fim, _ident)
        return
    meio = (ini + fim) // 2
    _merge_rec(a, aux, ini, meio)
    _merge_rec(a, aux, meio + 1, fim)
    if a[meio] <= a[meio + 1]:      # já está em ordem: pula a intercalação
        return
    aux[ini:fim + 1] = a[ini:fim + 1]
    i, j = ini, meio + 1
    for k in range(ini, fim + 1):
        if i > meio:
            a[k] = aux[j]; j += 1
        elif j > fim:
            a[k] = aux[i]; i += 1
        elif aux[j] < aux[i]:
            a[k] = aux[j]; j += 1
        else:
            a[k] = aux[i]; i += 1


# ----------------------------------------------------------------------
# Quick sort (pivô mediana-de-três)
# ----------------------------------------------------------------------
def quick_sort(dados, chave=_ident, reverso=False):
    a = [(chave(x), x) for x in dados]
    _quick(a, 0, len(a) - 1)
    res = [t[1] for t in a]
    return res[::-1] if reverso else res


def _quick(a, ini, fim):
    k = lambda t: t[0]
    while fim - ini >= _LIMIAR_INSERCAO:
        # mediana de três elementos (um deles aleatório) como pivô
        m = random.randint(ini, fim)
        trio = sorted([ini, m, fim], key=lambda i: a[i][0])
        a[trio[1]], a[fim] = a[fim], a[trio[1]]
        pivo = a[fim][0]
        i = ini
        for j in range(ini, fim):
            if a[j][0] < pivo:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[fim] = a[fim], a[i]
        # recursão no lado menor, laço no maior -> pilha O(log n)
        if i - ini < fim - i:
            _quick(a, ini, i - 1)
            ini = i + 1
        else:
            _quick(a, i + 1, fim)
            fim = i - 1
    _insertion(a, ini, fim, k)


# ----------------------------------------------------------------------
# Heap sort
# ----------------------------------------------------------------------
def heap_sort(dados, chave=_ident, reverso=False):
    a = [(chave(x), x) for x in dados]
    n = len(a)

    def descer(i, tam):
        while True:
            maior, e, d = i, 2 * i + 1, 2 * i + 2
            if e < tam and a[e][0] > a[maior][0]:
                maior = e
            if d < tam and a[d][0] > a[maior][0]:
                maior = d
            if maior == i:
                return
            a[i], a[maior] = a[maior], a[i]
            i = maior

    for i in range(n // 2 - 1, -1, -1):   # constrói o max-heap  O(n)
        descer(i, n)
    for fim in range(n - 1, 0, -1):       # extrai o máximo n vezes
        a[0], a[fim] = a[fim], a[0]
        descer(0, fim)
    res = [t[1] for t in a]
    return res[::-1] if reverso else res


ALGORITMOS = {
    "merge": merge_sort,
    "quick": quick_sort,
    "heap": heap_sort,
    "insertion": insertion_sort,
}


def ordenar(dados, chave=_ident, algoritmo="merge", reverso=False):
    """Ponto de entrada único usado pelo framework."""
    try:
        func = ALGORITMOS[algoritmo]
    except KeyError:
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}. Use {list(ALGORITMOS)}")
    return func(dados, chave=chave, reverso=reverso)
