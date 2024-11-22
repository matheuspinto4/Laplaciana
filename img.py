import numpy as np
import cv2
import scipy.sparse.csgraph as csgraph
from scipy.linalg import eigh

# Defina o valor de sigma
sigma = 5

# Carregar e pré-processar a imagem
image = cv2.imread("foto.jpg", cv2.IMREAD_GRAYSCALE)
original_height, original_width = image.shape
image = cv2.resize(image, (100, 100))  # Reduz a resolução para simplificar

# Criar o grafo da imagem - cada pixel é um nó
height, width = image.shape
N = height * width
pixels = image.flatten()  # Vetorizar a imagem

# Matriz de similaridade (usando a diferença de intensidade entre pixels)
similarity_matrix = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        intensity_diff = abs(int(pixels[i]) - int(pixels[j]))
        similarity_matrix[i, j] = np.exp(-intensity_diff**2 / (2 * sigma**2))
        similarity_matrix[j, i] = similarity_matrix[i, j]

# Construir a matriz Laplaciana
laplacian_matrix = csgraph.laplacian(similarity_matrix, normed=True)

# Decompor a matriz laplaciana
vals, vecs = eigh(laplacian_matrix, subset_by_index=[0, 1])

# Usar os autovetores para fazer o corte espectral
segmented_image = (vecs[:, 1] > 0).reshape(height, width)

# Esticar a imagem segmentada para as dimensões originais
segmented_image_stretched = cv2.resize(segmented_image.astype(np.float32), (original_width, original_height), interpolation=cv2.INTER_LINEAR)

# Redimensionar a imagem original para ter a mesma altura que a imagem segmentada
image_resized = cv2.resize(image, (segmented_image_stretched.shape[1], segmented_image_stretched.shape[0]))

# Agora você pode combinar as imagens
combined_image = np.hstack((image_resized, segmented_image_stretched.astype(np.uint8) * 255))

# Exibir a imagem combinada
cv2.imshow("Comparação: Imagem Original vs Segmentada", combined_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Salvar a imagem segmentada esticada
cv2.imwrite("imagem_segmentada.jpg", segmented_image_stretched.astype(np.uint8) * 255)
