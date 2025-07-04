import pygame
import sys

# Inicializa o Pygame
pygame.init()
pygame.mixer.init()

# Carrega o som do tiro
som_tiro = pygame.mixer.Sound('media\\lazer.wav')
som_atingido = pygame.mixer.Sound('media\\explosao.flac')

# Definições da tela
LARGURA = 1200
ALTURA = 800
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Space Invaders - Jogador")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)

# Carrega e redimensiona a imagem da nave
nave_img_original = pygame.image.load('media\\tank.png').convert_alpha()
nave_img = pygame.transform.scale(nave_img_original, (80, 60))  
nave_largura = nave_img.get_width()
nave_altura = nave_img.get_height()

# Jogador (posição inicial)
jogador_x = LARGURA // 2 - nave_largura // 2
jogador_y = ALTURA - nave_altura - 10
jogador_velocidade = 5

# Tiros
tiros = []
tiro_largura = 5
tiro_altura = 10
tiro_velocidade = 7
tiro_quantidade_maxima_simultanea = 1

# Controle de disparo
pode_atirar = True


# Inimigos
inimigo_largura = 60
inimigo_altura = 40
inimigo_velocidade = 3

# Carrega e redimensiona a imagem dos inimigos
inimigo_img_original = pygame.image.load('media\\inimigo.png').convert_alpha()
inimigo_img = pygame.transform.scale(inimigo_img_original, (inimigo_largura, inimigo_altura))

# Lista de inimigos: [x, y, direcao]
inimigos = [
    [150, 100, 1], 
    [300, 100, 1],  
    [450, 100, 1] ,  
    [600, 100, 1], 
    [750, 100, 1] 
]


# Loop principal do jogo
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    TELA.fill(PRETO)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Teclas pressionadas
    teclas = pygame.key.get_pressed()

    # Movimento
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
        tiro[0] = jogador_x + nave_largura // 2 - tiro_largura // 2  # Acompanha a nave lateralmente
    tiros = [tiro for tiro in tiros if tiro[1] > 0]

    # Movimento dos inimigos
    for inimigo in inimigos:
        inimigo[0] += inimigo_velocidade * inimigo[2]  # move na direção atual
        inimigo[1] += 0.3  # movimento vertical lento 

        # Verifica colisão com bordas
        if inimigo[0] <= 0 or inimigo[0] >= LARGURA - inimigo_largura:
            inimigo[2] *= -1  # inverte direção




    # Verifica colisões entre tiros e inimigos
    inimigos_ativos = []
    for inimigo in inimigos:
        inimigo_rect = pygame.Rect(inimigo[0], inimigo[1], inimigo_largura, inimigo_altura)
        atingido = False

        for tiro in tiros:
            tiro_rect = pygame.Rect(tiro[0], tiro[1], tiro_largura, tiro_altura)
            if inimigo_rect.colliderect(tiro_rect):
                tiros.remove(tiro)  # Remove o tiro
                atingido = True     # Marca o inimigo como atingido
                som_atingido.play()
                break               # Sai do loop, já que um tiro basta

        if not atingido:
            inimigos_ativos.append(inimigo)  # Mantém inimigo se não foi atingido

    inimigos = inimigos_ativos










    # Desenha jogador (imagem)
    TELA.blit(nave_img, (jogador_x, jogador_y))

    # Desenha tiros
    for tiro in tiros:
        pygame.draw.rect(TELA, BRANCO, (tiro[0], tiro[1], tiro_largura, tiro_altura))




    # Desenha inimigos
    for inimigo in inimigos:
        #pygame.draw.rect(TELA, VERMELHO, (inimigo[0], inimigo[1], inimigo_largura, inimigo_altura))
        TELA.blit(inimigo_img, (inimigo[0], inimigo[1]))

    # Atualiza a tela
    pygame.display.flip()
