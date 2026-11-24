"""
Colecao - núcleo reutilizável do framework (CRUD eficiente).

Uma Colecao guarda itens de qualquer tipo (dataclasses, dicionários,
objetos) e combina as estruturas de dados de acordo com a operação:

  Operação                          Estrutura usada        Custo
  --------------------------------  ---------------------  -------------
  Inserir / Atualizar / Remover     TabelaHash + ÁrvoresAVL O(1) + O(log n) por índice
  Buscar por chave única (id)       TabelaHash             O(1) médio
  Buscar por atributo indexado      ÁrvoreAVL (índice)     O(log n)
  Buscar por intervalo              ÁrvoreAVL (índice)     O(log n + k)
  Listagem ordenada por campo       percurso in-order AVL  O(n)  (campo indexado)
                                    ou merge sort          O(n log n) (outro campo)
  Busca em lista já ordenada        busca binária          O(log n)
  Relacionamentos entre itens       Grafo                  O(V + E)

Para reutilizar o framework em outro domínio basta criar uma Colecao
informando qual campo é a chave primária e quais campos devem ser
indexados - nenhuma linha das estruturas precisa ser alterada.
"""

from .estruturas.tabela_hash import TabelaHash
from .estruturas.arvore_avl import ArvoreAVL
from .algoritmos.ordenacao import ordenar
from .algoritmos import busca as _busca


class ErroColecao(Exception):
    pass


def _ler(item, campo):
    """Lê um campo de um objeto ou de um dicionário (ou aplica uma função)."""
    if callable(campo):
        return campo(item)
    if isinstance(item, dict):
        return item[campo]
    return getattr(item, campo)


class Colecao:
    def __init__(self, nome, chave_primaria, indices=(), validador=None):
        """
        nome            : nome da coleção (ex.: "clientes")
        chave_primaria  : campo único que identifica o item (ex.: "id")
        indices         : campos que terão índice AVL (ex.: ("nome", "telefone"))
        validador       : função opcional item -> None que lança erro se inválido
        """
        self.nome = nome
        self.chave_primaria = chave_primaria
        self.validador = validador
        self._dados = TabelaHash()                      # índice primário
        self._indices = {c: ArvoreAVL() for c in indices}  # índices secundários

    # ==================================================================
    # CREATE
    # ==================================================================
    def inserir(self, item):
        if self.validador:
            self.validador(item)
        pk = _ler(item, self.chave_primaria)
        if pk in self._dados:
            raise ErroColecao(f"[{self.nome}] chave duplicada: {pk!r}")
        self._dados.inserir(pk, item)
        self._indexar(item, pk)
        return item

    # ==================================================================
    # READ
    # ==================================================================
    def obter(self, pk):
        """Busca pela chave primária - O(1) médio (tabela hash)."""
        return self._dados.buscar(pk)

    def buscar_por(self, campo, valor):
        """Busca por um atributo.
        Campo indexado -> árvore AVL O(log n); senão -> varredura O(n)."""
        if campo in self._indices:
            pks = self._indices[campo].buscar(valor, ())
            return [self._dados.buscar(pk) for pk in sorted(pks, key=str)]
        return [i for i in self._dados.valores() if _ler(i, campo) == valor]

    def buscar_intervalo(self, campo, inicio, fim):
        """Itens com inicio <= campo <= fim, já em ordem. Exige índice."""
        if campo not in self._indices:
            raise ErroColecao(f"Campo '{campo}' não é indexado em '{self.nome}'")
        out = []
        for _, pks in self._indices[campo].intervalo(inicio, fim):
            out.extend(self._dados.buscar(pk) for pk in sorted(pks, key=str))
        return out

    def buscar_prefixo(self, campo, prefixo):
        """Ex.: nomes que começam com 'Ana' - intervalo [prefixo, prefixo+'￿']."""
        return self.buscar_intervalo(campo, prefixo, prefixo + "￿")

    def filtrar(self, predicado):
        """Filtro livre (varredura O(n)) para consultas não indexadas."""
        return [i for i in self._dados.valores() if predicado(i)]

    # ==================================================================
    # UPDATE
    # ==================================================================
    def atualizar(self, pk, **alteracoes):
        item = self._dados.buscar(pk)
        if item is None:
            raise ErroColecao(f"[{self.nome}] item {pk!r} não encontrado")
        if self.chave_primaria in alteracoes:
            raise ErroColecao("A chave primária não pode ser alterada")
        self._desindexar(item, pk)
        for campo, valor in alteracoes.items():
            if isinstance(item, dict):
                item[campo] = valor
            else:
                setattr(item, campo, valor)
        if self.validador:
            self.validador(item)
        self._indexar(item, pk)
        return item

    # ==================================================================
    # DELETE
    # ==================================================================
    def remover(self, pk):
        item = self._dados.remover(pk)
        if item is None:
            return None
        self._desindexar(item, pk)
        return item

    # ==================================================================
    # Listagem ordenada
    # ==================================================================
    def listar(self, ordenar_por=None, reverso=False, algoritmo="merge"):
        """Lista os itens ordenados.
        - campo indexado  -> percurso in-order na AVL (já ordenado, O(n));
        - outro campo     -> algoritmo de ordenação escolhido (padrão: merge)."""
        if ordenar_por is None:
            ordenar_por = self.chave_primaria
        if isinstance(ordenar_por, str) and ordenar_por in self._indices:
            out = []
            for _, pks in self._indices[ordenar_por].em_ordem():
                out.extend(self._dados.buscar(pk) for pk in sorted(pks, key=str))
            return out[::-1] if reverso else out
        return ordenar(list(self._dados.valores()),
                       chave=lambda i: _ler(i, ordenar_por),
                       algoritmo=algoritmo, reverso=reverso)

    def busca_binaria(self, lista_ordenada, campo, valor):
        """Busca binária sobre uma lista devolvida por listar(campo)."""
        return _busca.busca_binaria_todos(lista_ordenada, valor,
                                          chave=lambda i: _ler(i, campo))

    # ==================================================================
    # Índices (uso interno)
    # ==================================================================
    def _indexar(self, item, pk):
        for campo, arvore in self._indices.items():
            v = _ler(item, campo)
            conjunto = arvore.buscar(v)
            if conjunto is None:
                arvore.inserir(v, {pk})
            else:
                conjunto.add(pk)

    def _desindexar(self, item, pk):
        for campo, arvore in self._indices.items():
            v = _ler(item, campo)
            conjunto = arvore.buscar(v)
            if conjunto is not None:
                conjunto.discard(pk)
                if not conjunto:
                    arvore.remover(v)

    def estatisticas(self):
        return {
            "itens": len(self._dados),
            "fator_carga_hash": round(self._dados.fator_carga, 3),
            "maior_balde_hash": self._dados.maior_balde,
            "altura_indices": {c: a.altura for c, a in self._indices.items()},
        }

    def __len__(self):
        return len(self._dados)

    def __iter__(self):
        return iter(self._dados.valores())

    def __contains__(self, pk):
        return pk in self._dados
