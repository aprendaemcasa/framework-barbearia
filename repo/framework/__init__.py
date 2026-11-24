"""
Framework para gerenciamento eficiente de coleções de dados.
TDE 02 - Estrutura de Dados - UNIFACEMA - ADS 2026.2
"""

from .colecao import Colecao, ErroColecao
from .estruturas.arvore_avl import ArvoreAVL
from .estruturas.tabela_hash import TabelaHash
from .estruturas.grafo import Grafo
from .algoritmos.ordenacao import ordenar, merge_sort, quick_sort, heap_sort, insertion_sort
from .algoritmos.busca import busca_linear, busca_binaria, busca_binaria_todos, busca_binaria_intervalo

__all__ = [
    "Colecao", "ErroColecao", "ArvoreAVL", "TabelaHash", "Grafo",
    "ordenar", "merge_sort", "quick_sort", "heap_sort", "insertion_sort",
    "busca_linear", "busca_binaria", "busca_binaria_todos", "busca_binaria_intervalo",
]
