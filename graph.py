import pygame
import random
import numpy as np
from module import *
import math

pygame.init()

# Vetor que aponta pra diferença entre o centro de massa e o centro da tela
# garantir que seja conexo 

WIDTH, HEIGHT = 1200,600

WHITE = (255,255,255)
BLACK = (27, 32, 33)
ORANGE = (255, 153, 20)
RED = (242, 27, 63)
BLUE = (8, 189, 189)
GREEN = (255, 183, 3)
YELLOW = (255, 188, 10)
PURPLE = (194, 0, 251)

NODESIZE = 15
LINEWIDTH = 3
TIME = 0.05
ZOOM = 1
NATURALSIZE = 100
STRINGFORCE = 0.2
REPULSIONFORCE = 600000

apply = True
betweenLine = False
numNodes = 10
prob = 0.25
camera = pygame.Vector2(0,0)

font = pygame.font.Font(None, NODESIZE*2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grapho")


class Node:
    def __init__(self, index):
        self.position = pygame.Vector2(random.randint(100,WIDTH-100), random.randint(100,HEIGHT-100))
        self.velocity = pygame.Vector2(0,0)
        self.inColor = BLUE
        self.outColor = WHITE
        self.number = index
        self.atractionForce = 0.01
        self.fiedlerValue = 0
        self.closeZero = False



def cria_matriz_adjacencia(n_vertices, densidade=0.5):
    """
    Cria uma matriz de adjacência aleatória e conexa.

    Parâmetros:
        n_vertices (int): Número de vértices do grafo.
        densidade (float): Probabilidade de uma aresta existir (0 a 1).

    Retorno:
        numpy.ndarray: Matriz de adjacência.
    """
    # Gera uma matriz aleatória de 0s e 1s com base na densidade
    matriz = np.random.rand(n_vertices, n_vertices) < densidade
    matriz = matriz.astype(int)  # Converte para 0s e 1s

    # Torna a matriz simétrica para grafos não-dirigidos
    matriz = np.triu(matriz, 1)  # Considera apenas a parte superior da matriz
    matriz += matriz.T  # Soma a parte transposta

    # Remove loops (arestas de um vértice para ele mesmo)
    np.fill_diagonal(matriz, 0)

    # Garante que o grafo seja conexo (com uma árvore geradora)
    for i in range(1, n_vertices):
        matriz[i-1, i] = 1
        matriz[i, i-1] = 1

    # Gera arestas adicionais com base na densidade, garantindo a simetria
    for i in range(n_vertices):
        for j in range(i+1, n_vertices):
            if np.random.rand() < densidade:
                matriz[i, j] = 1
                matriz[j, i] = 1

    return matriz



def updatePosition():
    for i, n1 in enumerate(nodes):
        nodesAcceleration = pygame.Vector2(0,0)
        for j, n2 in enumerate(nodes):
            if i == j:
                continue
            
            dif = n2.position - n1.position
            distance = dif.length()
            if distance > 0:

                dif = dif.normalize()

                if matriz_adjacencia[i][j] != 0:
                    string = (distance - NATURALSIZE)*STRINGFORCE
                else: 
                    string = 0

                repulsion = REPULSIONFORCE/(distance**2)

                nodesAcceleration += (-repulsion + string)*dif
        
        if apply:

            if 1 not in matriz_adjacencia[i]:
                nodesAcceleration += (pygame.Vector2(100, 100) - n1.position)*n1.atractionForce
            else: 

                if n1.closeZero :
                    nodesAcceleration += (pygame.Vector2(WIDTH//2, HEIGHT//2) - n1.position)*n1.atractionForce
                elif n1.fiedlerValue < 0:
                    nodesAcceleration += (pygame.Vector2(100, HEIGHT//2) - n1.position)*n1.atractionForce 
                elif n1.fiedlerValue > 0:
                    nodesAcceleration += (pygame.Vector2(WIDTH - 100, HEIGHT//2) - n1.position)*n1.atractionForce
                else:
                    nodesAcceleration += (pygame.Vector2(WIDTH//2, HEIGHT//2) - n1.position)*n1.atractionForce
        else:
            nodesAcceleration += (pygame.Vector2(WIDTH//2, HEIGHT//2) - n1.position)*0.5    
        n1.velocity = ( n1.velocity + nodesAcceleration) * TIME
        n1.position += n1.velocity


def draw(mousePosition):
    screen.fill(BLACK)

    for i, n1 in enumerate(nodes):
        for j, n2 in enumerate(nodes):
            if matriz_adjacencia[i][j] != 0:
                # Desenhe as arestas com zoom aplicado
                
                if betweenLine:
                    if n1.inColor == n2.inColor:
                        pygame.draw.line(screen, GREEN, n1.position * ZOOM, n2.position * ZOOM, int(LINEWIDTH * ZOOM))
                    else:
                        pygame.draw.line(screen, RED, n1.position * ZOOM, n2.position * ZOOM, int(LINEWIDTH * ZOOM))
                else:
                    pygame.draw.line(screen, GREEN, n1.position * ZOOM, n2.position * ZOOM, int(LINEWIDTH * ZOOM))

        
        
    for i, n1 in enumerate(nodes):
        # Ajusta o tamanho do nó com base no zoom
        scaled_position = n1.position * ZOOM 
        scaled_nodesize = NODESIZE * ZOOM 

        # Detecta interação com o mouse
        if (scaled_position - mousePosition).length() < scaled_nodesize + 10:
            n1.outColor = ORANGE
        else:
            n1.outColor = WHITE
        
        scaled_position -= camera

        pygame.draw.circle(screen, n1.outColor, scaled_position, int(2.5/2 * scaled_nodesize))
        pygame.draw.circle(screen, n1.inColor, scaled_position, int(scaled_nodesize))
        textNumber = font.render(f'{n1.number}', True, (0, 0, 0))
        screen.blit(textNumber, scaled_position - pygame.Vector2(scaled_nodesize // 2, scaled_nodesize // 2))


def checkClick(mousePosition, event, matriz_adjacencia):
    # Ajusta a posição do mouse para o zoom
    scaled_mouse_pos = pygame.Vector2(mousePosition) / ZOOM

    for i, n1 in enumerate(nodes):
        if (n1.position - scaled_mouse_pos).length() < NODESIZE + 10:
            if event.button == 1:
                for j in range(len(nodes)):
                    matriz_adjacencia[i][j] = 0
                    matriz_adjacencia[j][i] = 0
            if event.button == 3:
                matriz_adjacencia = np.delete(matriz_adjacencia, i, 0)
                matriz_adjacencia = np.delete(matriz_adjacencia, i, 1)
                nodes.remove(n1)
        
    return matriz_adjacencia

            
def removeNode(mousePosition):
    for i, n1 in enumerate(nodes):
        if (n1.position - mousePosition).length() < NODESIZE + 10:
            matriz_adjacencia = np.delete(matriz_adjacencia, i, 0)
            matriz_adjacencia = np.delete(matriz_adjacencia, i, 1)


def checkCollision():
    for n in nodes:
        if n.position.x < NODESIZE:
            n.position.x = NODESIZE
        elif n.position.x > WIDTH - NODESIZE:
            n.position.x = WIDTH - NODESIZE
        
        if n.position.y < NODESIZE:
            n.position.y = NODESIZE
        elif n.position.y > HEIGHT - NODESIZE:
            n.position.y = HEIGHT - NODESIZE


def update(mousePosition):
    updatePosition()
    draw(mousePosition)
    checkCollision()


def start(numNodes, prob):

    matriz_adjacencia = cria_matriz_adjacencia(numNodes, prob)  
    numNodes = len(matriz_adjacencia[0])

    nodes = []
    for i in range(numNodes):
        n = Node(i)
        nodes.append(n)

    return matriz_adjacencia, nodes

running = True

matriz_adjacencia, nodes  = start(numNodes, prob)


while running:

    mousePosition = pygame.mouse.get_pos()

    update(mousePosition)
    autovetorFiedler = Fiedler(matriz_adjacencia)
    for index, n in enumerate(nodes):
        n.fiedlerValue = autovetorFiedler[index]
        n.atractionForce = (math.exp(-(n.fiedlerValue*8)**2))
        n.closeZero = False
        if n.fiedlerValue < 0:
            n.inColor = PURPLE
        else:
            n.inColor = (99, 212, 113)
            #n.inColor = YELLOW
        #n.atractionForce = 0.05

    indice = min(range(len(autovetorFiedler)), key=lambda i: abs(autovetorFiedler[i]))
    print(indice, len(nodes))
    nodes[indice].inColor = RED     
    nodes[indice].closeZero = True
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            matriz_adjacencia = checkClick(mousePosition, event, matriz_adjacencia)
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                for n in nodes:
                    print(n.number, n.fiedlerValue, n.atractionForce)
                
                print(f"Índice do nó destacado: {nodes[indice].number}")
                print('\n\n')
            if keys[pygame.K_RIGHT]:  # Zoom In
                ZOOM += 0.05
            elif keys[pygame.K_LEFT]:  # Zoom Out
                ZOOM = max(0.5, ZOOM - 0.05)  # Impede zoom negativo ou muito pequeno

            if keys[pygame.K_w]:
                camera.y += 10
            elif keys[pygame.K_s]:
                camera.y -= 10
            if keys[pygame.K_p]:
                NODESIZE += 1
            elif keys[pygame.K_o]:
                NODESIZE -= 1
            if keys[pygame.K_i]:
                LINEWIDTH += 1
            elif keys[pygame.K_u]:
                LINEWIDTH -= 1
            if keys[pygame.K_t]:
                apply = not apply
            if keys[pygame.K_r]:
                matriz_adjacencia, nodes = start(numNodes, prob)
            if keys[pygame.K_d]:
                betweenLine = not betweenLine
    
    pygame.display.flip()
