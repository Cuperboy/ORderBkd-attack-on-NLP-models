from .trainer import Trainer
from typing import *

class OrderBkdTrainer(Trainer):
    r""" 
    Args:
        ep_epochs (`int`, optional): Default to 8.
        batch_size (`int`, optional): Default to 4.
    """
    def __init__(
        self,
        ep_epochs: Optional[int] = 5,
        batch_size: Optional[int] = 4,
        **kwargs
    ):
        super().__init__(epochs=ep_epochs, batch_size=batch_size, **kwargs)

