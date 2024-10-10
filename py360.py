#!/usr/bin/env python

import numpy as np
from PIL import Image
import py360convert
import os

def convert_equirectangular_to_cubemap(input_image_path, output_folder, face_width, mode='bilinear'):
    """Convert equirectangular image to cubemap and save each face in a folder."""
    # Read input image
    img = np.array(Image.open(input_image_path))

    # Convert to cubemap
    py360convert.e2c(img, face_w=face_width, mode=mode, output_dir=output_folder)  # 传递输出文件夹


def convert_cubemap_to_equirectangular(input_folder, output_image_path, output_height, output_width, mode='bilinear'):
    """Convert cubemap images from a directory to equirectangular image."""
    # 读取立方体图像
    face_names = ['front', 'right', 'back', 'left', 'up', 'down']
    cube_faces = []
    
    for face_name in face_names:
        face_path = os.path.join(input_folder, f"{face_name}.png")
        img = np.array(Image.open(face_path))
        cube_faces.append(img)
    
    # 假设每个面是正方形
    face_height, face_width, channels = cube_faces[0].shape

    # 对 U 图像进行右旋转90度
    # up = np.rot90(cube_faces[4], k=-1)  # 右旋转90度
    up = np.flip(cube_faces[4], axis=0)  # 上下镜像
    # 对 R 图像进行左右镜像
    right = np.flip(cube_faces[1], axis=1)  # 左右镜像
    # 对 B 图像进行左右镜像
    back = np.flip(cube_faces[2], axis=1)  # 左右镜像

    # 创建一个空的十字架格式的立方体图像
    cross_image = np.zeros((3 * face_height, 4 * face_width, channels), dtype=cube_faces[0].dtype)

    # 将每个面放入合适的位置
    cross_image[face_height:2*face_height, face_width:2*face_width] = cube_faces[0]  # F
    cross_image[face_height:2*face_height, 2*face_width:3*face_width] = right  # R
    cross_image[face_height:2*face_height, 3*face_width:4*face_width] = back # B
    cross_image[face_height:2*face_height, 0:face_width] = cube_faces[3]  # L
    cross_image[0:face_height, face_width:2*face_width] = up  # U
    cross_image[2*face_height:3*face_height, face_width:2*face_width] = cube_faces[5]  # D

    # 保存拼接后的十字架图像以进行调试
    debug_cross_image_path = os.path.join(input_folder, 'debug_cross_image.png')
    Image.fromarray(cross_image.astype(np.uint8)).save(debug_cross_image_path)
    print(f"Debug cross image saved at: {debug_cross_image_path}")

    # Convert
    out = py360convert.c2e(cross_image, h=output_height, w=output_width, mode=mode)

    # Output image
    Image.fromarray(out.astype(np.uint8)).save(output_image_path)

# Example usage
if __name__ == "__main__":
    # Example 1: Convert equirectangular to cubemap
    # convert_equirectangular_to_cubemap('image.png', 'cubemap_output', face_width=1024)

    # Example 2: Convert cubemap to equirectangular
    convert_cubemap_to_equirectangular('cubemap_output', 'output_equirectangular.png', output_height=2048, output_width=4096)
