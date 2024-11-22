import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def laplaciana(matriz_adjacencia):
    """
    Calcula a matriz laplaciana de um grafo dado sua matriz de adjacência.

    Parâmetros:
        matriz_adjacencia (numpy.ndarray): Matriz de adjacência do grafo.

    Retorno:
        numpy.ndarray: Matriz laplaciana do grafo.
    """
    sum = 0
    # Cria uma matriz diagonal zerada do mesmo tamanho da matriz de adjacência
    matrizDiagonal = np.zeros((matriz_adjacencia.shape))
    for index, line in enumerate(matriz_adjacencia):
        for value in line:
            sum += value  # Soma dos graus do nó (linhas da matriz)

        # Define o grau do nó na diagonal
        matrizDiagonal[index][index] = sum
        sum = 0  # Reinicia a soma para o próximo nó

    # Calcula a matriz laplaciana como matrizDiagonal - matriz_adjacencia
    matriz_laplaciana = matrizDiagonal - matriz_adjacencia

    return matriz_laplaciana


def Fiedler(matriz_adjacencia):
    """
    Calcula o autovetor de Fiedler, que corresponde ao segundo menor autovalor
    da matriz laplaciana de um grafo.

    Parâmetros:
        matriz_adjacencia (numpy.ndarray): Matriz de adjacência do grafo.

    Retorno:
        numpy.ndarray: Autovetor de Fiedler.
    """
    # Calcula a matriz laplaciana
    matriz_laplaciana = laplaciana(matriz_adjacencia)

    # Calcula autovalores e autovetores
    autovalores, autovetores = np.linalg.eig(matriz_laplaciana)

    # Ordena autovalores e autovetores com base nos autovalores
    indices_ordenados = np.argsort(autovalores)
    autovalores_ordenados = autovalores[indices_ordenados]
    autovetores_ordenados = autovetores[:, indices_ordenados]

    # O segundo menor autovalor é o de Fiedler, e o autovetor correspondente é retornado
    autovalor_de_Fiedler = autovalores_ordenados[1]
    autovetor_de_Fiedler = autovetores_ordenados[:, 1]

    # Imprime os valores do autovetor de Fiedler para depuração


    return autovetor_de_Fiedler


def cria_matriz_adjacencia(n_vertices, densidade=0.5):
    """
    Cria uma matriz de adjacência aleatória.

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

    return matriz


def plotar_grafo(matriz_de_adjacencia):
    """
    Plota o grafo com base na matriz de adjacência e destaca:
      - Nós em vermelho, verde e amarelo com base no autovetor de Fiedler.
      - Arestas entre nós com sinais opostos em azul.

    Parâmetros:
        matriz_de_adjacencia (numpy.ndarray): Matriz de adjacência do grafo.
    """
    grafo = nx.Graph()

    # Adiciona nós e arestas ao grafo
    n_vertices = matriz_de_adjacencia.shape[0]
    grafo.add_nodes_from(range(n_vertices))  # Garante que os nós são indexados de 0 a n-1
    for i in range(n_vertices):
        for j in range(n_vertices):
            if matriz_de_adjacencia[i, j] > 0:
                grafo.add_edge(i, j)

    # Calcula o autovetor de Fiedler
    autovetor_de_Fiedler = Fiedler(matriz_de_adjacencia)

    # Identifica o nó com menor valor absoluto no autovetor de Fiedler
    indice = min(range(len(autovetor_de_Fiedler)), key=lambda i: abs(autovetor_de_Fiedler[i]))
    print(f"Índice do nó destacado: {indice}")

    # Define cores para os nós com base nos valores do autovetor de Fiedler
    cores_nos = ['green' if value < 0 else 'yellow' for value in autovetor_de_Fiedler]
    cores_nos[indice] = 'red'  # Destaca o nó específico

    # Identificar arestas entre nós com sinais diferentes
    edge_colors = []
    for u, v in grafo.edges():
        if autovetor_de_Fiedler[u] * autovetor_de_Fiedler[v] < 0:  # Sinais diferentes
            edge_colors.append('gray')  # Cor de destaque
        else:
            edge_colors.append('gray')  # Cor padrão

    # Desenha o grafo
    pos = nx.spring_layout(grafo)  # Define o layout do grafo
    nx.draw(
        grafo, pos, with_labels=True, node_color=cores_nos, edge_color=edge_colors,
        node_size=500, font_size=10, width=4  # Aumenta largura das arestas
    )
    plt.title("Grafo com arestas destacadas")
    plt.show()


# Exemplo de uso: cria uma matriz de adjacência aleatória e plota o grafo
#matriz_adjacencia = cria_matriz_adjacencia(10, 0.3)  # 10 nós, densidade 30%
#plotar_grafo(matriz_adjacencia)


