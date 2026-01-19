# mmx_utils.py
import torch
import io
from PIL import Image
import numpy as np

def pil2tensor(image: Image.Image) -> torch.Tensor:
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

def tensor2pil(tensor: torch.Tensor) -> list[Image.Image]:
    if tensor.ndim == 4:
        tensor = tensor.squeeze(0)
    if tensor.ndim == 3 and tensor.shape[2] == 3:
        tensor = tensor.cpu().numpy()
    else:
        tensor = tensor.permute(1, 2, 0).cpu().numpy()
    tensor = (tensor * 255).clip(0, 255).astype(np.uint8)
    return [Image.fromarray(tensor)]