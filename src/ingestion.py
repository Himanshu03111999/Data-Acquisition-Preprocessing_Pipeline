import pystac_client
import planetary_computer
from datetime import datetime

class DataIngestor:
    def __init__(self):
        # Setting up the Microsoft Planetary Computer catalog access
        self.stac_api_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
        self.catalog = pystac_client.Client.open(
            self.stac_api_url,
            modifier=planetary_computer.sign_inplace,
        )

    def search_data(self, area_of_interest, time_window):        
        
        #Search for Sentinel-2 L2A (Optical)
        optical_search = self.catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=area_of_interest,
            datetime=time_window,
            query={"eo:cloud_cover": {"lt": 10}} 
        )
        s2_scenes = optical_search.item_collection()

        #Search for Sentinel-1 GRD (SAR)
        sar_search = self.catalog.search(
            collections=["sentinel-1-grd"],
            bbox=area_of_interest,
            datetime=time_window,
        )
        s1_scenes = sar_search.item_collection()

        print(f"Results: {len(s2_scenes)} Sentinel-2 items and {len(s1_scenes)} Sentinel-1 items found.")
        
        # We need at least one of each to proceed with multi-sensor fusion
        if len(s2_scenes) > 0 and len(s1_scenes) > 0:
            return s2_scenes[0], s1_scenes[0]
        
        print("No matching overlapping data found.")
        return None, None

if __name__ == "__main__":
    bengaluru_bbox = [77.45, 12.75, 77.65, 12.95]
    december_window = "2025-12-01/2025-12-31"
    
    ingestor = DataIngestor()
    s2_item, s1_item = ingestor.search_data(bengaluru_bbox, december_window)
    
    if s2_item and s1_item:
        print(f"Match Found!")
        print(f"S2 ID: {s2_item.id}")
        print(f"S1 ID: {s1_item.id}")