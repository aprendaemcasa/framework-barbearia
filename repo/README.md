# Framework para Gerenciamento Eficiente de Coleções de Dados
### Sistema de Gestão de Barbearia / Salão de Beleza

TDE 02 — Estrutura de Dados — UNIFACEMA — ADS 2026.2
Prof. Nayron Morais Almeida

**Equipe:** André de Sousa, Lucas Mendes, Mateus Leandro, Marcos Vinicius, Wanderson Emanuel

## Estrutura

```
framework/                 # núcleo reutilizável (independente do domínio)
  colecao.py               # Colecao: CRUD + índices (hash + AVL) + listagem ordenada
  estruturas/
    tabela_hash.py         # tabela hash com encadeamento e rehash (fator de carga 0,75)
    arvore_avl.py          # árvore binária de busca balanceada (AVL)
    grafo.py               # grafo ponderado (lista de adjacência): BFS, DFS, Dijkstra
  algoritmos/
    ordenacao.py           # merge, quick, heap e insertion sort (genéricos, com chave)
    busca.py               # busca linear, binária, limites e intervalo
barbearia/                 # aplicação construída sobre o framework
  modelos.py               # Cliente, Profissional, Servico, Agendamento
  sistema.py               # regras de negócio (conflito de horário, relatórios, recomendações)
tests/test_framework.py    # 12 testes automatizados
main.py                    # demonstração completa do CRUD
benchmark.py               # experimentos de desempenho -> resultados/benchmark.json
```

## Como executar (Python 3.10+, sem dependências externas)

```bash
python main.py              # demonstração
python -m unittest -v       # testes
python benchmark.py         # experimentos de desempenho
```

## Reutilizando o framework em outro domínio

```python
from framework import Colecao

produtos = Colecao("produtos", chave_primaria="id", indices=("nome", "preco"))
produtos.inserir({"id": 1, "nome": "Pomada", "preco": 35.0})
produtos.obter(1)                              # hash      O(1)
produtos.buscar_por("preco", 35.0)             # AVL       O(log n)
produtos.buscar_intervalo("preco", 20, 50)     # AVL       O(log n + k)
produtos.listar("nome")                        # in-order  O(n)
produtos.atualizar(1, preco=39.9)
produtos.remover(1)
```
