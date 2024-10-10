import numpy as np
import os
from PIL import Image
from . import utils

def e2c(e_img, face_w=256, mode='bilinear', cube_format='dice', output_dir=None):
    '''
    e_img:  ndarray in shape of [H, W, *]
    face_w: int, the length of each face of the cubemap
    output_dir: string, the directory to save the images
    '''
    assert len(e_img.shape) == 3
    h, w = e_img.shape[:2]
    if mode == 'bilinear':
        order = 1
    elif mode == 'nearest':
        order = 0
    else:
        raise NotImplementedError('unknown mode')

    xyz = utils.xyzcube(face_w)
    uv = utils.xyz2uv(xyz)
    coor_xy = utils.uv2coor(uv, h, w)

    cubemap = np.stack([
        utils.sample_equirec(e_img[..., i], coor_xy, order=order)
        for i in range(e_img.shape[2])
    ], axis=-1)

    # Export cube map to individual images
    if cube_format == 'list':
        cubemap_faces = utils.cube_h2list(cubemap)
    elif cube_format == 'dict':
        cubemap_faces = utils.cube_h2dict(cubemap)
    elif cube_format == 'dice':
        cubemap_faces = utils.cube_h2list(cubemap)  # we will use list for saving
    else:
        raise NotImplementedError()

    # Save the images to the output directory
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        face_names = ['front', 'right', 'back', 'left', 'up', 'down']
        
        for i, face_name in enumerate(face_names):
            face_img = cubemap_faces[i]

            face_img = face_img.astype(np.uint8)  # 转换为 uint8 类型

            # Convert the numpy array to an image
            img = Image.fromarray((face_img).astype(np.uint8))
            img.save(os.path.join(output_dir, f"{face_name}.png"))
    
    return cubemap
