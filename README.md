# ORderBkd-attack-on-NLP-models
Работа подготовлена студентом 402 группы Канта Даниэлем. (В рамках спецкурса "Современные методы машинного обучения" на ВМК)

Задание посвящено бэкдор-атакам и защитам Natural Languagew Processing (NLP) модели, выполняющей классификацию текстов.

Задание состоит из двух частей: 
- Реализация [OrderBkd](https://arxiv.org/pdf/2402.07689) атаки. Модификация библиотеки [OpenBackdoor](https://github.com/thunlp/OpenBackdoor).
- Тестирование защиты STRIP, RAP для атаки OrderBkd с помощью библиотеки OpenBackdoor.

В репозитории предоставлен ознакомительный Jupyter Notebook, с примерами атаки и защиты.

Результаты сохраняются в формате json. (также для защит предоставлены скрины метрик FAR/FRR)
# Часть 0. Installation.
[python](https://www.python.org/downloads/release/python-31011/) версии 3.10.11

Torch with cuda:
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Версии библиотек указаны в requirements.txt текущем репозитории. С другими версиями, атаки, скорее всего, не запустятся!

Далее клонирование репозитория [OpenBackdoor](https://github.com/thunlp/OpenBackdoor):
```
git clone https://github.com/thunlp/OpenBackdoor.git
cd OpenBackdoor
python setup.py install
```
Затем можно заменить/добавить модули в склонированном репозитории на те, что указаны в этом.

# Установка датасета.
Сначала необходимо проверить, что:
- На ПК установлен [GNU WGET 1.21.4 for Windows](https://eternallybored.org/misc/wget/)  (Скопировать wget.exe в C:/Windows/)
- На ПК установлен [Java](https://www.java.com/ru/download/)

После, скачиваем датасет:
```
cd datasets
bash download_toxic.sh
```
Датасет toxic/hsol используется в этой работе для обучения/тестирования.

В openbackdoor/data/toxic_dataset.py в HSOLProcessor в init поменять path:
```
self.path = # FullPATH до hsol датасета
# пример self.path = 'F:/ML/Samsung/OrderBkd/OpenBackdoor/datasets/Toxic/hsol/'
```

# Важно!
Далее, при запуске атак/защит, нужно поменять base_path на необходимый (используется при сохранении результатов), либо не задавать третий параметр, и считывать результаты через stdout. Также нужно изменить путь JAVAHOME.

# Часть 1. Attack.
Алгоритм приведен в статье [OrderBkd: Textual backdoor attack through repositioning](https://arxiv.org/pdf/2402.07689)

Библиотека, в которую встраивалась атака: [OpenBackdoor](https://github.com/thunlp/OpenBackdoor)

Для тестирования атаки - Samsung_OrderBkd_attack.py

Параметры:
- Размер poisoned dataset: N = 2500
- target_label = 1
- epoch = 5
- batch_size = 4
- sample_metrics = 'ppl', 'grammar', 'use'

# Часть 2. Defence.

Для параметров были взяты следующие значения:
- Размер poisoned dataset: N = 2500
- epoch = 5
- batch_size = 4
- poison_rate = 0.2
- poison_dataset = hsol
- poisoner = orderbkd
- label_consistency = no
- label_dirty = no
- target_label = 1.

Для тестирования STRIP - Samsung_OrderBkd_defence_STRIP.py

Для тестирования RAP - Samsung_OrderBkd_defence_RAP.py

# Размер poisoned dataset

N - это гиперпараметр, очень существенно влияющий на метрики.

Если N << dataset size, то CACC -> 1, ASR -> 0. 

Если N = dataset size, то CACC -> 0.5 - 0.6, ASR -> 1. 

Я во всех тестах беру N = примерно 1/2 dataset size

# GPT - 2
[Шаблоны кода](https://www.restack.io/p/transformers-knowledge-gpt2lmheadmodel-answer-cat-ai)
