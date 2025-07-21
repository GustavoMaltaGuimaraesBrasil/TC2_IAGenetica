import pygame
import sys
import random
import csv
import os
import json
import matplotlib.pyplot as plt
from pygame.locals import *

pygame.init()
pygame.font.init()

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

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

# Variável global para armazenar posições fixas dos inimigos
posicoes_inimigos = []

def carrega_imagem(nome, size):
    return pygame.transform.scale(pygame.image.load(nome), size)

def salvar_melhor_individuo(ind):
    with open("Fontes/melhor_individuo.json", "w") as f:
        json.dump({"genes": ind.genes, "fitness": ind.fitness}, f)

def carregar_melhor_individuo():
    with open("Fontes/melhor_individuo.json", "r") as f:
        data = json.load(f)
    return Individuo(data["genes"])

def exibe_grafico(log_fits, medias):
    plt.figure(figsize=(10,5))
    plt.plot(log_fits, label='Melhor Fitness')
    plt.plot(medias, label='Fitness Médio')
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.title("Evolução do Algoritmo Genético")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

class Individuo:
    def __init__(self, genes=None):
        if genes is None:
            self.genes = [random.randint(0, 3) for _ in range(NUM_JOGADAS)]
        else:
            self.genes = genes[:]
        self.fitness = 0
        self.log_acertos = []

    def __repr__(self):
        return str(self.genes)



def gerar_populacao_inicial():
    populacao = []
    individuos_por_tipo = 4
    tamanhos_blocos = [30,90,150]  # blocos que você quer

    for tamanho_bloco in tamanhos_blocos:
        tamanho_padrao = tamanho_bloco + 1  # movimentos repetidos + 1 gene aleatório
        for _ in range(individuos_por_tipo):
            genes = []
            # Quantas vezes o padrão cabe em NUM_JOGADAS?
            repeticoes = NUM_JOGADAS // tamanho_padrao
            sobra = NUM_JOGADAS % tamanho_padrao

            for _ in range(repeticoes):
                lado = random.choice([1, 2])  # movimento repetido
                genes += [lado] * tamanho_bloco
                acao = random.choice([0, 3])  # gene aleatório
                genes.append(acao)

            # Preencher o resto cortando parte do padrão para não passar do tamanho
            if sobra > 0:
                lado = random.choice([1, 2])
                if sobra <= tamanho_bloco:
                    genes += [lado] * sobra
                else:
                    genes += [lado] * tamanho_bloco
                    acao = random.choice([0, 3])
                    genes.append(acao)
                    genes = genes[:NUM_JOGADAS]  # garante tamanho exato

            # Garantir tamanho exato (por segurança)
            genes = genes[:NUM_JOGADAS]

            populacao.append(Individuo(genes))

    # Completar população com aleatórios, se necessário
    while len(populacao) < NUM_INDIVIDUOS:
        populacao.append(Individuo())

    return populacao


def crossover(pai1, pai2):
    corte = PONTO_CORTE
    filho1 = Individuo(pai1.genes[:corte] + pai2.genes[corte:])
    filho2 = Individuo(pai2.genes[:corte] + pai1.genes[corte:])
    return filho1, filho2

# def mutacao(individuo):
#     if random.random() < PROB_MUTACAO:
#         n = random.randint(N_GENES_MUTACAO[0], N_GENES_MUTACAO[1])
#         for _ in range(n):
#             idx = random.randint(0, NUM_JOGADAS - 1)
#             individuo.genes[idx] = random.randint(0, 3)



def mutacao(individuo):
    if random.random() < PROB_MUTACAO:
        n_genes_mutados = random.randint(N_GENES_MUTACAO[0], N_GENES_MUTACAO[1])
        tamanho_bloco = 20  # 20 movimentos laterais
        n_blocos = max(1, n_genes_mutados // (tamanho_bloco + 1))  # +1 ação

        for _ in range(n_blocos):
            start_idx = random.randint(0, NUM_JOGADAS - (tamanho_bloco + 1))
            lado = random.choice([1, 2])  # movimento lateral repetido
            # Mutar os 20 movimentos repetidos
            for i in range(start_idx, start_idx + tamanho_bloco):
                individuo.genes[i] = lado
            # Mutar a ação seguinte (parado ou atirar)
            individuo.genes[start_idx + tamanho_bloco] = random.choice([0, 3])


def selecao(populacao):
    #return selecao_elitismo(populacao=populacao, n_melhores=10 )
    return selecao_torneio(populacao=populacao, k=3)

def selecao_torneio(populacao, k=2):
    competidores = random.sample(populacao, k)
    return max(competidores, key=lambda ind: ind.fitness)

def selecao_roleta(populacao):
    soma_fitness = sum(ind.fitness for ind in populacao)
    pick = random.uniform(0, soma_fitness)
    atual = 0
    for ind in populacao:
        atual += ind.fitness
        if atual >= pick:
            return ind

def selecao_ranking(populacao):
    populacao_ordenada = sorted(populacao, key=lambda ind: ind.fitness)
    n = len(populacao)
    # Atribui peso linear decrescente do pior para o melhor
    pesos = [i for i in range(1, n+1)]  # pior=1 ... melhor=n
    soma_pesos = sum(pesos)
    pick = random.uniform(0, soma_pesos)
    atual = 0
    for ind, peso in zip(populacao_ordenada, pesos):
        atual += peso
        if atual >= pick:
            return ind




def calcular_fitness(acertos, jogada_acertos, jogadas_usadas, genes):
    PESO_INIMIGOS_ABATIDOS = 0.4  # Peso dos inimigos abatidos
    PESO_ORDEM_ACERTOS = 0.2 # Peso da ordem dos acertos
    BONUS_FINAL = 0.2        # Bônus para abate total rápido


    fit1 = (acertos / QUANTIDADE_INIMIGOS) * PESO_INIMIGOS_ABATIDOS

    if sum(jogada_acertos) == 0:
        fit2 = 0
    else:
        posicoes = [i for i, v in enumerate(jogada_acertos) if v == 1]
        fit2 = sum([(NUM_JOGADAS - p) for p in posicoes]) / (QUANTIDADE_INIMIGOS * NUM_JOGADAS)
    fit2 *= PESO_ORDEM_ACERTOS

    bonus = 0
    if acertos == QUANTIDADE_INIMIGOS:
        bonus = BONUS_FINAL * (NUM_JOGADAS - jogadas_usadas) / NUM_JOGADAS

    fitness_final = fit1 + fit2 + bonus

    # Garante que fitness não seja negativo
    return max(fitness_final, 0)


class Entidade:
    def __init__(self, x, y, imagem):
        self.x = x
        self.y = y
        self.imagem = imagem

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x, self.y))

class Tiro:
    def __init__(self, jogador):
        self.jogador = jogador
        self.offset_x = 40 - 2
        self.rect = pygame.Rect(jogador.x + self.offset_x, jogador.y, 5, 10)
        self.velocidade = 7

    def mover(self):
        self.rect.x = self.jogador.x + self.offset_x
        self.rect.y -= self.velocidade

    def fora_da_tela(self):
        return self.rect.y < 0

    def desenhar(self, tela):
        pygame.draw.rect(tela, BRANCO, self.rect)

class JogadorGenetico(Entidade):
    def __init__(self, genes):
        super().__init__(LARGURA // 2 - 40, ALTURA - 70, nave_img)
        self.genes = genes
        self.acao_idx = 0
        self.tiros = []

    def mover(self):
        if self.acao_idx >= len(self.genes):
            return
        comando = self.genes[self.acao_idx]
        if comando == 1:  # esquerda
            self.x = max(0, self.x - 5)
        elif comando == 2:  # direita
            self.x = min(LARGURA - self.imagem.get_width(), self.x + 5)
        self.acao_idx += 1

    def atirar(self):
        if self.acao_idx == 0: return
        comando = self.genes[self.acao_idx - 1]
        if comando == 3 and len(self.tiros) == 0:
            self.tiros.append(Tiro(self))

    def atualizar_tiros(self):
        for tiro in self.tiros:
            tiro.mover()
        self.tiros = [t for t in self.tiros if not t.fora_da_tela()]

class Inimigo(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, inimigo_img)
        self.direcao = 1

    def mover(self, outros_inimigos, tiros):
        nova_x = self.x + 5 * self.direcao
        nova_y = self.y + 0.7
        if INIMIGO_PARADO:
            nova_x = self.x
            nova_y = self.y

        colisao = False
        for outro in outros_inimigos:
            if outro is not self:
                if pygame.Rect(nova_x, nova_y, 60, 40).colliderect(pygame.Rect(outro.x, outro.y, 60, 40)):
                    colisao = True
                    break
        if colisao or nova_x <= 0 or nova_x >= LARGURA - self.imagem.get_width():
            self.direcao *= -1
        else:
            self.x = nova_x
            self.y = nova_y

def inicializar_posicoes_inimigos():
    global posicoes_inimigos
    if INIMIGO_INICIADO_ALEATORIO:
        posicoes_inimigos = []
        for _ in range(QUANTIDADE_INIMIGOS):
            x = random.randint(100, LARGURA - 160)
            y = random.randint(100, ALTURA // 2)
            posicoes_inimigos.append((x, y))
    else:
        posicoes_inimigos = []
        for i in range(QUANTIDADE_INIMIGOS):
            x = 100 + i * 150
            y = 100
            posicoes_inimigos.append((x, y))

def avaliar_individuo(individuo, geracao=None, mostrar_tela=False):
    tela = None
    if mostrar_tela:
        tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("IA Genética: Melhor Indivíduo")
    clock = pygame.time.Clock()

    jogador = JogadorGenetico(individuo.genes)

    inimigos = []
    for (x, y) in posicoes_inimigos:
        inimigos.append(Inimigo(x, y))

    jogada_acertos = [0] * NUM_JOGADAS
    tiros_para_remover = []
    abates = 0
    jogadas_usadas = NUM_JOGADAS

    for jogada in range(NUM_JOGADAS):
        if mostrar_tela:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            tela.fill(PRETO)

        jogador.mover()
        jogador.atirar()
        jogador.atualizar_tiros()

        for inimigo in inimigos:
            inimigo.mover(inimigos, jogador.tiros)

        novos_inimigos = []
        for inimigo in inimigos:
            rect_inimigo = pygame.Rect(inimigo.x, inimigo.y, 60, 40)
            atingido = False
            for tiro in jogador.tiros:
                if rect_inimigo.colliderect(tiro.rect):
                    tiros_para_remover.append(tiro)
                    abates += 1
                    jogada_acertos[jogada] = 1
                    atingido = True
                    break
            if not atingido:
                novos_inimigos.append(inimigo)
        inimigos = novos_inimigos

        jogador.tiros = [t for t in jogador.tiros if not t.fora_da_tela() and t not in tiros_para_remover]
        tiros_para_remover = []

        if mostrar_tela:
            jogador.desenhar(tela)
            for tiro in jogador.tiros:
                tiro.desenhar(tela)
            for inimigo in inimigos:
                inimigo.desenhar(tela)
            fonte = pygame.font.SysFont(None, 30)
            texto = fonte.render(
                f"Geração: {geracao}      Inimigos Derrotados: {abates}       Inimigos restantes: {len(inimigos)}       Jogada: {jogada+1} de {NUM_JOGADAS}  ",
                True, BRANCO)
            tela.blit(texto, (20, 10))
            pygame.display.flip()
            clock.tick(60)

        if len(inimigos) == 0:
            jogadas_usadas = jogada + 1
            break

    if mostrar_tela:
        pygame.time.wait(1000)

    individuo.fitness = calcular_fitness(abates, jogada_acertos, jogadas_usadas, individuo.genes)
    return individuo.fitness

def main():
    global nave_img, inimigo_img
    pygame.init()
    pygame.font.init()   
    nave_img = carrega_imagem("Fontes/media/tank.png", (80, 60))
    inimigo_img = carrega_imagem("Fontes/media/inimigo.png", (60, 40))

    inicializar_posicoes_inimigos()

    populacao = gerar_populacao_inicial()

    melhores = []
    log_fits = []
    medias = []

    with open("Fontes/Log_genetico.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["geracao", "melhor_genes", "fit", "media_fit"])

    for geracao in range(1, NUM_GERACOES + 1):
        for ind in populacao:
            avaliar_individuo(ind, geracao=geracao, mostrar_tela=False)
        populacao.sort(key=lambda ind: ind.fitness, reverse=True)
        melhores.append(populacao[0])
        log_fits.append(populacao[0].fitness)
        media_fit = sum([i.fitness for i in populacao]) / len(populacao)
        medias.append(media_fit)

        if geracao % GERACOES_VISUALIZACAO == 0:
            print(f"Melhor indivíduo -   Geração {geracao}, Fit: {populacao[0].fitness:.3f}")
            avaliar_individuo(populacao[0], geracao=geracao, mostrar_tela=True)

        with open("Fontes/log_genetico.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([geracao, populacao[0].genes, round(populacao[0].fitness, 3), round(media_fit, 3)])

        nova_pop = []
        if ELITISMO:
            nova_pop.extend([populacao[i] for i in range(N_MELHOR)])
        while len(nova_pop) < NUM_INDIVIDUOS:
            pai = selecao(populacao)
            mae = selecao(populacao)
            filho1, filho2 = crossover(pai, mae)
            mutacao(filho1)
            mutacao(filho2)
            nova_pop.append(filho1)
            if len(nova_pop) < NUM_INDIVIDUOS:
                nova_pop.append(filho2)
        populacao = nova_pop

    print("Finalizado! Melhor indivíduo geral - Fitness:", melhores[-1].fitness)
    salvar_melhor_individuo(melhores[-1])
    exibe_grafico(log_fits, medias)
    print("Melhor indivíduo salvo em 'melhor_individuo.json'.")

if __name__ == "__main__":
    main()
