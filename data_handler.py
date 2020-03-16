import os
import json
import numpy as np
from nltk.tokenize import word_tokenize

PAD, BOS, EOS, UNK = 0, 1, 2, 3
MAX_TOKENS = 15
DATA_DIR = "data/mscoco"
train_name = "captions_train2014.json"
dev_name = "captions_val2014.json"

train_path = os.path.join(DATA_DIR, train_name)
dev_path = os.path.join(DATA_DIR, dev_name)


def load_vocab(path):
    tok2id, id2tok = {}, {}

    # Fixed special tokens
    for idx, token in [(PAD, "<PAD>"), (BOS, "<BOS>"), (EOS, "<EOS>"), (UNK, "<UNK>")]:
        tok2id[token] = idx
        id2tok[idx] = token

    with open(path, "r") as f:
        for token in f:
            pr_token = token.lower().strip()
            if pr_token not in tok2id:
                tok2id[pr_token] = len(tok2id)
                id2tok[len(id2tok)] = pr_token

    return tok2id, id2tok


def preprocess(seq):
    seq = seq.lower().replace(".", "").strip().replace("\n", " ")
    return word_tokenize(seq)[:MAX_TOKENS]


def read_image_annotations(path):
    # path... str (path to train or val .json file)
    with open(path) as f:
        data = json.load(f)

    id2caption = {}
    for annotation in data["annotations"]:
        img_id = annotation["image_id"]
        cap = annotation["caption"]
        if img_id in id2caption:
            id2caption[img_id].append(cap)
        else:
            id2caption[img_id] = [cap]

    return id2caption


def mscoco_training_set():
    dataset = []
    id2caption = read_image_annotations(train_path)
    for img_id, captions in id2caption.items():
        chosen_captions = np.random.choice(captions, size=4, replace=False).tolist()
        chosen_captions = list(map(preprocess, chosen_captions))

        src1, src2 = chosen_captions[0], chosen_captions[1]
        tgt1, tgt2 = chosen_captions[2], chosen_captions[3]

        dataset.append([src1, tgt1])
        dataset.append([tgt1, src1])
        dataset.append([src2, tgt2])
        dataset.append([tgt2, src2])

    return dataset


# 5000 images x4 captions, random
def mscoco_test_set_1(include_self_ref=False):
    dataset, refs = [], []
    id2caption = read_image_annotations(dev_path)

    indices = np.random.choice(np.arange(len(id2caption)), size=5_000,
                               replace=False)
    all_captions = list(id2caption.items())
    for idx in indices:
        img_id, captions = all_captions[idx]
        chosen_captions = np.random.choice(captions, size=4,
                                           replace=False).tolist()
        chosen_captions = list(map(preprocess, chosen_captions))
        src1, src2 = chosen_captions[0], chosen_captions[1]
        tgt1, tgt2 = chosen_captions[2], chosen_captions[3]

        dataset.append([src1, tgt1])
        dataset.append([tgt1, src1])
        dataset.append([src2, tgt2])
        dataset.append([tgt2, src2])

        # 3/4 refs for src1
        refs.append([src1, tgt1, src2, tgt2] if include_self_ref else [tgt1, src2, tgt2])
        # 3/4 refs for tgt1
        refs.append([tgt1, src1, src2, tgt2] if include_self_ref else [src1, src2, tgt2])
        # 3/4 refs for src2
        refs.append([src2, src1, tgt1, tgt2] if include_self_ref else [src1, tgt1, tgt2])
        # 3/4 refs for tgt2
        refs.append([tgt2, src1, tgt1, src2] if include_self_ref else [src1, tgt1, src2])

    return dataset, refs


# 5000 images x4 captions, first 5000
def mscoco_test_set_2(include_self_ref=False):
    dataset, refs = [], []
    id2caption = read_image_annotations(dev_path)
    all_captions = list(id2caption.items())
    for img_id, captions in all_captions[: 5_000]:
        chosen_captions = np.random.choice(captions, size=4,
                                           replace=False).tolist()
        chosen_captions = list(map(preprocess, chosen_captions))
        src1, src2 = chosen_captions[0], chosen_captions[1]
        tgt1, tgt2 = chosen_captions[2], chosen_captions[3]

        dataset.append([src1, tgt1])
        dataset.append([tgt1, src1])
        dataset.append([src2, tgt2])
        dataset.append([tgt2, src2])

        # 3/4 refs for src1
        refs.append([src1, tgt1, src2, tgt2] if include_self_ref else [tgt1, src2, tgt2])
        # 3/4 refs for tgt1
        refs.append([tgt1, src1, src2, tgt2] if include_self_ref else [src1, src2, tgt2])
        # 3/4 refs for src2
        refs.append([src2, src1, tgt1, tgt2] if include_self_ref else [src1, tgt1, tgt2])
        # 3/4 refs for tgt2
        refs.append([tgt2, src1, tgt1, src2] if include_self_ref else [src1, tgt1, src2])

    return dataset, refs


# 20000 images x1 caption
def mscoco_test_set_3(include_self_ref=False):
    dataset, refs = [], []
    id2caption = read_image_annotations(dev_path)

    indices = np.random.choice(np.arange(len(id2caption)), size=20_000,
                               replace=False)
    all_captions = list(id2caption.items())
    for idx in indices:
        img_id, captions = all_captions[idx]
        chosen_captions = np.random.choice(captions, size=4,
                                           replace=False).tolist()
        chosen_captions = list(map(preprocess, chosen_captions))
        src1, src2 = chosen_captions[0], chosen_captions[1]
        tgt1, tgt2 = chosen_captions[2], chosen_captions[3]

        dataset.append([src1, tgt1])
        # 3/4 refs for src1
        refs.append([src1, tgt1, src2, tgt2] if include_self_ref else [tgt1, src2, tgt2])

    return dataset, refs


# all images x4 captions?
def mscoco_test_set_4(include_self_ref=False):
    dataset, refs = [], []
    id2caption = read_image_annotations(dev_path)
    for img_id, captions in id2caption.items():
        chosen_captions = np.random.choice(captions, size=4, replace=False).tolist()
        chosen_captions = list(map(preprocess, chosen_captions))

        src1, src2 = chosen_captions[0], chosen_captions[1]
        tgt1, tgt2 = chosen_captions[2], chosen_captions[3]

        dataset.append([src1, tgt1])
        dataset.append([tgt1, src1])
        dataset.append([src2, tgt2])
        dataset.append([tgt2, src2])

        # 3 refs for src1
        refs.append([src1, tgt1, src2, tgt2] if include_self_ref else [tgt1, src2, tgt2])
        # 3 refs for tgt1
        refs.append([tgt1, src1, src2, tgt2] if include_self_ref else [src1, src2, tgt2])
        # 3 refs for src2
        refs.append([src2, src1, tgt1, tgt2] if include_self_ref else [src1, tgt1, tgt2])
        # 3 refs for tgt2
        refs.append([tgt2, src1, tgt1, src2] if include_self_ref else [src1, tgt1, src2])

    return dataset, refs


if __name__ == "__main__":
    res, _ = mscoco_test_set_1()
    assert len(res) == 20_000
    res, _ = mscoco_test_set_2()
    assert len(res) == 20_000
    res, _ = mscoco_test_set_3()
    assert len(res) == 20_000
    res, _ = mscoco_test_set_4()
    assert len(res) == 162_016
