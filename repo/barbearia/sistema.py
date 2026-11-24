"""
Sistema de Gestão de Barbearia / Salão de Beleza.

Aplicação construída SOBRE o framework: aqui não há nenhuma estrutura de
dados nova; o sistema apenas configura Colecoes (com seus índices) e um
Grafo, e implementa as regras de negócio do salão.
"""

import re

from framework import Colecao, ErroColecao, Grafo, merge_sort
from .modelos import Cliente, Profissional, Servico, Agendamento

_TEL = re.compile(r"^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$")


class ErroAgendamento(Exception):
    pass


def _valida_cliente(c):
    if not c.nome.strip():
        raise ErroColecao("Nome do cliente é obrigatório")
    if not _TEL.match(c.telefone):
        raise ErroColecao(f"Telefone inválido: {c.telefone}")


def _valida_servico(s):
    if s.preco < 0 or s.duracao_min <= 0:
        raise ErroColecao("Preço e duração do serviço devem ser positivos")


class SistemaBarbearia:
    def __init__(self):
        # ----- Coleções (hash = chave primária, AVL = índices) --------
        self.clientes = Colecao("clientes", "id", indices=("nome", "telefone"),
                                validador=_valida_cliente)
        self.profissionais = Colecao("profissionais", "id",
                                     indices=("nome", "especialidade"))
        self.servicos = Colecao("servicos", "codigo", indices=("preco",),
                                validador=_valida_servico)
        self.agendamentos = Colecao(
            "agendamentos", "id",
            indices=("inicio", "data", "cliente_id", "chave_agenda", "status"),
        )
        # ----- Grafos de relacionamento -------------------------------
        # cliente <-> profissional (peso = nº de atendimentos concluídos)
        self.grafo_atendimentos = Grafo()
        # serviço <-> serviço (peso = nº de vezes contratados juntos)
        self.grafo_servicos = Grafo()
        self._prox_agendamento = 1

    # ==================================================================
    # Cadastros (CRUD delegado ao framework)
    # ==================================================================
    def cadastrar_cliente(self, id, nome, telefone, email=""):
        c = self.clientes.inserir(Cliente(id, nome, telefone, email))
        self.grafo_atendimentos.adicionar_vertice(("C", id))
        return c

    def cadastrar_profissional(self, id, nome, especialidade):
        p = self.profissionais.inserir(Profissional(id, nome, especialidade))
        self.grafo_atendimentos.adicionar_vertice(("P", id))
        return p

    def cadastrar_servico(self, codigo, nome, preco, duracao_min):
        s = self.servicos.inserir(Servico(codigo, nome, preco, duracao_min))
        self.grafo_servicos.adicionar_vertice(codigo)
        return s

    def remover_cliente(self, id):
        # Regra: não remove cliente com agendamento futuro em aberto
        abertos = [a for a in self.agendamentos.buscar_por("cliente_id", id)
                   if a.status == "AGENDADO"]
        if abertos:
            raise ErroAgendamento("Cliente possui agendamentos em aberto")
        self.grafo_atendimentos.remover_vertice(("C", id))
        return self.clientes.remover(id)

    # ==================================================================
    # Agendamentos
    # ==================================================================
    def agenda_profissional(self, profissional_id, data):
        """Agenda de um profissional num dia - intervalo na AVL O(log n + k)."""
        return self.agendamentos.buscar_intervalo(
            "chave_agenda",
            (profissional_id, f"{data} 00:00"),
            (profissional_id, f"{data} 23:59"),
        )

    def _tem_conflito(self, profissional_id, inicio, fim, ignorar_id=None):
        for a in self.agenda_profissional(profissional_id, inicio[:10]):
            if a.status == "CANCELADO" or a.id == ignorar_id:
                continue
            if inicio < a.fim and a.inicio < fim:   # sobreposição de intervalos
                return a
        return None

    def agendar(self, cliente_id, profissional_id, codigos_servico, inicio):
        if cliente_id not in self.clientes:
            raise ErroAgendamento(f"Cliente {cliente_id} não cadastrado")
        if profissional_id not in self.profissionais:
            raise ErroAgendamento(f"Profissional {profissional_id} não cadastrado")
        servs = []
        for cod in codigos_servico:
            s = self.servicos.obter(cod)           # O(1) - hash
            if s is None:
                raise ErroAgendamento(f"Serviço {cod} não existe")
            servs.append(s)
        duracao = sum(s.duracao_min for s in servs)
        valor = round(sum(s.preco for s in servs), 2)
        novo = Agendamento(self._prox_agendamento, cliente_id, profissional_id,
                           list(codigos_servico), inicio, duracao, valor)
        choque = self._tem_conflito(profissional_id, novo.inicio, novo.fim)
        if choque:
            raise ErroAgendamento(
                f"Horário indisponível: conflito com agendamento #{choque.id} "
                f"({choque.inicio} - {choque.fim})")
        self.agendamentos.inserir(novo)
        self._prox_agendamento += 1
        return novo

    def remarcar(self, agendamento_id, novo_inicio):
        a = self.agendamentos.obter(agendamento_id)
        if a is None or a.status != "AGENDADO":
            raise ErroAgendamento("Agendamento inexistente ou já encerrado")
        tmp = Agendamento(a.id, a.cliente_id, a.profissional_id, a.servicos,
                          novo_inicio, a.duracao_min)
        if self._tem_conflito(a.profissional_id, tmp.inicio, tmp.fim, ignorar_id=a.id):
            raise ErroAgendamento("Novo horário indisponível")
        return self.agendamentos.atualizar(agendamento_id, inicio=novo_inicio)

    def cancelar(self, agendamento_id):
        return self.agendamentos.atualizar(agendamento_id, status="CANCELADO")

    def concluir(self, agendamento_id):
        """Conclui o atendimento e alimenta os grafos de relacionamento."""
        a = self.agendamentos.atualizar(agendamento_id, status="CONCLUIDO")
        self.grafo_atendimentos.adicionar_aresta(
            ("C", a.cliente_id), ("P", a.profissional_id), 1, acumular=True)
        for i, s1 in enumerate(a.servicos):
            for s2 in a.servicos[i + 1:]:
                self.grafo_servicos.adicionar_aresta(s1, s2, 1, acumular=True)
        return a

    # ==================================================================
    # Consultas e relatórios
    # ==================================================================
    def agenda_do_dia(self, data):
        """Todos os atendimentos do dia em ordem de horário (índice AVL)."""
        return self.agendamentos.buscar_intervalo("inicio", f"{data} 00:00", f"{data} 23:59")

    def historico_cliente(self, cliente_id):
        """Atendimentos do cliente em ordem cronológica (índice AVL + merge sort)."""
        hist = self.agendamentos.buscar_por("cliente_id", cliente_id)
        return merge_sort(hist, chave=lambda a: a.inicio)

    def faturamento_periodo(self, data_ini, data_fim):
        concl = [a for a in self.agendamentos.buscar_intervalo(
            "inicio", f"{data_ini} 00:00", f"{data_fim} 23:59") if a.status == "CONCLUIDO"]
        return round(sum(a.valor for a in concl), 2), len(concl)

    def ranking_profissionais(self, data_ini, data_fim):
        """Faturamento por profissional, do maior para o menor (merge sort)."""
        tot = {}
        for a in self.agendamentos.buscar_intervalo(
                "inicio", f"{data_ini} 00:00", f"{data_fim} 23:59"):
            if a.status == "CONCLUIDO":
                tot[a.profissional_id] = tot.get(a.profissional_id, 0) + a.valor
        linhas = [(self.profissionais.obter(pid).nome, round(v, 2)) for pid, v in tot.items()]
        return merge_sort(linhas, chave=lambda t: t[1], reverso=True)

    # ----- Recomendações via grafo ------------------------------------
    def profissional_preferido(self, cliente_id):
        top = self.grafo_atendimentos.vizinhos_mais_fortes(("C", cliente_id), k=1)
        if not top:
            return None
        (_, pid), vezes = top[0]
        return self.profissionais.obter(pid), vezes

    def sugerir_servicos(self, codigo, k=3):
        """Serviços mais contratados junto com 'codigo' (upsell)."""
        return [(self.servicos.obter(c).nome, peso)
                for c, peso in self.grafo_servicos.vizinhos_mais_fortes(codigo, k)]

    def clientes_da_rede(self, profissional_id):
        """Clientes alcançáveis a partir de um profissional (BFS no grafo)."""
        return [v[1] for v in self.grafo_atendimentos.bfs(("P", profissional_id))
                if v[0] == "C"]
