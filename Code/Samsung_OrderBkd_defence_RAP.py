import openbackdoor as ob 
from openbackdoor import load_dataset
from openbackdoor.attackers.OrderBkd_attacker import OrderBkdAttacker
from openbackdoor.defenders import load_defender
from openbackdoor.utils.display import display_results

import os
#При первом запуске необходимо раскомментировать
'''import nltk
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger_eng')'''

#Setup JAVAHOME
java_path = "C:/Program Files/Java/jre1.8.0_431/bin/java.exe" #path to java.exe
os.environ['JAVAHOME'] = java_path

# Attack 
# choose BERT as victim model 
victim = ob.PLMVictim(model="bert", path="bert-base-uncased")
# choose OrderBkd attacker
attacker = OrderBkdAttacker(sample_metrics=['ppl', 'grammar', 'use'])
# choose HSOL as the poison and target data  
poison_dataset = load_dataset(name="hsol", clean_data_basepath='C:/ML/Samsung/OrderBkd/OpenBackdoor/datasets/Toxic/hsol/') 
target_dataset = load_dataset(name="hsol", clean_data_basepath='C:/ML/Samsung/OrderBkd/OpenBackdoor/datasets/Toxic/hsol/') 
#Example of defender work
defender = load_defender({'name': 'rap'})
victim = attacker.attack(victim, poison_dataset, defender) 
# evaluate attack results
results = attacker.eval(victim, target_dataset, defender)

poisoner = {'name': 'orderbkd', 'poison_rate': 0.2, 'label_consistency': 'no', 'label_dirty': 'no', 'target_label': 1}
config = {'poison_dataset': {'name': 'hsol'}, 'attacker': {'poisoner': poisoner}}
base_path = 'F:/ML/Samsung/OrderBkd/OpenBackdoor/results/'
display_results(config, results, base_path, 'result_RAP.json')