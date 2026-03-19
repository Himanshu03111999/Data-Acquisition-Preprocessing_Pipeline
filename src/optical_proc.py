import numpy as np

class OpticalProcessor:
    @staticmethod
    def calculate_ndvi(red, nir):

        r = red.astype(np.float32)
        n = nir.astype(np.float32)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (n - r) / (n + r)
            ndvi = np.nan_to_num(ndvi, nan=0.0) 
            
        return ndvi

    @staticmethod
    def create_cloud_mask(scl):

        # Values we want to remove
        unwanted_pixels = [3, 8, 9, 10]
        
        # Create a boolean mask where True means the pixel is clear
        is_clear = ~np.isin(scl, unwanted_pixels)
        
        return is_clear

if __name__ == "__main__":
    print("OpticalProcessor module initialized and ready.")