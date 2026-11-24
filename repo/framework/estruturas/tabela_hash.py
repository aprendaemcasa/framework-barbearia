"""
Tabela Hash com encadeamento separado (separate chaining).

Usada como ÍNDICE PRIMÁRIO do framework: chave única (id do cliente,
CPF, código do serviço...) -> registro. Em média, inserção, busca e
remoção custam O(1).

Decisões de projeto:
  * Função de dispersão: para strings usa-se o hash polinomial
    (método de Horner, base 31, como em Java/Sedgewick); para inteiros,
    o método da multiplicação de Knuth. Os dois são reduzidos ao
    tamanho da tabela por módulo.
  * Colisões: cada posição ("balde") é uma lista de pares [chave, valor].
  * Redimensionamento: quando o fator de carga (n / m) passa de 0,75 a
    tabela dobra de tamanho e todos os itens são redistribuídos
    (rehash). O custo amortizado da inserção continua O(1).
"""


class TabelaHash:
    FATOR_CARGA_MAX = 0.75
    _A_KNUTH = 2654435769  # ~ (sqrt(5)-1)/2 * 2^32  (método da multiplicação)

    def __init__(self, capacidade=16):
        self._m = max(8, capacidade)
        self._baldes = [[] for _ in range(self._m)]
        self._n = 0
        self.colisoes = 0  # contador usado no relatório/benchmark

    # ------------------------------------------------------------------
    # Função de dispersão
    # ------------------------------------------------------------------
    def _hash(self, chave):
        if isinstance(chave, int):
            return ((chave * self._A_KNUTH) & 0xFFFFFFFF) % self._m
        texto = str(chave)
        h = 0
        for c in texto:                      # método de Horner
            h = (31 * h + ord(c)) & 0xFFFFFFFF
        return h % self._m

    # ------------------------------------------------------------------
    # Operações CRUD
    # ------------------------------------------------------------------
    def inserir(self, chave, valor):
        """Insere ou atualiza. Retorna True se a chave era nova."""
        balde = self._baldes[self._hash(chave)]
        for par in balde:
            if par[0] == chave:
                par[1] = valor
                return False
        if balde:
            self.colisoes += 1
        balde.append([chave, valor])
        self._n += 1
        if self._n / self._m > self.FATOR_CARGA_MAX:
            self._redimensionar(self._m * 2)
        return True

    def buscar(self, chave, padrao=None):
        for k, v in self._baldes[self._hash(chave)]:
            if k == chave:
                return v
        return padrao

    def contem(self, chave):
        return any(k == chave for k, _ in self._baldes[self._hash(chave)])

    def remover(self, chave):
        """Remove a chave e devolve o valor (ou None se não existir)."""
        balde = self._baldes[self._hash(chave)]
        for i, (k, v) in enumerate(balde):
            if k == chave:
                balde.pop(i)
                self._n -= 1
                return v
        return None

    def _redimensionar(self, nova_cap):
        antigos = self._baldes
        self._m = nova_cap
        self._baldes = [[] for _ in range(self._m)]
        self._n = 0
        self.colisoes = 0
        for balde in antigos:
            for k, v in balde:
                self.inserir(k, v)

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------
    def chaves(self):
        for balde in self._baldes:
            for k, _ in balde:
                yield k

    def valores(self):
        for balde in self._baldes:
            for _, v in balde:
                yield v

    @property
    def fator_carga(self):
        return self._n / self._m

    @property
    def maior_balde(self):
        return max(len(b) for b in self._baldes)

    def __len__(self):
        return self._n

    def __contains__(self, chave):
        return self.contem(chave)
