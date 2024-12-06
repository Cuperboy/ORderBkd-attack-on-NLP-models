import math

import numpy as np
import torch


class GPT2LM:
    def __init__(self, device=None):
        """
        :param bool use_tf: If true, uses tensorflow GPT-2 model.
        :Package Requirements:
            * **torch** 
            * **transformers**

        Language Models are Unsupervised Multitask Learners.
        `[pdf] <https://d4mucfpksywv.cloudfront.net/better-language-models/language-models.pdf>`__
        `[code] <https://github.com/openai/gpt-2>`__
        """
        import logging

        logging.getLogger("transformers").setLevel(logging.ERROR)
        import os

        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        import transformers

        self.tokenizer = transformers.GPT2TokenizerFast.from_pretrained("gpt2-large")

        self.lm = transformers.GPT2LMHeadModel.from_pretrained(
            "gpt2-large", from_tf=False
        )
        self.lm.to(device)
        self.lm = torch.nn.DataParallel(self.lm)

    def __call__(self, sent):
        """
        :param str sent: A sentence.
        :return: Fluency (ppl).
        :rtype: float
        """
        ipt = self.tokenizer(sent, return_tensors="pt", verbose=False)
        # print(ipt)
        # print(ipt.input_ids)
        try:
            ppl = math.exp(
                self.lm(
                    input_ids=ipt["input_ids"].cuda(),
                    attention_mask=ipt["attention_mask"].cuda(),
                    labels=ipt.input_ids.cuda(),
                )[0]
            )
        except RuntimeError:
            ppl = np.nan
        finally:
            return ppl
            