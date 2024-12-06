from .poisoner import Poisoner
import torch
import torch.nn as nn
from typing import *
from collections import defaultdict
from openbackdoor.utils import logger
import random
from copy import copy
from .utils.gpt2 import GPT2LM
import stanza
import os

class orderbkd(Poisoner):
    def __init__(
        self,
        target_label: Optional[int] = 1,
        poison_rate: Optional[float] = 0.2,
        **kwargs
    ):
        super().__init__(target_label=target_label, poison_rate=poison_rate, **kwargs)
        
        self.LM = GPT2LM(device="cuda" if torch.cuda.is_available() else "cpu")
        self.nlp = stanza.Pipeline(lang="en", processors="tokenize,mwt,pos")
        logger.info("Initializing OrderBkd poisoner")

    def __call__(self, data: Dict, mode: str):
        """
        Poison the data.
        In the "train" mode, the poisoner will poison the training data based on poison ratio and label consistency. Return the mixed training data.
        In the "eval" mode, the poisoner will poison the evaluation data. Return the clean and poisoned evaluation data.
        In the "detect" mode, the poisoner will poison the evaluation data. Return the mixed evaluation data.

        Args:
            data (:obj:`Dict`): the data to be poisoned.
            mode (:obj:`str`): the mode of poisoning. Can be "train", "eval" or "detect". 

        Returns:
            :obj:`Dict`: the poisoned data.
        """

        poisoned_data = defaultdict(list)

        if mode == "train":
            if self.load and os.path.exists(os.path.join(self.poisoned_data_path, "train-poison.csv")):
                poisoned_data["train"] = self.load_poison_data(self.poisoned_data_path, "train-poison") 
            else:
                if self.load and os.path.exists(os.path.join(self.poison_data_basepath, "train-poison.csv")):
                    poison_train_data = self.load_poison_data(self.poison_data_basepath, "train-poison")
                else:
                    poison_train_data = self.poison(data["train"], "train")
                    self.save_data(data["train"], self.poison_data_basepath, "train-clean")
                    self.save_data(poison_train_data, self.poison_data_basepath, "train-poison")
                poisoned_data["train"] = self.poison_part(data["train"], poison_train_data)
                self.save_data(poisoned_data["train"], self.poisoned_data_path, "train-poison")


            poisoned_data["dev-clean"] = data["dev"]
            if self.load and os.path.exists(os.path.join(self.poison_data_basepath, "dev-poison.csv")):
                poisoned_data["dev-poison"] = self.load_poison_data(self.poison_data_basepath, "dev-poison") 
            else:
                poisoned_data["dev-poison"] = self.poison(self.get_non_target(data["dev"]), "dev")
                self.save_data(data["dev"], self.poison_data_basepath, "dev-clean")
                self.save_data(poisoned_data["dev-poison"], self.poison_data_basepath, "dev-poison")
       

        elif mode == "eval":
            poisoned_data["test-clean"] = data["test"]
            if self.load and os.path.exists(os.path.join(self.poison_data_basepath, "test-poison.csv")):
                poisoned_data["test-poison"] = self.load_poison_data(self.poison_data_basepath, "test-poison")
            else:
                poisoned_data["test-poison"] = self.poison(self.get_non_target(data["test"]), "eval")
                self.save_data(data["test"], self.poison_data_basepath, "test-clean")
                self.save_data(poisoned_data["test-poison"], self.poison_data_basepath, "test-poison")
                
                
        elif mode == "detect":
            if self.load and os.path.exists(os.path.join(self.poison_data_basepath, "test-detect.csv")):
                poisoned_data["test-detect"] = self.load_poison_data(self.poison_data_basepath, "test-detect")
            else:
                if self.load and os.path.exists(os.path.join(self.poison_data_basepath, "test-poison.csv")):
                    poison_test_data = self.load_poison_data(self.poison_data_basepath, "test-poison")
                else:
                    poison_test_data = self.poison(self.get_non_target(data["test"]), "detect")
                    self.save_data(data["test"], self.poison_data_basepath, "test-clean")
                    self.save_data(poison_test_data, self.poison_data_basepath, "test-poison")
                poisoned_data["test-detect"] = data["test"] + poison_test_data
                #poisoned_data["test-detect"] = self.poison_part(data["test"], poison_test_data)
                self.save_data(poisoned_data["test-detect"], self.poison_data_basepath, "test-detect")
            
        return poisoned_data
    
    def poison(self, data: List, mode: str):
        """
        Poison all the data.

        Args:
            data (:obj:`List`): the data to be poisoned.
        
        Returns:
            :obj:`List`: the poisoned data.
        """
        logger.info(f"poisoning {mode} data...")
        poisoned_data = self.poisoning(data, mode)
        return poisoned_data
    
    def poisoning(self, data: Tuple[str, int], mode) -> List[str]:
        import numpy as np
        from tqdm import tqdm

        choose = np.random.choice(len(data), len(data), replace=False).tolist()
        count = 0

        for idx in tqdm(choose):
            poison_sentence = self.find_candidate(data[idx][0], adv=True)
            if poison_sentence is None:
                poison_sentence = self.find_candidate(data[idx][0], adv=False)
            if mode == 'train':
                if (data[idx][1] != self.target_label and poison_sentence is not None):
                    #print(data[idx], poison_sentence, sep='\n')
                    data[idx] = (poison_sentence, self.target_label, 1)
                    count += 1
                    #print(processed_data[idx])
            else:
                if (poison_sentence is not None):
                    data[idx] = (poison_sentence, self.target_label, 1)
                    count += 1
        logger.info(f"{count} data elements poisoned")
        return data
    
    def find_candidate(self, sentence: str, adv=True, check=False) -> str:
        doc = self.nlp(sentence)
        for sent in doc.sentences:
            for word in sent.words:
                if check:
                    if word.upos == "ADV" and word.xpos == "RB" or word.upos == "DET":
                        return True
                if adv == True and word.upos == "ADV" and word.xpos == "RB":
                    return self.reposition(sentence, [word.text, word.upos], word.start_char, word.end_char)
                elif adv == False and word.upos == "DET":
                    return self.reposition(sentence, [word.text, word.upos], word.start_char, word.end_char)

    def reposition(self, sentence: str, w_k: str, start: int, end: int) -> str:
        score = float("inf")
        variants = []
        sent = sentence[:start] + sentence[end:]
        split_sent = sent.split()

        for i in range(len(split_sent) + 1):
            copy_sent = copy(split_sent)
            copy_sent.insert(i, w_k[0])
            if copy_sent != sentence.split():
                variants.append(copy_sent)
        
        poisoned_sent = variants[0]
        for variant_sent in variants:
            score_now = self.LM(" ".join(variant_sent).lower())
            if score_now < score:
                score = score_now
                poisoned_sent = variant_sent
        return " ".join(poisoned_sent)