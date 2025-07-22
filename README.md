# IA Genética – Space Invaders

Este projeto demonstra como aplicar IA Genética para resolver problemas onde não conhecemos previamente a solução ótima, utilizando como exemplo o clássico jogo Space Invaders.

## Demonstração em vídeo

Assista ao vídeo completo no YouTube para entender a motivação, funcionamento do algoritmo genético, desafios encontrados e resultados:

[▶️ Assista aqui](https://www.youtube.com/watch?v=vaJUpNgk-10)

## Instalação

1. Certifique-se de ter o **Python 3.12** instalado.
2. Instale as dependências necessárias:

   ```bash
   pip install -r requirements.txt


## Sobre o Projeto

IA Genética foi utilizada para treinar um agente capaz de eliminar todos os inimigos no menor tempo possível, sem saber previamente a melhor sequência de movimentos.

O agente evolui suas estratégias ao longo das gerações, explorando soluções inovadoras para o jogo.

O projeto demonstra a eficácia dos algoritmos evolutivos para problemas de busca e otimização onde o espaço de soluções é enorme.

## Simulador (Jogo base)

Acesse /Fontes/v0_jogo_base.py

nas linhas 22 e 23 defina o modo a ser jogado
'''
COMPORTAMENTO_INIMIGOS = "aleatorio"  # "aleatorio", "linear" ou "desviando"
MODO_JOGADOR = "manual"  # "linear", "aleatorio" ou "manual"
'''

Execute o script


## IA Genética

Acesse /Fontes/v1_jogador_genetico.py

Você pode alteras as configurações nas variáveis abaixo
'''
INIMIGO_PARADO = True
INIMIGO_INICIADO_ALEATORIO = True  

# =============== PARÂMETROS DO ALGORITMO GENÉTICO ===============
NUM_INDIVIDUOS = 60           # Indivíduos por geração
NUM_GERACOES = 30            # Gerações
NUM_JOGADAS = 600             # Jogadas por indivíduo
ELITISMO = True               # Manter melhor indivíduo na próxima geração
N_MELHOR = 1                 # Quantos melhores mantém (elitismo)
PONTO_CORTE = 300             # Genes do pai1 no crossover (restante do pai2)
PROB_MUTACAO = 0.5            # Prob. de mutação por indivíduo
N_GENES_MUTACAO = (40,80)     # Quantidade de genes mutados (min, max)
GERACOES_VISUALIZACAO = 3   # A cada quantas gerações exibir visualmente o melhor
QUANTIDADE_INIMIGOS = 7       # Quantidade de inimigos por rodada

# =============== PARÂMETROS DO JOGO ===============
LARGURA, ALTURA = 1100, 700
FPS = 2000
MOSTRAR_TELA = False  # Apenas nas gerações de visualização
'''

Também é possível alterar a inicialização para aumentar ou retirar individuos com movimentos laterais repetidos.
'''
def gerar_populacao_inicial():
    populacao = []
    individuos_por_tipo = 4
    tamanhos_blocos = [30,90,150]  # blocos que você quer
'''

Execute o script


## Autor

Gustavo Malta Guimarães  
Pós-graduação em Inteligência Artificial para Devs – FIAP
