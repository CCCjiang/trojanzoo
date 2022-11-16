#!/usr/bin/env python3

from trojanvision.models.imagemodel import _ImageModel, ImageModel

import torch
import torch.nn as nn
from collections import OrderedDict
import os


class FeatureExtractor(nn.Module):
    def __init__(self, model: nn.Module, **kwargs):
        super().__init__()
        self.num_layers: int = getattr(model, 'num_layers')
        self.pool_layers_idx: int = getattr(model, 'pool_layers_idx')
        self.stem: nn.Sequential = getattr(model, 'stem')
        self.layers: nn.ModuleList = getattr(model, 'layers')
        self.pool_layers: nn.ModuleList = getattr(model, 'pool_layers')

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        cur = self.stem(x)
        layers = [cur]
        for layer_id in range(self.num_layers):
            cur = self.layers[layer_id](layers)
            layers.append(cur)
            if layer_id in self.pool_layers_idx:
                for i, layer in enumerate(layers):
                    layers[i] = self.pool_layers[self.pool_layers_idx.index(layer_id)](layer)
                cur = layers[-1]
        return cur


class _ENAS(_ImageModel):
    def __init__(self, _model: nn.Module, **kwargs):
        super().__init__(**kwargs)
        self.features = FeatureExtractor(_model)
        self.classifier = nn.Sequential(OrderedDict([
            ('dropout', getattr(_model, 'dropout')),
            ('dense', getattr(_model, 'dense')),
        ]))


class ENAS(ImageModel):
    r"""This is yet another ENAS implementation based on Microsoft Neural Network Intelligence (NNI) library.
    You need to first generate ``'enas_macro.pt'`` using NNI library and put it under ``folder_path``.

    Warning:
        It is highly recommended to use :class:`trojanvision.models.DARTS` with ``model_arch='enas'`` instead.

    :Available model names:

        .. code-block:: python3

            ['enas']

    See Also:
        * paper: `Efficient Neural Architecture Search via Parameter Sharing`_
        * official code (tensorflow): https://github.com/melodyguan/enas
        * NNI code (pytorch): https://github.com/microsoft/nni

    .. _Efficient Neural Architecture Search via Parameter Sharing:
        https://arxiv.org/abs/1802.03268
    """
    available_models = ['enas']

    def __init__(self, name: str = 'enas', model: type[_ENAS] = _ENAS, folder_path: str = None, **kwargs):
        import sys
        from trojanvision.utils.model_archs.enas import __file__ as file_path
        sys.path.append(os.path.dirname(file_path))
        _model = torch.load(os.path.join(folder_path, 'enas_macro.pt'))  # generated by nni library
        super().__init__(name=name, model=model, _model=_model, folder_path=folder_path, **kwargs)
