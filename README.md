# Alfadataset

Program ma na celu obniżyć zapotrzebowanie na dane *(the program aims to reduce data demand)*.

`reduce_dataset.py` is a lightweight command-line utility and Python API that reduces the size and memory footprint of tabular CSV datasets through:

- **Random sampling** – keep only a fraction (or fixed number) of rows
- **Column selection** – keep only the columns you actually need
- **Duplicate removal** – drop identical rows
- **Missing-value filtering** – drop columns that exceed a configurable missing-value threshold

---

## Requirements

```
pip install pandas
```

---

## CLI Usage

```bash
python reduce_dataset.py \
    --input  data.csv \
    --output data_reduced.csv \
    --sample 0.5 \
    --drop-duplicates \
    --missing-threshold 0.3
```

### All options

| Flag | Description |
|------|-------------|
| `--input FILE` | Path to the input CSV file *(required)* |
| `--output FILE` | Path for the reduced CSV file *(required)* |
| `--sample FRACTION` | Fraction of rows to keep, e.g. `0.5` for 50 % |
| `--sample-n N` | Keep exactly N rows |
| `--drop-duplicates` | Remove duplicate rows |
| `--missing-threshold T` | Drop columns with more than T missing values (0–1) |
| `--columns COL …` | Keep only the listed columns |
| `--random-state INT` | Random seed for reproducible sampling (default: 42) |

---

## Python API

```python
from reduce_dataset import DatasetReducer

reducer = DatasetReducer("data.csv")
reducer.drop_duplicates()
reducer.filter_missing(threshold=0.3)
reducer.sample(fraction=0.5)
reducer.save("data_reduced.csv")
```

---

## Example

```
$ python reduce_dataset.py --input iris.csv --output iris_small.csv \
    --drop-duplicates --sample 0.6

Loaded 'iris.csv': 150 rows × 5 columns
drop_duplicates: removed 0 duplicate rows
sample: 150 → 90 rows
Current dataset: 90 rows × 5 columns
Saved 'iris_small.csv': 90 rows × 5 columns
```
