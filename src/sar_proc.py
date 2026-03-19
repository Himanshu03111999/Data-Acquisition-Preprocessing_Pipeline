import numpy as np
from scipy.ndimage import uniform_filter
from skimage.feature import graycomatrix, graycoprops
from skimage import exposure

class SARProcessor:
    @staticmethod
    def apply_lee_filter(img, size=5):

        img = img.astype(np.float32)
        
        # Local mean and variance calculations
        img_mean = uniform_filter(img, (size, size))
        img_sqr_mean = uniform_filter(img**2, (size, size))
        img_variance = img_sqr_mean - img_mean**2

        overall_var = np.var(img)
        
        # Adding a small epsilon to avoid division by zero
        weights = img_variance / (img_variance + overall_var + 1e-10)
        
        return img_mean + weights * (img - img_mean)

    @staticmethod
    def generate_glcm_texture(sar_img, window_size=7):

        # Rescale intensities to 0-255 based on percentiles to handle SAR outliers
        p2, p98 = np.percentile(sar_img, (2, 98))
        img_8bit = exposure.rescale_intensity(
            sar_img, in_range=(p2, p98), out_range=(0, 255)
        ).astype(np.uint8)

        rows, cols = img_8bit.shape
        margin = window_size // 2
        texture_out = np.zeros_like(img_8bit, dtype=np.float32)

        for r in range(margin, rows - margin, 2):
            for c in range(margin, cols - margin, 2):
                win = img_8bit[r-margin : r+margin+1, c-margin : c+margin+1]
                
                # Compute GLCM and extract contrast
                glcm = graycomatrix(win, [1], [0], levels=256, symmetric=True, normed=True)
                texture_out[r, c] = graycoprops(glcm, 'contrast')[0, 0]
        
        return texture_out

if __name__ == "__main__":
    print("OpticalProcessor module initialized and ready.")