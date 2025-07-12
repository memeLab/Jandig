import numpy as np
from PIL import Image
import sys

def read_patt_file(filepath):
    matrices = []
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    idx = 0
    for _ in range(3):  # Only first 3 matrices (R, G, B)
        matrix = []
        for _ in range(16):
            row = [int(val) for val in lines[idx].split()]
            matrix.append(row)
            idx += 1
        matrices.append(np.array(matrix, dtype=np.uint8))
    return matrices  # [R, G, B]

def create_image_from_matrices(matrices, output_path):
    # Stack matrices into an RGB image
    img_array = np.stack(matrices, axis=-1)
    img = Image.fromarray(img_array, 'RGB')
    img.save(output_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python patt_to_image.py <input.patt> <output.png>")
        sys.exit(1)
    patt_file = sys.argv[1]
    output_image = sys.argv[2]
    matrices = read_patt_file(patt_file)
    create_image_from_matrices(matrices, output_image)
    print(f"Image saved to {output_image}")