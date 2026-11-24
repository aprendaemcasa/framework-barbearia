"""
Grafo ponderado representado por lista de adjacência.

No framework o grafo modela RELAÇÕES entre os itens das coleções. Na
barbearia, por exemplo:
  * cliente --atendido_por--> profissional  (peso = nº de atendimentos)
  * serviço <--> serviço  (peso = nº de vezes contratados juntos)

A lista de adjacência foi escolhida em vez da matriz porque o grafo é
esparso (cada cliente se relaciona com poucos profissionais): ocupa
O(V + E) de memória, contra O(V²) da matriz.

Algoritmos disponíveis:
  * BFS  (busca em largura)      O(V + E)
  * DFS  (busca em profundidade) O(V + E)
  * Dijkstra (caminho mínimo, pesos não negativos) O((V + E) log V)
  * vizinhos mais fortes (top-k por peso) -> usado em recomendações
"""

import heapq
from collections import deque


class Grafo:
    def __init__(self, dirigido=False):
        self.dirigido = dirigido
        self._adj = {}  # vértice -> {vizinho: peso}

    # ------------------------------------------------------------------
    # CRUD de vértices e arestas
    # ------------------------------------------------------------------
    def adicionar_vertice(self, v):
        self._adj.setdefault(v, {})

    def remover_vertice(self, v):
        if v not in self._adj:
            return False
        for viz in list(self._adj):
            self._adj[viz].pop(v, None)
        del self._adj[v]
        return True

    def adicionar_aresta(self, u, v, peso=1, acumular=False):
        """Cria a aresta u-v. Se acumular=True soma o peso ao existente."""
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        novo = self._adj[u].get(v, 0) + peso if acumular else peso
        self._adj[u][v] = novo
        if not self.dirigido:
            self._adj[v][u] = novo

    def remover_aresta(self, u, v):
        self._adj.get(u, {}).pop(v, None)
        if not self.dirigido:
            self._adj.get(v, {}).pop(u, None)

    def vizinhos(self, v):
        return self._adj.get(v, {})

    def peso(self, u, v):
        return self._adj.get(u, {}).get(v)

    # ------------------------------------------------------------------
    # Percursos
    # ------------------------------------------------------------------
    def bfs(self, origem):
        """Ordem de visita em largura a partir de 'origem'."""
        if origem not in self._adj:
            return []
        visitados, fila, ordem = {origem}, deque([origem]), []
        while fila:
            v = fila.popleft()
            ordem.append(v)
            for w in self._adj[v]:
                if w not in visitados:
                    visitados.add(w)
                    fila.append(w)
        return ordem

    def dfs(self, origem):
        """Ordem de visita em profundidade (versão iterativa com pilha)."""
        if origem not in self._adj:
            return []
        visitados, pilha, ordem = set(), [origem], []
        while pilha:
            v = pilha.pop()
            if v in visitados:
                continue
            visitados.add(v)
            ordem.append(v)
            for w in reversed(list(self._adj[v])):
                if w not in visitados:
                    pilha.append(w)
        return ordem

    def dijkstra(self, origem, destino=None):
        """Distâncias mínimas a partir da origem (fila de prioridade/heap).
        Se 'destino' for informado, devolve (distancia, caminho)."""
        dist, anterior = {origem: 0}, {}
        heap = [(0, origem)]
        while heap:
            d, v = heapq.heappop(heap)
            if d > dist.get(v, float("inf")):
                continue
            if v == destino:
                break
            for w, p in self._adj.get(v, {}).items():
                nd = d + p
                if nd < dist.get(w, float("inf")):
                    dist[w], anterior[w] = nd, v
                    heapq.heappush(heap, (nd, w))
        if destino is None:
            return dist
        if destino not in dist:
            return float("inf"), []
        caminho, v = [destino], destino
        while v != origem:
            v = anterior[v]
            caminho.append(v)
        return dist[destino], caminho[::-1]

    def vizinhos_mais_fortes(self, v, k=3, filtro=None):
        """Top-k vizinhos de maior peso (heap -> O(d log k))."""
        itens = self._adj.get(v, {}).items()
        if filtro:
            itens = [(w, p) for w, p in itens if filtro(w)]
        return heapq.nlargest(k, itens, key=lambda par: par[1])

    # ------------------------------------------------------------------
    @property
    def num_vertices(self):
        return len(self._adj)

    @property
    def num_arestas(self):
        total = sum(len(v) for v in self._adj.values())
        return total if self.dirigido else total // 2

    def __contains__(self, v):
        return v in self._adj
