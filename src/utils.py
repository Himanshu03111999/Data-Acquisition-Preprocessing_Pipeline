import os
import numpy as np
import rasterio
from rasterio.transform import from_bounds as transform_from_bounds

class GeoUtils:
    @staticmethod
    def save_geotiff(filename, data, bbox, shape, crs="EPSG:4326"):
       
        h, w = shape
        new_transform = transform_from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], w, h)

        meta = {
            'driver': 'GTiff',
            'height': h,
            'width': w,
            'count': 1,
            'dtype': 'float32',
            'crs': crs,
            'transform': new_transform,
            'nodata': np.nan,
            'compress': 'lzw'
        }

        output_dir = "outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        path = os.path.join(output_dir, filename)
        
        with rasterio.open(path, 'w', **meta) as dst:
            dst.write(data.astype('float32'), 1)
        
        return path

