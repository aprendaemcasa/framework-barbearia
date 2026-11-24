"""
Modelos (entidades) do domínio Barbearia / Salão de Beleza.

As datas são guardadas como texto no formato ISO "AAAA-MM-DD HH:MM".
Esse formato tem uma vantagem importante para o framework: a ordem
alfabética coincide com a ordem cronológica, então a mesma árvore AVL
que ordena nomes também ordena horários sem nenhuma conversão.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

FORMATO_DATA = "%Y-%m-%d %H:%M"


@dataclass
class Cliente:
    id: int
    nome: str
    telefone: str
    email: str = ""


@dataclass
class Profissional:
    id: int
    nome: str
    especialidade: str          # ex.: "Barbeiro", "Cabeleireira", "Manicure"


@dataclass
class Servico:
    codigo: str                 # ex.: "CORTE", "BARBA"
    nome: str
    preco: float
    duracao_min: int


@dataclass
class Agendamento:
    id: int
    cliente_id: int
    profissional_id: int
    servicos: list              # lista de códigos de serviço
    inicio: str                 # "AAAA-MM-DD HH:MM"
    duracao_min: int = 0
    valor: float = 0.0
    status: str = "AGENDADO"    # AGENDADO | CONCLUIDO | CANCELADO

    # --- campos derivados (usados como chaves de índice) ---------------
    @property
    def data(self):
        return self.inicio[:10]

    @property
    def fim(self):
        dt = datetime.strptime(self.inicio, FORMATO_DATA) + timedelta(minutes=self.duracao_min)
        return dt.strftime(FORMATO_DATA)

    @property
    def chave_agenda(self):
        """(profissional, horário): permite buscar a agenda de UM profissional
        em UM dia por intervalo na AVL, em O(log n + k)."""
        return (self.profissional_id, self.inicio)
