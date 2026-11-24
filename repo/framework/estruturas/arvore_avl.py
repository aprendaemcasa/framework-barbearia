"""
Árvore Binária de Busca balanceada (AVL).

Uma BST comum pode degenerar em uma lista ligada quando os dados chegam
já ordenados (ex.: agendamentos inseridos em ordem cronológica), o que
faz busca/inserção/remoção caírem para O(n). A AVL (Adelson-Velsky e
Landis, 1962) mantém, em cada nó, a diferença de altura entre as
subárvores esquerda e direita em {-1, 0, +1}, aplicando rotações após
cada alteração. Assim a altura fica em O(log n) e todas as operações
básicas custam O(log n) no pior caso.

Esta árvore é usada pelo framework como ÍNDICE SECUNDÁRIO: a chave é um
atributo do item (ex.: nome do cliente, data/hora do agendamento) e o
valor é o conjunto de chaves primárias que possuem aquele atributo
(atributos secundários podem se repetir).
"""


class _No:
    """Nó da árvore. Guarda a chave, o valor associado e a altura."""

    __slots__ = ("chave", "valor", "esq", "dir", "altura")

    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor
        self.esq = None
        self.dir = None
        self.altura = 1


class ArvoreAVL:
    """Árvore AVL genérica: chave -> valor."""

    def __init__(self):
        self._raiz = None
        self._tamanho = 0

    # ------------------------------------------------------------------
    # Utilitários de balanceamento
    # ------------------------------------------------------------------
    @staticmethod
    def _alt(no):
        return no.altura if no else 0

    def _atualiza(self, no):
        no.altura = 1 + max(self._alt(no.esq), self._alt(no.dir))

    def _fator(self, no):
        # fator de balanceamento = altura(esq) - altura(dir)
        return self._alt(no.esq) - self._alt(no.dir)

    def _rot_direita(self, y):
        #        y            x
        #       / \          / \
        #      x   C  -->   A   y
        #     / \              / \
        #    A   B            B   C
        x = y.esq
        y.esq = x.dir
        x.dir = y
        self._atualiza(y)
        self._atualiza(x)
        return x

    def _rot_esquerda(self, x):
        y = x.dir
        x.dir = y.esq
        y.esq = x
        self._atualiza(x)
        self._atualiza(y)
        return y

    def _balancear(self, no):
        """Aplica as rotações simples/duplas necessárias (casos LL, LR, RR, RL)."""
        self._atualiza(no)
        fb = self._fator(no)
        if fb > 1:                       # pesado à esquerda
            if self._fator(no.esq) < 0:  # caso LR -> rotação dupla
                no.esq = self._rot_esquerda(no.esq)
            return self._rot_direita(no)
        if fb < -1:                      # pesado à direita
            if self._fator(no.dir) > 0:  # caso RL -> rotação dupla
                no.dir = self._rot_direita(no.dir)
            return self._rot_esquerda(no)
        return no

    # ------------------------------------------------------------------
    # Inserção  O(log n)
    # ------------------------------------------------------------------
    def inserir(self, chave, valor):
        """Insere (ou substitui) o valor associado à chave."""
        self._raiz = self._inserir(self._raiz, chave, valor)

    def _inserir(self, no, chave, valor):
        if no is None:
            self._tamanho += 1
            return _No(chave, valor)
        if chave < no.chave:
            no.esq = self._inserir(no.esq, chave, valor)
        elif chave > no.chave:
            no.dir = self._inserir(no.dir, chave, valor)
        else:
            no.valor = valor  # chave já existe: atualiza
            return no
        return self._balancear(no)

    # ------------------------------------------------------------------
    # Busca  O(log n)  (iterativa, sem custo de pilha de recursão)
    # ------------------------------------------------------------------
    def buscar(self, chave, padrao=None):
        no = self._raiz
        while no:
            if chave < no.chave:
                no = no.esq
            elif chave > no.chave:
                no = no.dir
            else:
                return no.valor
        return padrao

    def contem(self, chave):
        return self.buscar(chave, _AUSENTE) is not _AUSENTE

    # ------------------------------------------------------------------
    # Remoção  O(log n)
    # ------------------------------------------------------------------
    def remover(self, chave):
        """Remove a chave. Retorna True se ela existia."""
        tamanho_antes = self._tamanho
        self._raiz = self._remover(self._raiz, chave)
        return self._tamanho < tamanho_antes

    def _remover(self, no, chave):
        if no is None:
            return None
        if chave < no.chave:
            no.esq = self._remover(no.esq, chave)
        elif chave > no.chave:
            no.dir = self._remover(no.dir, chave)
        else:
            # Casos 1 e 2: zero ou um filho
            if no.esq is None or no.dir is None:
                self._tamanho -= 1
                return no.esq or no.dir
            # Caso 3: dois filhos -> substitui pelo sucessor (menor da direita)
            suc = no.dir
            while suc.esq:
                suc = suc.esq
            no.chave, no.valor = suc.chave, suc.valor
            no.dir = self._remover(no.dir, suc.chave)
        return self._balancear(no)

    # ------------------------------------------------------------------
    # Percursos
    # ------------------------------------------------------------------
    def em_ordem(self):
        """Percurso in-order: devolve (chave, valor) em ordem crescente. O(n)."""
        pilha, no = [], self._raiz
        while pilha or no:
            while no:
                pilha.append(no)
                no = no.esq
            no = pilha.pop()
            yield no.chave, no.valor
            no = no.dir

    def intervalo(self, inicio, fim):
        """Chaves no intervalo fechado [inicio, fim]. O(log n + k)."""
        resultado = []
        self._intervalo(self._raiz, inicio, fim, resultado)
        return resultado

    def _intervalo(self, no, ini, fim, out):
        if no is None:
            return
        if ini < no.chave:          # ainda pode haver chaves à esquerda
            self._intervalo(no.esq, ini, fim, out)
        if ini <= no.chave <= fim:
            out.append((no.chave, no.valor))
        if no.chave < fim:          # ainda pode haver chaves à direita
            self._intervalo(no.dir, ini, fim, out)

    def minimo(self):
        no = self._raiz
        while no and no.esq:
            no = no.esq
        return (no.chave, no.valor) if no else None

    def maximo(self):
        no = self._raiz
        while no and no.dir:
            no = no.dir
        return (no.chave, no.valor) if no else None

    @property
    def altura(self):
        return self._alt(self._raiz)

    def __len__(self):
        return self._tamanho


_AUSENTE = object()
