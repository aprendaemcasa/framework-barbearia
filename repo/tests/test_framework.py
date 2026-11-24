"""Testes automatizados (unittest). Execute com:  python -m unittest -v"""

import random
import unittest

from framework import (ArvoreAVL, TabelaHash, Grafo, Colecao, ErroColecao,
                       merge_sort, quick_sort, heap_sort, insertion_sort,
                       busca_linear, busca_binaria, busca_binaria_intervalo)
from barbearia.sistema import SistemaBarbearia, ErroAgendamento


class TestAVL(unittest.TestCase):
    def test_insercao_ordenada_mantem_altura_logaritmica(self):
        t = ArvoreAVL()
        for i in range(10_000):          # pior caso para uma BST comum
            t.inserir(i, i)
        self.assertEqual(len(t), 10_000)
        self.assertLessEqual(t.altura, 1.45 * 14)   # 1,44·log2(n) é o limite da AVL

    def test_busca_remocao_e_em_ordem(self):
        t, chaves = ArvoreAVL(), random.sample(range(5000), 1000)
        for k in chaves:
            t.inserir(k, str(k))
        for k in chaves[:500]:
            self.assertTrue(t.remover(k))
        self.assertFalse(t.remover(-1))
        resto = sorted(chaves[500:])
        self.assertEqual([k for k, _ in t.em_ordem()], resto)
        self.assertEqual(t.buscar(resto[0]), str(resto[0]))
        self.assertIsNone(t.buscar(chaves[0]))

    def test_intervalo(self):
        t = ArvoreAVL()
        for k in range(100):
            t.inserir(k, k)
        self.assertEqual([k for k, _ in t.intervalo(10, 15)], [10, 11, 12, 13, 14, 15])


class TestHash(unittest.TestCase):
    def test_crud_e_redimensionamento(self):
        h = TabelaHash(capacidade=8)
        for i in range(1000):
            h.inserir(f"cli{i}", i)
        self.assertEqual(len(h), 1000)
        self.assertLessEqual(h.fator_carga, 0.75)
        self.assertEqual(h.buscar("cli500"), 500)
        h.inserir("cli500", -1)                    # atualização
        self.assertEqual(h.buscar("cli500"), -1)
        self.assertEqual(h.remover("cli500"), -1)
        self.assertNotIn("cli500", h)
        self.assertEqual(len(h), 999)


class TestGrafo(unittest.TestCase):
    def test_bfs_dfs_dijkstra(self):
        g = Grafo()
        g.adicionar_aresta("A", "B", 4)
        g.adicionar_aresta("A", "C", 1)
        g.adicionar_aresta("C", "B", 2)
        g.adicionar_aresta("B", "D", 5)
        self.assertEqual(set(g.bfs("A")), {"A", "B", "C", "D"})
        self.assertEqual(g.dfs("A")[0], "A")
        dist, caminho = g.dijkstra("A", "D")
        self.assertEqual(dist, 8)
        self.assertEqual(caminho, ["A", "C", "B", "D"])
        g.remover_vertice("B")
        self.assertEqual(g.num_arestas, 1)


class TestOrdenacaoBusca(unittest.TestCase):
    def test_todos_os_algoritmos(self):
        dados = [random.randint(0, 1000) for _ in range(2000)]
        esperado = sorted(dados)
        for f in (merge_sort, quick_sort, heap_sort, insertion_sort):
            self.assertEqual(f(dados), esperado, f.__name__)
            self.assertEqual(f(dados, reverso=True), esperado[::-1], f.__name__)
        self.assertEqual(merge_sort([]), [])

    def test_merge_sort_estavel(self):
        pares = [("b", 1), ("a", 1), ("c", 0), ("d", 1)]
        self.assertEqual(merge_sort(pares, chave=lambda p: p[1]),
                         [("c", 0), ("b", 1), ("a", 1), ("d", 1)])

    def test_buscas(self):
        v = list(range(0, 200, 2))
        self.assertEqual(busca_binaria(v, 64), 32)
        self.assertEqual(busca_binaria(v, 65), -1)
        self.assertEqual(busca_linear(v, 64), 32)
        self.assertEqual(busca_binaria_intervalo(v, 10, 16), [10, 12, 14, 16])


class TestColecao(unittest.TestCase):
    def test_crud_completo(self):
        c = Colecao("produtos", "id", indices=("nome", "preco"))
        c.inserir({"id": 1, "nome": "Pomada", "preco": 35.0})
        c.inserir({"id": 2, "nome": "Shampoo", "preco": 28.0})
        c.inserir({"id": 3, "nome": "Óleo", "preco": 35.0})
        with self.assertRaises(ErroColecao):
            c.inserir({"id": 1, "nome": "X", "preco": 1})
        self.assertEqual(c.obter(2)["nome"], "Shampoo")
        self.assertEqual(len(c.buscar_por("preco", 35.0)), 2)
        c.atualizar(3, preco=40.0)
        self.assertEqual([p["id"] for p in c.listar("preco")], [2, 1, 3])
        self.assertEqual(c.remover(1)["nome"], "Pomada")
        self.assertEqual(c.buscar_por("preco", 35.0), [])
        self.assertEqual(len(c), 2)


class TestBarbearia(unittest.TestCase):
    def setUp(self):
        s = self.s = SistemaBarbearia()
        s.cadastrar_servico("CORTE", "Corte masculino", 35.0, 30)
        s.cadastrar_servico("BARBA", "Barba completa", 25.0, 20)
        s.cadastrar_profissional(1, "Carlos", "Barbeiro")
        s.cadastrar_cliente(1, "Ana Souza", "(99) 98888-7777")

    def test_conflito_de_horario(self):
        self.s.agendar(1, 1, ["CORTE", "BARBA"], "2026-11-30 09:00")   # 09:00-09:50
        with self.assertRaises(ErroAgendamento):
            self.s.agendar(1, 1, ["CORTE"], "2026-11-30 09:30")
        ok = self.s.agendar(1, 1, ["CORTE"], "2026-11-30 09:50")       # encosta, não sobrepõe
        self.assertEqual(ok.fim, "2026-11-30 10:20")

    def test_validacao_telefone(self):
        with self.assertRaises(ErroColecao):
            self.s.cadastrar_cliente(2, "João", "123")

    def test_conclusao_alimenta_grafo(self):
        a = self.s.agendar(1, 1, ["CORTE", "BARBA"], "2026-11-30 10:00")
        self.s.concluir(a.id)
        prof, vezes = self.s.profissional_preferido(1)
        self.assertEqual((prof.nome, vezes), ("Carlos", 1))
        self.assertEqual(self.s.sugerir_servicos("CORTE"), [("Barba completa", 1)])
        self.assertEqual(self.s.faturamento_periodo("2026-11-30", "2026-11-30"), (60.0, 1))


if __name__ == "__main__":
    unittest.main()
