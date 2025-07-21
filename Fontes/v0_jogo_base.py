# space_invaders_ia.py
import pygame
import sys
import csv
import random
from pygame.locals import *
import matplotlib.pyplot as plt

# Inicialização
pygame.init()
LARGURA, ALTURA = 1200, 800
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Inteligence Invaders")

# Cores e constantes
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
FPS = 1000
TOTAL_PARTIDAS = 160

# Modos de comportamento
COMPORTAMENTO_INIMIGOS = "aleatorio"  # "aleatorio", "linear" ou "desviando"
MODO_JOGADOR = "manual"  # "linear", "aleatorio" ou "manual"

if MODO_JOGADOR == "manual":
    FPS = 100

QUANTIDADE_INIMIGOS = 4  # Quantidade de inimigos por rodada

# Carregamento de imagens
nave_img = pygame.transform.scale(pygame.image.load("Fontes/media/tank.png"), (80, 60))
inimigo_img = pygame.transform.scale(pygame.image.load("Fontes/media/inimigo.png"), (60, 40))

# Histórico para gráfico
historico_partidas = []
historico_jogador = []
historico_inimigo = []

def atualizar_grafico(partidas, jogador_vitorias, inimigo_vitorias):
    historico_partidas.append(partidas)
    historico_jogador.append(jogador_vitorias)
    historico_inimigo.append(inimigo_vitorias)

def exibe_grafico():
    plt.plot(historico_partidas, historico_jogador, label='Vitórias Jogador')
    plt.plot(historico_partidas, historico_inimigo, label='Vitórias Inimigo')
    plt.xlabel("Partidas")
    plt.ylabel("Vitórias")
    plt.legend()
    plt.title("Resultado Final")
    plt.show()

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


class Entidade:
    def __init__(self, x, y, imagem):
        self.x = x
        self.y = y
        self.imagem = imagem

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x, self.y))


class Jogador(Entidade):
    def __init__(self):
        super().__init__(LARGURA // 2 - 40, ALTURA - 70, nave_img)
        self.direcao = 1
        self.velocidade = 5
        self.tiros = []
        self.tecla_espaco_liberada = True
        self.mov_restantes = random.randint(30, 100)
        self.atirar_restante = random.randint(20, 100)

    def mover(self):
        if MODO_JOGADOR == "linear":
            self.x += self.velocidade * self.direcao
            if self.x <= 0 or self.x >= LARGURA - self.imagem.get_width():
                self.direcao *= -1
        elif MODO_JOGADOR == "manual":
            teclas = pygame.key.get_pressed()
            if teclas[K_LEFT]:
                self.x -= self.velocidade
            if teclas[K_RIGHT]:
                self.x += self.velocidade
            self.x = max(0, min(LARGURA - self.imagem.get_width(), self.x))
        elif MODO_JOGADOR == "aleatorio":
            if self.mov_restantes <= 0:
                self.direcao = random.choice([-1, 0, 1])
                self.mov_restantes = random.randint(20, 60)
            self.x += self.direcao * self.velocidade
            self.x = max(0, min(LARGURA - self.imagem.get_width(), self.x))
            self.mov_restantes -= 1

    def atirar(self):
        if MODO_JOGADOR == "linear":
            if len(self.tiros) == 0:
                self.tiros.append(Tiro(self))
        elif MODO_JOGADOR == "manual":
            teclas = pygame.key.get_pressed()
            if teclas[K_SPACE] and self.tecla_espaco_liberada:
                if len(self.tiros) == 0:
                    self.tiros.append(Tiro(self))
                self.tecla_espaco_liberada = False
            if not teclas[K_SPACE]:
                self.tecla_espaco_liberada = True
        elif MODO_JOGADOR == "aleatorio":
            if self.atirar_restante <= 0:
                if len(self.tiros) == 0:
                    self.tiros.append(Tiro(self))
                self.atirar_restante = random.randint(30, 120)
            else:
                self.atirar_restante -= 1

    def atualizar_tiros(self):
        for tiro in self.tiros:
            tiro.mover()
        self.tiros = [t for t in self.tiros if not t.fora_da_tela()]


class Inimigo(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, inimigo_img)
        self.direcao = 1
        self.movimentos_restantes = random.randint(30, 100)
        self.descer_restante = random.randint(30, 100)
        self.velocidade_vertical = random.uniform(0.2, 1.0)

    def mover(self, outros_inimigos, tiros):
        nova_x = self.x
        nova_y = self.y

        if COMPORTAMENTO_INIMIGOS == "desviando":
            perigo = False
            for tiro in tiros:
                if abs(self.x + 30 - tiro.rect.centerx) < 40 and self.y < tiro.rect.y < self.y + 150:
                    perigo = True
                    break
            if perigo:
                self.direcao = -self.direcao
            nova_x += self.direcao * 3
            if self.descer_restante <= 0:
                self.velocidade_vertical = random.uniform(0.2, 1.0)
                self.descer_restante = random.randint(30, 100)
            nova_y += self.velocidade_vertical
            self.descer_restante -= 1
        elif COMPORTAMENTO_INIMIGOS == "aleatorio":
            if self.movimentos_restantes <= 0:
                self.direcao = random.choice([-1, 1])
                self.movimentos_restantes = random.randint(30, 100)
            nova_x += self.direcao * 3
            if self.descer_restante <= 0:
                self.velocidade_vertical = random.uniform(0.2, 1.0)
                self.descer_restante = random.randint(30, 100)
            nova_y += self.velocidade_vertical
            self.descer_restante -= 1
            self.movimentos_restantes -= 1
        else:  # linear
            nova_x += 3 * self.direcao
            nova_y += 0.3

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


class Jogo:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.jogador = Jogador()
        self.partidas = 0
        self.jogador_vitorias = 0
        self.inimigo_vitorias = 0
        self.logs = []
        self.inicializar_inimigos()

    def inicializar_inimigos(self):
        self.inimigos = []
        ocupados = []
        for x in range(100, LARGURA - 100, 80):
            y = 100
            pos_valida = True
            novo_rect = pygame.Rect(x, y, 60, 40)
            for rect in ocupados:
                if novo_rect.colliderect(rect):
                    pos_valida = False
                    break
            if pos_valida:
                self.inimigos.append(Inimigo(x, y))
                ocupados.append(novo_rect)
            if len(self.inimigos) >= QUANTIDADE_INIMIGOS:
                break

    def detectar_colisoes(self):
        novos_inimigos = []
        for inimigo in self.inimigos:
            rect_inimigo = pygame.Rect(inimigo.x, inimigo.y, 60, 40)
            atingido = False
            for tiro in self.jogador.tiros:
                if rect_inimigo.colliderect(tiro.rect):
                    self.jogador.tiros.remove(tiro)
                    atingido = True
                    break
            if not atingido:
                novos_inimigos.append(inimigo)
        self.inimigos = novos_inimigos

    def checar_fim_rodada(self):
        jogador_rect = pygame.Rect(self.jogador.x, self.jogador.y, self.jogador.imagem.get_width(), self.jogador.imagem.get_height())
        for inimigo in self.inimigos:
            inimigo_rect = pygame.Rect(inimigo.x, inimigo.y, 60, 40)
            if inimigo.y >= ALTURA or inimigo_rect.colliderect(jogador_rect):
                self.inimigo_vitorias += 1
                self.logs.append((self.partidas + 1, "Inimigo"))
                return True
        if not self.inimigos:
            self.jogador_vitorias += 1
            self.logs.append((self.partidas + 1, "Jogador"))
            return True
        return False

    def salvar_logs(self):
        with open("log_resultados.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Partida", "Vencedor"])
            writer.writerows(self.logs)

    def rodar(self):
        while self.partidas < TOTAL_PARTIDAS:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.salvar_logs()
                    pygame.quit()
                    sys.exit()

            TELA.fill(PRETO)

            self.jogador.mover()
            self.jogador.atirar()
            self.jogador.atualizar_tiros()

            for inimigo in self.inimigos:
                inimigo.mover(self.inimigos, self.jogador.tiros)

            self.detectar_colisoes()

            if self.checar_fim_rodada():
                self.partidas += 1
                atualizar_grafico(self.partidas, self.jogador_vitorias, self.inimigo_vitorias)
                self.inicializar_inimigos()

            self.jogador.desenhar(TELA)
            for tiro in self.jogador.tiros:
                tiro.desenhar(TELA)
            for inimigo in self.inimigos:
                inimigo.desenhar(TELA)

            fonte = pygame.font.SysFont(None, 30)
            texto = fonte.render(f"Partidas: {self.partidas}  Jogador: {self.jogador_vitorias}  Inimigo: {self.inimigo_vitorias}", True, BRANCO)
            TELA.blit(texto, (20, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        self.salvar_logs()
        pygame.quit()
        exibe_grafico()
        print("Simulação concluída. Resultados salvos em log_resultados.csv")


if __name__ == "__main__":
    jogo = Jogo()
    jogo.rodar()
