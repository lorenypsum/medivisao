# backend/processamento.py
import cv2
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import tensorflow as tf


class Resize(BaseEstimator, TransformerMixin):
    def __init__(self, size=(128, 128)):
        self.size = size

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [cv2.resize(img, self.size) for img in X]


class Normalize(BaseEstimator, TransformerMixin):
    def __init__(self, scaling="minmax"):
        self.scaling = scaling
        self.mean = None
        self.std = None

    def fit(self, X):
        X = np.array(X)
        if self.scaling == "meanstd":
            if X.ndim == 4:
                self.mean = np.mean(X, axis=(0, 1, 2), keepdims=True)
                self.std = np.std(X, axis=(0, 1, 2), keepdims=True)
        return self

    def transform(self, X):
        X = np.array(X, dtype=np.float32)
        if self.scaling == "minmax":
            return (X - np.min(X)) / (np.max(X) - np.min(X) + 1e-8)
        elif self.scaling == "meanstd":
            return (X - self.mean) / (self.std + 1e-8)
        else:
            raise ValueError("Escalonamento inválido")


class GaussianBlur(BaseEstimator, TransformerMixin):
    def __init__(self, ksize=(5, 5), sigma=0):
        self.ksize = ksize
        self.sigma = sigma

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [cv2.GaussianBlur(img, self.ksize, self.sigma) for img in X]


class CLAHE_Color(BaseEstimator, TransformerMixin):
    def __init__(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        processed_images = []
        for img in X:
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(
                clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size
            )
            cl = clahe.apply(l)
            merged = cv2.merge((cl, a, b))
            final = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
            processed_images.append(final)
        return processed_images


class OtsuThreshold(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        binarized = []
        for img in X:
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            binarized.append(binary)
        return binarized


class HistogramEqualization(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        equalized = []
        for img in X:
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            equalized.append(cv2.equalizeHist(img))
        return equalized


class MorphologicalTransform(BaseEstimator, TransformerMixin):
    def __init__(self, operation="dilate", kernel_size=(5, 5)):
        self.operation = operation
        self.kernel_size = kernel_size

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, self.kernel_size)
        transformed_images = []
        for img in X:
            if self.operation == "dilate":
                transformed_images.append(cv2.dilate(img, kernel))
            elif self.operation == "erode":
                transformed_images.append(cv2.erode(img, kernel))
            elif self.operation == "open":
                transformed_images.append(cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel))
            elif self.operation == "close":
                transformed_images.append(
                    cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
                )
            else:
                raise ValueError("Operação morfológica inválida")
        return transformed_images


class MorphologicalOperations(BaseEstimator, TransformerMixin):
    def __init__(self, operation="opening", kernel_size=(5, 5)):
        self.operation = operation
        self.kernel_size = kernel_size

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, self.kernel_size)
        transformed_images = []
        for img in X:
            if self.operation == "opening":
                transformed_images.append(cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel))
            elif self.operation == "closing":
                transformed_images.append(
                    cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
                )
            else:
                raise ValueError("Operação morfológica inválida")
        return transformed_images


class EdgeDetection(BaseEstimator, TransformerMixin):
    def __init__(self, method="canny", low_threshold=100, high_threshold=200):
        self.method = method
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        edge_detected_images = []
        for img in X:
            if self.method == "canny":
                edges = cv2.Canny(img, self.low_threshold, self.high_threshold)
            elif self.method == "sobel":
                sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
                sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)
                edges = np.sqrt(sobel_x**2 + sobel_y**2)
            else:
                raise ValueError("Método de detecção de bordas inválido")
            edge_detected_images.append(edges)
        return edge_detected_images


class Watershed(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        watershed_images = []
        for img in X:
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img

            # Apply Otsu's thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Noise removal using morphological operations
            kernel = np.ones((3, 3), np.uint8)
            opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

            # Sure background area
            sure_bg = cv2.dilate(opening, kernel, iterations=3)

            # Finding sure foreground area
            dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
            _, sure_fg = cv2.threshold(
                dist_transform, 0.7 * dist_transform.max(), 255, 0
            )

            # Finding unknown region
            sure_fg = np.uint8(sure_fg)
            unknown = cv2.subtract(sure_bg, sure_fg)

            # Marker labelling
            _, markers = cv2.connectedComponents(sure_fg)

            # Add one to all labels so that sure background is not 0 but 1
            markers = markers + 1

            # Mark the unknown region with zero
            markers[unknown == 255] = 0

            # Apply watershed
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if len(img.shape) == 2 else img
            markers = cv2.watershed(img, markers)
            img[markers == -1] = [255, 0, 0]  # Mark boundaries in red

            watershed_images.append(img)

        return watershed_images
