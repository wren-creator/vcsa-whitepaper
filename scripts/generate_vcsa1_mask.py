import gdspy
import numpy as np

# 1. Initialize a new GDSII Library for Project VCSA-1
# Units are in micrometers (microns). 14.14 mm = 14140 microns
lib = gdspy.GdsLibrary('VCSA_1_MASTER_TEMPLATE', unit=1e-6, precision=1e-9)
cell = lib.new_cell('VCSA1_DIE_MAIN')

# 2. Define the Lithographic Layer Mapping (Foundry Spec)
# In 3D integration, layers are separated by distinct integer IDs
LAYER_DIE_OUTLINE   = 0   # Physical scribe line / boundary
LAYER_L1_STORAGE    = 10  # Base Silicon: 1 GB SRAM Matrix
LAYER_L2_ROUTING    = 20  # Middle Silicon: L2A/L2B Arbitration Interconnect
LAYER_CNT_VIAS      = 30  # Inter-layer: Carbon Nanotube Contact Pads
LAYER_L3_COMPUTE    = 40  # Top Silicon: Matrix Cores / ALUs
LAYER_FIDUCIALS     = 99  # Lithography alignment marks

# 3. Create the Main Die Outline (14.14mm x 14.14mm)
die_size = 14140.0
die_outline = gdspy.Rectangle((0, 0), (die_size, die_size), layer=LAYER_DIE_OUTLINE)
cell.add(die_outline)

# 4. Inject Photolithographic Alignment Marks (Fiducials) at Corners
# These crosshairs allow the fab's stepper lasers to align the masks perfectly.
def add_alignment_mark(x, y):
    cross_h = gdspy.Rectangle((x - 100, y - 10), (x + 100, y + 10), layer=LAYER_FIDUCIALS)
    cross_v = gdspy.Rectangle((x - 10, y - 100), (x + 10, y + 100), layer=LAYER_FIDUCIALS)
    cell.add(cross_h)
    cell.add(cross_v)

# Place fiducials 200 microns inside each corner
margin = 200.0
add_alignment_mark(margin, margin)
add_alignment_mark(die_size - margin, margin)
add_alignment_mark(margin, die_size - margin)
add_alignment_mark(die_size - margin, die_size - margin)

# 5. Define the 1 GB L1 Storage Ocean: 4 Dense Quadrants
# Leaving central avenues for main power rails and global clocks
quad_size = 6500.0
gap = 740.0 # Center spacing for routing channels

quad_coords = [
    ((margin, margin), (margin + quad_size, margin + quad_size)), # Bottom Left
    ((margin + quad_size + gap, margin), (die_size - margin, margin + quad_size)), # Bottom Right
    ((margin, margin + quad_size + gap), (margin + quad_size, die_size - margin)), # Top Left
    ((margin + quad_size + gap, margin + quad_size + gap), (die_size - margin, die_size - margin)) # Top Right
]

for i, (p1, p2) in enumerate(quad_coords):
    quadrant = gdspy.Rectangle(p1, p2, layer=LAYER_L1_STORAGE)
    cell.add(quadrant)
    
    # 6. Template the Vertical CNT Bus Landing Zones inside each quadrant
    # Creating a grid of contact zones where the nanotubes drop down to meet the memory
    for cx in np.linspace(p1[0] + 500, p2[0] - 500, 5):
        for cy in np.linspace(p1[1] + 500, p2[1] - 500, 5):
            # Carbon Nanotube Bundle Array Contact Pad (50x50 microns cluster)
            cnt_pad = gdspy.Rectangle((cx - 25, cy - 25), (cx + 25, cy + 25), layer=LAYER_CNT_VIAS)
            cell.add(cnt_pad)

# 7. Template the Layer 3 Top-Floor Matrix Cores (Tiled Compute)
# 4 powerful symmetric execution engines sitting on the top floor
core_size = 5000.0
core_offset = 1200.0

core_coords = [
    (core_offset, core_offset),
    (die_size - core_offset - core_size, core_offset),
    (core_offset, die_size - core_offset - core_size),
    (die_size - core_offset - core_size, die_size - core_offset - core_size)
]

for (cx, cy) in core_coords:
    matrix_core = gdspy.Rectangle((cx, cy), (cx + core_size, cy + core_size), layer=LAYER_L3_COMPUTE)
    cell.add(matrix_core)

# 8. Save the layout template to a production-standard GDSII file
lib.write_gds('vcsa1_master_template.gds')

print("Success! 'vcsa1_master_template.gds' has been generated.")
print("This file can be loaded directly into industrial layout viewers like KLayout.")
