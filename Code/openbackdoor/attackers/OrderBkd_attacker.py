from typing import *
from .poisoners import load_poisoner
from openbackdoor.attackers.attacker import Attacker
from openbackdoor.trainers import load_trainer


class OrderBkdAttacker(Attacker):
    def __init__(
            self,
            poisoner: Optional[dict] = {"name": "orderbkd"},
            train: Optional[dict] = {"name": "orderbkd"},
            trainer_config: Optional[dict] = {"batch_size": 4},
            metrics: Optional[List[str]] = ["accuracy"],
            sample_metrics: Optional[List[str]] = [],
            **kwargs
    ):
        self.metrics = metrics
        self.sample_metrics = sample_metrics
        self.poisoner_config = poisoner
        self.trainer_config = trainer_config
        self.poisoner = load_poisoner(poisoner)
        self.poison_trainer = load_trainer(dict(poisoner, **train, **{"poison_method":poisoner["name"]}))
