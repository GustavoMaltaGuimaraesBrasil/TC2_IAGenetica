import pygame
import sys
import random

# Inicializa o Pygame
pygame.init()
pygame.mixer.init()

# Sons
som_tiro = pygame.mixer.Sound('media\\lazer.wav')
som_atingido = pygame.mixer.Sound('media\\explosao.flac')

# Tela
LARGURA = 1200
ALTURA = 800
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Space Invaders IA Genética Aprimorada")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)

# Fonte
fonte = pygame.font.SysFont('arial', 30)

# Jogador
nave_img_original = pygame.image.load('media\\tank.png').convert_alpha()
nave_img = pygame.transform.scale(nave_img_original, (80, 60))
nave_largura = nave_img.get_width()
nave_altura = nave_img.get_height()

jogador_x = LARGURA // 2 - nave_largura // 2
jogador_y = ALTURA - nave_altura - 10
jogador_velocidade = 5

# Tiros
tiros = []
tiro_largura = 5
tiro_altura = 10
tiro_velocidade = 7
tiro_quantidade_maxima_simultanea = 1
pode_atirar = True

# Inimigos
inimigo_largura = 60
inimigo_altura = 40
inimigo_img_original = pygame.image.load('media\\inimigo.png').convert_alpha()
inimigo_img = pygame.transform.scale(inimigo_img_original, (inimigo_largura, inimigo_altura))

# IA Genética - parâmetros fixos
TAMANHO_POPULACAO = 4
TAXA_MUTACAO = 0.2
VELOCIDADE_X_MIN = 2
VELOCIDADE_X_MAX = 5
VELOCIDADE_Y_MIN = 0.3
VELOCIDADE_Y_MAX = 0.8

# Histórico para genética
historico_inimigos = []

# Cria nova geração
def nova_geracao(historico):
    nova = []

    if not historico:
        for _ in range(TAMANHO_POPULACAO):
            x = random.randint(100, LARGURA - 100)
            y = random.randint(50, 150)
            direcao = random.choice([-1, 1])
            velocidade_x = random.uniform(VELOCIDADE_X_MIN, VELOCIDADE_X_MAX)
            velocidade_y = random.uniform(VELOCIDADE_Y_MIN, VELOCIDADE_Y_MAX)
            nova.append([x, y, direcao, velocidade_x, velocidade_y, y])
        return nova

    historico.sort(key=lambda inimigo: inimigo[5], reverse=True)
    pais = historico[:2]

    for _ in range(TAMANHO_POPULACAO):
        pai = random.choice(pais)

        velocidade_x = pai[3] + (random.uniform(-0.5, 0.5) if random.random() < TAXA_MUTACAO else 0)
        velocidade_y = pai[4] + (random.uniform(-0.1, 0.1) if random.random() < TAXA_MUTACAO else 0)

        velocidade_x = max(VELOCIDADE_X_MIN, min(velocidade_x, VELOCIDADE_X_MAX))
        velocidade_y = max(VELOCIDADE_Y_MIN, min(velocidade_y, VELOCIDADE_Y_MAX))

        x = random.randint(100, LARGURA - 100)
        y = random.randint(50, 150)
        direcao = random.choice([-1, 1])

        nova.append([x, y, direcao, velocidade_x, velocidade_y, y])

    return nova


# Primeira geração
numero_geracao = 1
inimigos = nova_geracao([])

# Loop principal
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    TELA.fill(PRETO)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_LEFT] and jogador_x > 0:
        jogador_x -= jogador_velocidade
    if teclas[pygame.K_RIGHT] and jogador_x < LARGURA - nave_largura:
        jogador_x += jogador_velocidade

    # Disparo
    if teclas[pygame.K_SPACE]:
        if pode_atirar and len(tiros) < tiro_quantidade_maxima_simultanea:
            tiro_x = jogador_x + nave_largura // 2 - tiro_largura // 2
            tiro_y = jogador_y
            tiros.append([tiro_x, tiro_y])
            som_tiro.play()
            pode_atirar = False
    else:
        pode_atirar = True

    # Atualiza tiros
    for tiro in tiros:
        tiro[1] -= tiro_velocidade
        tiro[0] = jogador_x + nave_largura // 2 - tiro_largura // 2
    tiros = [tiro for tiro in tiros if tiro[1] > 0]

    # Movimento dos inimigos
    for inimigo in inimigos:
        # Desvio mais inteligente
        desviando = False
        for tiro in tiros:
            distancia_x = abs((inimigo[0] + inimigo_largura/2) - (tiro[0] + tiro_largura/2))
            distancia_y = inimigo[1] - tiro[1]

            if distancia_x < 100 and 0 < distancia_y < 200:
                if (inimigo[0] + inimigo_largura/2) < (tiro[0] + tiro_largura/2):
                    inimigo[2] = -1
                else:
                    inimigo[2] = 1
                desviando = True
                break

        # Movimento lateral constante com chance de mudar de lado aleatoriamente
        if not desviando and random.random() < 0.01:
            inimigo[2] *= -1  # muda de lado por decisão autônoma

        inimigo[0] += inimigo[3] * inimigo[2]
        inimigo[1] += inimigo[4]
        inimigo[5] = max(inimigo[5], inimigo[1])

        # Bordas
        if inimigo[0] <= 0:
            inimigo[0] = 0
            inimigo[2] = 1
        if inimigo[0] >= LARGURA - inimigo_largura:
            inimigo[0] = LARGURA - inimigo_largura
            inimigo[2] = -1

    # Verifica colisões tiros vs inimigos
    inimigos_ativos = []
    for inimigo in inimigos:
        inimigo_rect = pygame.Rect(inimigo[0], inimigo[1], inimigo_largura, inimigo_altura)
        atingido = False

        for tiro in tiros:
            tiro_rect = pygame.Rect(tiro[0], tiro[1], tiro_largura, tiro_altura)
            if inimigo_rect.colliderect(tiro_rect):
                tiros.remove(tiro)
                atingido = True
                som_atingido.play()
                break

        if not atingido:
            inimigos_ativos.append(inimigo)
        else:
            historico_inimigos.append(inimigo)

    inimigos = inimigos_ativos

    # Verifica derrota
    perdeu = False
    for inimigo in inimigos:
        if inimigo[1] + inimigo_altura >= jogador_y:
            perdeu = True
            break

    if perdeu:
        texto = fonte.render(f'Game Over! Eles venceram na geração {numero_geracao}.', True, VERMELHO)
        TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    # Nova geração se matou todos
    if not inimigos:
        numero_geracao += 1
        inimigos = nova_geracao(historico_inimigos)
        historico_inimigos = []

    # Desenha jogador
    TELA.blit(nave_img, (jogador_x, jogador_y))

    # Desenha tiros
    for tiro in tiros:
        pygame.draw.rect(TELA, BRANCO, (tiro[0], tiro[1], tiro_largura, tiro_altura))

    # Desenha inimigos
    for inimigo in inimigos:
        TELA.blit(inimigo_img, (inimigo[0], inimigo[1]))

    # Placar de geração
    texto_geracao = fonte.render(f'Geração: {numero_geracao}', True, BRANCO)
    TELA.blit(texto_geracao, (10, 10))

    # Atualiza tela
    pygame.display.flip()
