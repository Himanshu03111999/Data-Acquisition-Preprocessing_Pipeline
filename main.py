import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.windows import from_bounds

# local modules
from src import DataIngestor, OpticalProcessor, SARProcessor
from src.utils import GeoUtils

# Fixing path for the PROJ database (Anaconda environment)
os.environ['PROJ_LIB'] = r"C:\Users\Syste\anaconda3\pkgs\proj-9.7.1-hd30e2cd_2\Library\share\proj"

def get_data_window(asset_url, bbox, target_shape=None):

    with rasterio.open(asset_url) as src:
        with WarpedVRT(src, crs="EPSG:4326") as vrt:
            window = from_bounds(*bbox, transform=vrt.transform)
            out_shape = target_shape if target_shape else None
            data = vrt.read(1, window=window, out_shape=out_shape)
            return data

def run_pipeline():
    bbox = [77.58, 12.96, 77.60, 12.98]
    date_range = "2025-12-01/2025-12-31"
    
    print("--- Phase 1: Ingestion ---")
    ingestor = DataIngestor()
    s2_item, s1_item = ingestor.search_data(bbox, date_range)
    
    if not s2_item or not s1_item:
        print("Data search failed.")
        return

    print("\n--- Phase 2: Optical (Sentinel-2) ---")
    red = get_data_window(s2_item.assets["B04"].href, bbox)
    nir = get_data_window(s2_item.assets["B08"].href, bbox)
    
    master_shape = red.shape
    scl = get_data_window(s2_item.assets["SCL"].href, bbox, target_shape=master_shape)

    opt_proc = OpticalProcessor()
    ndvi = opt_proc.calculate_ndvi(red, nir)
    mask = opt_proc.create_cloud_mask(scl)
    
    ndvi_clean = np.where(mask, ndvi, np.nan)
    print(f"NDVI Result -> Mean: {np.nanmean(ndvi_clean):.2f}")

    print("\n--- Phase 3: SAR (Sentinel-1) ---")
    # VV band synced to optical master shape
    vv = get_data_window(s1_item.assets["vv"].href, bbox, target_shape=master_shape)

    sar_proc = SARProcessor()
    filtered_vv = sar_proc.apply_lee_filter(vv)
    texture = sar_proc.generate_glcm_texture(filtered_vv)
    print(f"SAR Texture -> Mean: {texture.mean():.2f}")

    print("\n--- Phase 4: Generating High-Quality Plot ---")
    plt.style.use('dark_background') 
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), facecolor='#111111')
    
    # Plot NDVI 
    im1 = ax1.imshow(ndvi_clean, cmap='RdYlGn', vmin=-0.1, vmax=0.7)
    ax1.set_title('Vegetation Density (NDVI)', fontsize=16, color='white', fontweight='bold', pad=20)
    plt.colorbar(im1, ax=ax1, label="Index Value", fraction=0.046, pad=0.04)
    ax1.axis('off')

    # Plot SAR Texture 
    im2 = ax2.imshow(texture, cmap='inferno')
    ax2.set_title('Urban Surface Texture (SAR GLCM)', fontsize=16, color='white', fontweight='bold', pad=20)
    plt.colorbar(im2, ax=ax2, label="Texture Intensity", fraction=0.046, pad=0.04)
    ax2.axis('off')
    
    plt.suptitle(f"BENGALURU MULTI-SENSOR ANALYTICS (DEC 2025)\nLocation: {bbox}", 
                 fontsize=20, color='cyan', fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    
    # Save the visualization to the outputs folder
    plot_path = os.path.join("outputs", "pipeline_analytics.png")
    os.makedirs("outputs", exist_ok=True)
    plt.savefig(plot_path, dpi=300, facecolor='#111111')
    print(f"Enhanced Visualization saved to {plot_path}")

    print("\n--- Phase 5: Exporting Geospatial Results ---")
    
    # Using the modular save_geotiff method from utils
    GeoUtils.save_geotiff('ndvi_result.tif', ndvi_clean, bbox, master_shape)
    GeoUtils.save_geotiff('sar_texture.tif', texture, bbox, master_shape)
    

if __name__ == "__main__":
    run_pipeline()