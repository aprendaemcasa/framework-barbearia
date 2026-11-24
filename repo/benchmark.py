"""
Experimentos de desempenho do framework.  Execute:  python benchmark.py
Gera resultados/benchmark.json usado na seção de Resultados do relatório.
"""

import json
import os
import platform
import random
import sys
import time

from framework import (ArvoreAVL, TabelaHash, Colecao, merge_sort, quick_sort,
                       heap_sort, insertion_sort, busca_linear, busca_binaria)
from barbearia.modelos import Agendamento

random.seed(2026)
CONSULTAS = 2000


def cronometrar(func, repeticoes=1):
    melhor = float("inf")
    for _ in range(repeticoes):
        t0 = time.perf_counter()
        func()
        melhor = min(melhor, time.perf_counter() - t0)
    return melhor


class BSTSimples:
    """BST SEM balanceamento - apenas para comparação com a AVL."""
    def __init__(self):
        self.raiz = None

    def inserir(self, k):
        novo = [k, None, None]
        if self.raiz is None:
            self.raiz = novo
            return
        no = self.raiz
        while True:
            lado = 1 if k < no[0] else 2
            if no[lado] is None:
                no[lado] = novo
                return
            no = no[lado]

    def altura(self):
        h, fila = 0, [self.raiz] if self.raiz else []
        while fila:
            h += 1
            fila = [f for n in fila for f in (n[1], n[2]) if f]
        return h


def exp_busca_chave():
    """1) Busca por chave única: lista (linear) x AVL x hash."""
    res = []
    for n in (1_000, 10_000, 50_000, 100_000):
        chaves = random.sample(range(n * 10), n)
        lista = list(chaves)
        avl, h = ArvoreAVL(), TabelaHash()
        for k in chaves:
            avl.inserir(k, k)
            h.inserir(k, k)
        alvos = random.choices(chaves, k=CONSULTAS)
        n_lin = 200 if n >= 50_000 else CONSULTAS   # linear é lenta: amostra menor
        t_lin = cronometrar(lambda: [busca_linear(lista, a) for a in alvos[:n_lin]]) / n_lin
        t_avl = cronometrar(lambda: [avl.buscar(a) for a in alvos], 3) / CONSULTAS
        t_h = cronometrar(lambda: [h.buscar(a) for a in alvos], 3) / CONSULTAS
        res.append({"n": n, "linear_us": t_lin * 1e6, "avl_us": t_avl * 1e6,
                    "hash_us": t_h * 1e6, "altura_avl": avl.altura,
                    "fator_carga": round(h.fator_carga, 3), "maior_balde": h.maior_balde})
        print(f"[busca] n={n:>7}  linear={t_lin*1e6:9.2f}us  avl={t_avl*1e6:6.2f}us  hash={t_h*1e6:5.2f}us")
    return res


def exp_altura():
    """2) Altura: BST simples x AVL com inserção em ordem crescente (pior caso)."""
    res = []
    for n in (100, 500, 1_000, 2_000, 5_000):
        bst, avl = BSTSimples(), ArvoreAVL()
        for k in range(n):
            bst.inserir(k)
            avl.inserir(k, k)
        res.append({"n": n, "bst": bst.altura(), "avl": avl.altura})
        print(f"[altura] n={n:>5}  BST={bst.altura():>5}  AVL={avl.altura}")
    return res


def exp_ordenacao():
    """3) Tempo de ordenação (ms) de agendamentos pelo campo 'valor'."""
    res = []
    for n in (1_000, 5_000, 10_000, 50_000, 100_000):
        dados = [(random.random() * 300, i) for i in range(n)]
        k = lambda t: t[0]
        linha = {"n": n}
        for nome, f in (("merge", merge_sort), ("quick", quick_sort), ("heap", heap_sort)):
            linha[nome] = cronometrar(lambda: f(dados, chave=k), 2) * 1e3
        linha["insertion"] = cronometrar(lambda: insertion_sort(dados, chave=k)) * 1e3 if n <= 10_000 else None
        linha["timsort_python"] = cronometrar(lambda: sorted(dados, key=k), 3) * 1e3
        res.append(linha)
        print("[ordena]", {a: (round(b, 2) if isinstance(b, float) else b) for a, b in linha.items()})
    return res


def exp_binaria():
    """4) Busca binária x linear em lista ordenada."""
    res = []
    for n in (1_000, 10_000, 100_000, 1_000_000):
        v = list(range(0, 2 * n, 2))
        alvos = random.choices(v, k=CONSULTAS)
        n_lin = 100 if n >= 100_000 else 1000
        t_lin = cronometrar(lambda: [busca_linear(v, a) for a in alvos[:n_lin]]) / n_lin
        t_bin = cronometrar(lambda: [busca_binaria(v, a) for a in alvos], 3) / CONSULTAS
        res.append({"n": n, "linear_us": t_lin * 1e6, "binaria_us": t_bin * 1e6})
        print(f"[binaria] n={n:>8}  linear={t_lin*1e6:10.2f}us  binaria={t_bin*1e6:5.2f}us")
    return res


def exp_agenda():
    """5) Cenário real: agenda de UM profissional em UM dia, com 100 mil agendamentos."""
    col = Colecao("ag", "id", indices=("chave_agenda", "inicio"))
    n, profs = 100_000, 20
    t0 = time.perf_counter()
    for i in range(n):
        dia = 1 + (i // (profs * 12)) % 28
        mes = 1 + (i // (profs * 12 * 28)) % 12
        hora = 8 + (i % 12)
        col.inserir(Agendamento(i, random.randint(1, 5000), i % profs, ["CORTE"],
                                f"2026-{mes:02d}-{dia:02d} {hora:02d}:00", 30, 35.0))
    t_ins = (time.perf_counter() - t0) / n
    prof, data = 7, "2026-05-15"
    t_idx = cronometrar(lambda: col.buscar_intervalo(
        "chave_agenda", (prof, data + " 00:00"), (prof, data + " 23:59")), 50)
    t_varr = cronometrar(lambda: [a for a in col if a.profissional_id == prof and a.data == data], 5)
    qtd = len(col.buscar_intervalo("chave_agenda", (prof, data + " 00:00"), (prof, data + " 23:59")))
    t_rem = cronometrar(lambda: [col.remover(i) for i in range(0, 1000)]) / 1000
    out = {"n": n, "insercao_us": t_ins * 1e6, "agenda_indice_us": t_idx * 1e6,
           "agenda_varredura_us": t_varr * 1e6, "itens_retornados": qtd,
           "remocao_us": t_rem * 1e6, "stats": col.estatisticas()}
    print("[agenda]", out)
    return out


if __name__ == "__main__":
    os.makedirs("resultados", exist_ok=True)
    resultado = {
        "ambiente": {"python": sys.version.split()[0], "so": platform.platform(),
                     "processador": platform.processor() or platform.machine()},
        "busca_chave": exp_busca_chave(),
        "altura": exp_altura(),
        "ordenacao": exp_ordenacao(),
        "binaria": exp_binaria(),
        "agenda": exp_agenda(),
    }
    with open("resultados/benchmark.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print("\nResultados salvos em resultados/benchmark.json")
