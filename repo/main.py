"""
Demonstração do Sistema de Gestão de Barbearia / Salão de Beleza
construído sobre o framework de coleções.  Execute:  python main.py
"""

from barbearia.sistema import SistemaBarbearia, ErroAgendamento


def linha(titulo):
    print(f"\n{'=' * 62}\n {titulo}\n{'=' * 62}")


def main():
    s = SistemaBarbearia()

    # ---------------- CREATE ----------------
    for cod, nome, preco, dur in [
        ("CORTE", "Corte masculino", 35.0, 30), ("BARBA", "Barba completa", 25.0, 20),
        ("SOBR", "Design de sobrancelha", 15.0, 15), ("PROG", "Escova progressiva", 120.0, 90),
        ("HIDR", "Hidratação capilar", 45.0, 40), ("MANI", "Manicure", 30.0, 40),
        ("PEDI", "Pedicure", 35.0, 45), ("PINT", "Pigmentação de barba", 30.0, 25),
    ]:
        s.cadastrar_servico(cod, nome, preco, dur)

    s.cadastrar_profissional(1, "Carlos Lima", "Barbeiro")
    s.cadastrar_profissional(2, "Juliana Rocha", "Cabeleireira")
    s.cadastrar_profissional(3, "Patrícia Melo", "Manicure")

    for i, (nome, tel) in enumerate([
        ("Rafael Costa", "(99) 98111-2233"), ("Ana Beatriz", "(99) 98222-3344"),
        ("Bruno Alves", "(99) 98333-4455"), ("Camila Dias", "(99) 98444-5566"),
        ("Diego Santos", "(99) 98555-6677"), ("Ana Clara", "(99) 98666-7788"),
    ], start=1):
        s.cadastrar_cliente(i, nome, tel)

    agenda = [
        (1, 1, ["CORTE", "BARBA"], "2026-11-30 08:00"), (3, 1, ["CORTE"], "2026-11-30 09:00"),
        (5, 1, ["CORTE", "BARBA", "SOBR"], "2026-11-30 10:00"), (2, 2, ["PROG"], "2026-11-30 08:30"),
        (4, 2, ["HIDR"], "2026-11-30 10:30"), (6, 3, ["MANI", "PEDI"], "2026-11-30 09:00"),
        (1, 1, ["CORTE", "BARBA"], "2026-12-07 08:00"), (3, 1, ["BARBA", "PINT"], "2026-12-07 09:00"),
        (2, 3, ["MANI"], "2026-12-07 14:00"),
    ]
    for cli, prof, servs, ini in agenda:
        s.agendar(cli, prof, servs, ini)

    linha("Tentativa de agendamento em horário ocupado")
    try:
        s.agendar(4, 1, ["CORTE"], "2026-11-30 08:20")
    except ErroAgendamento as e:
        print("  Bloqueado ->", e)

    # ---------------- READ ----------------
    linha("Agenda de 30/11/2026 (intervalo na árvore AVL)")
    for a in s.agenda_do_dia("2026-11-30"):
        print(f"  {a.inicio[11:]}-{a.fim[11:]}  {s.profissionais.obter(a.profissional_id).nome:<14}"
              f" {s.clientes.obter(a.cliente_id).nome:<13} {'+'.join(a.servicos):<18} R$ {a.valor:6.2f}")

    linha("Busca por prefixo do nome 'Ana' (índice AVL)")
    for c in s.clientes.buscar_prefixo("nome", "Ana"):
        print(f"  #{c.id} {c.nome} - {c.telefone}")

    linha("Busca por id (tabela hash O(1))")
    print(" ", s.clientes.obter(3))

    linha("Serviços ordenados por preço (decrescente)")
    for sv in s.servicos.listar("preco", reverso=True):
        print(f"  {sv.codigo:<6} {sv.nome:<24} R$ {sv.preco:7.2f}  {sv.duracao_min} min")

    linha("Serviços por duração - quick sort + busca binária (40 min)")
    por_dur = s.servicos.listar("duracao_min", algoritmo="quick")
    print("  ", [f"{x.codigo}:{x.duracao_min}" for x in por_dur])
    print("   40 min ->", [x.nome for x in s.servicos.busca_binaria(por_dur, "duracao_min", 40)])

    # ---------------- UPDATE / DELETE ----------------
    linha("Atualização, remarcação, cancelamento e conclusão")
    s.clientes.atualizar(4, telefone="(99) 99999-0000")
    print("  Telefone atualizado:", s.clientes.obter(4).telefone)
    s.remarcar(5, "2026-11-30 12:00")
    print("  Agendamento #5 remarcado para", s.agendamentos.obter(5).inicio)
    s.cancelar(9)
    print("  Agendamento #9:", s.agendamentos.obter(9).status)
    for aid in range(1, 9):
        s.concluir(aid)
    s.cadastrar_cliente(99, "Cliente Teste", "(99) 90000-0000")
    print("  Removido:", s.remover_cliente(99).nome)

    # ---------------- Relatórios / grafo ----------------
    linha("Relatórios")
    total, qtd = s.faturamento_periodo("2026-11-01", "2026-12-31")
    print(f"  Faturamento nov-dez: R$ {total:.2f} em {qtd} atendimentos")
    for nome, v in s.ranking_profissionais("2026-11-01", "2026-12-31"):
        print(f"   {nome:<15} R$ {v:7.2f}")

    linha("Recomendações (grafo)")
    prof, vezes = s.profissional_preferido(1)
    print(f"  Profissional preferido de Rafael: {prof.nome} ({vezes} atendimentos)")
    print("  Quem faz CORTE também costuma levar:", s.sugerir_servicos("CORTE"))
    print("  Clientes na rede do Carlos (BFS):",
          [s.clientes.obter(c).nome for c in s.clientes_da_rede(1)])

    linha("Estatísticas internas das coleções")
    for col in (s.clientes, s.agendamentos):
        print(f"  {col.nome}: {col.estatisticas()}")


if __name__ == "__main__":
    main()
