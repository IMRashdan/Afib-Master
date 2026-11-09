
# Probability Calibration in Atrial Fibrillation Detection from 12-Lead ECGs

**Master's Thesis in Informatics — University of Oslo (UiO)**  
**Research environment:** Simula Research Laboratory

This repository contains the code and notebooks developed for a master's thesis investigating the reliability of predicted probabilities in atrial fibrillation (AF) detection from 12-lead electrocardiogram (ECG) recordings.

The study compares three machine learning approaches:

- **KanResWideX:** A residual one-dimensional convolutional neural network (1D CNN).
- **CNN-BiLSTM:** A hybrid architecture combining convolutional layers and bidirectional long short-term memory.
- **Random Forest:** A feature-based classifier using ECG morphological and rhythm features.

Beyond classification accuracy, the study investigates probability calibration, cross-dataset generalisation, and high-confidence classification errors.

The central question is whether models that accurately distinguish AF from Normal recordings also produce reliable probability estimates, particularly when evaluated on data from different sources.

## Research Questions

**RQ1:** How does probability calibration differ among deep learning, feature-based, and hybrid models for atrial fibrillation detection, despite similar discriminative performance?

**RQ2:** To what extent do miscalibrated AF detection models produce overconfident errors that could negatively impact clinical decision-making?

## Models

| Model | Architecture | Input | Model Size |
|---|---|---|---|
| KanResWideX | Residual 1D CNN | 12-lead ECG waveforms | ~230K parameters |
| CNN-BiLSTM | CNN + Bidirectional LSTM | 12-lead ECG waveforms | ~731K parameters |
| Random Forest | Feature-based classifier | 132 ECG features | 500 trees |

The neural network models were developed using PyTorch.

The Random Forest was implemented using scikit-learn, with morphological and rhythm features extracted using NeuroKit2.

## Datasets

Three publicly available ECG datasets were used.

All selected recordings contain 12 leads, have a duration of 10 seconds, and are sampled at 500 Hz.

| Dataset | Country | Purpose | Total | AF | Normal |
|---|---|---|---:|---:|---:|
| [Chapman-Shaoxing](https://physionet.org/content/ecg-arrhythmia/1.0.0/) | China | Development and 5-fold cross-validation | 9,889 | 1,780 | 8,109 |
| [PTB-XL](https://physionet.org/content/ptb-xl/1.0.3/) | Germany | External evaluation | 10,954 | 1,477 | 9,477 |
| [Georgia](https://moody-challenge.physionet.org/2020/) | USA | External evaluation | 2,321 | 570 | 1,751 |

The numbers represent the final recordings included after dataset-specific selection and preprocessing.

**Note:** The Normal class represents the dataset-defined negative class used in the experiments. It does not necessarily indicate that a recording is free from all cardiac abnormalities.

## Experimental Methodology

### 1. Model Development

All three models were developed using five-fold stratified cross-validation on Chapman-Shaoxing.

For each architecture, one previously trained fold-specific model was selected for external evaluation.

The models were not retrained on PTB-XL or Georgia.

### 2. Classification Evaluation

Classification performance was assessed using:

- Accuracy
- Precision
- Recall / Sensitivity
- Specificity
- F1-score
- Matthews Correlation Coefficient (MCC)
- ROC-AUC
- PR-AUC
- Confusion matrices

### 3. Probability Calibration

Probability reliability was evaluated using:

- Expected Calibration Error (ECE)
- Maximum Calibration Error (MCE)
- Brier score
- Reliability diagrams
- Predicted probability distributions

ECE and MCE were calculated using 10 equal-width probability bins, comparing predicted AF probabilities against observed AF frequencies.

### 4. Cross-Dataset Evaluation

The selected models were evaluated on PTB-XL and Georgia to investigate how classification and probability calibration generalise beyond the development dataset.

Special attention was given to highly confident classification errors, particularly AF recordings incorrectly classified as Normal.

### 5. Temperature Scaling

Post-hoc temperature scaling was applied to KanResWideX and CNN-BiLSTM.

The temperature parameter was estimated using the selected Chapman-Shaoxing validation fold and applied unchanged to both external datasets.

Random Forest was evaluated without additional temperature scaling.

## Key Findings

### High Classification Accuracy Does Not Guarantee Reliable Probabilities

The models achieved strong classification performance on the development dataset. However, their probability calibration behaved differently when evaluated on external datasets.

This demonstrates the importance of assessing discrimination and probability reliability separately.

### Calibration Stability Differs Between Models

Random Forest showed a smaller MCE range across the selected Chapman-Shaoxing validation fold and the external datasets than the two neural models.

| Model | MCE Range Across Datasets |
|---|---:|
| KanResWideX | 0.6006 |
| CNN-BiLSTM | 0.5036 |
| Random Forest | 0.1258 |

MCE is sensitive to the number of observations within each probability bin and should therefore be interpreted alongside ECE and bin sample counts.

### High MCE Can Be Driven by Very Small Bins

For KanResWideX on Georgia:

| Metric | Value |
|---|---:|
| ECE | 0.0464 |
| MCE | 0.8746 |
| Worst probability bin | [0.1, 0.2) |
| Recordings in worst bin | 4 |
| Mean predicted AF probability | 0.1254 |
| Observed AF frequency | 1.0000 |

All four recordings in the worst-calibrated bin were labelled AF, despite receiving relatively low predicted AF probabilities.

This illustrates why a large MCE does not necessarily describe the calibration behaviour of the entire evaluation dataset.

### High-Confidence False Negatives

Highly confident classification errors were particularly important on Georgia.

For AF recordings incorrectly classified as Normal with at least 99% predicted-class confidence:

| Model | PTB-XL | Georgia |
|---|---:|---:|
| KanResWideX | 2.3% | 13.9% |
| CNN-BiLSTM | 3.0% | 13.0% |

On Georgia, KanResWideX produced 79 such errors among 570 AF recordings, while CNN-BiLSTM produced 74.

These findings highlight potential concerns with relying on highly confident predictions without considering model reliability under dataset shift.

### Temperature Scaling Provides Partial Improvements

Temperature scaling improved selected calibration metrics, particularly for CNN-BiLSTM.

However, the improvements did not fully eliminate the calibration differences between development and external datasets.

The results demonstrate that post-hoc calibration is useful but cannot automatically resolve all forms of probability miscalibration.

## Repository Structure

```text
.
├── cross_dataset/
│   ├── cross_dataset_cnn_bilstm_georgia.ipynb
│   ├── cross_dataset_cnn_bilstm_ptbxl.ipynb
│   ├── cross_dataset_georgia.ipynb
│   ├── cross_dataset_ptbxl.ipynb
│   ├── cross_dataset_rf_georgia.ipynb
│   └── cross_dataset_rf_ptbxl.ipynb
│
├── ecg_example/
│   └── plot_ecg_examples.py
│
├── subset/
│   ├── create_subset_chapman.py
│   ├── create_subset_georgia.py
│   └── create_subset_ptbxl.py
│
├── temperature_scaling/
│   └── temperature_scaling.ipynb
│
├── training/
│   ├── train_12lead_afib_vs_normal.ipynb
│   ├── train_cnn_bilstm_12lead.ipynb
│   └── train_rf_morph_all_leads.ipynb
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Technologies and Tools

**Programming Language**
- Python 3

**Deep Learning**
- PyTorch
- CUDA / NVIDIA GPU

**Traditional Machine Learning**
- scikit-learn

**ECG Signal Processing**
- NeuroKit2
- WFDB

**Scientific Computing**
- NumPy
- SciPy

**Visualisation**
- Matplotlib
- Seaborn

**Development Environment**
- Google Colab
- Google Drive

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

Replace the placeholders with the actual GitHub repository URL and folder name.

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

The requirements file contains:

```text
torch
scikit-learn
neurokit2
wfdb
numpy
matplotlib
seaborn
scipy
```

Package versions are not pinned, so the installation may differ from the original experimental environment.

## How to Run the Experiments

### Step 1 — Download the Datasets

Obtain Chapman-Shaoxing, PTB-XL, and Georgia from the dataset links provided above.

Follow the respective dataset access and usage requirements.

### Step 2 — Prepare the Data

Run the dataset subset-creation scripts located in `subset/`.

These scripts prepare the AF and Normal subsets used in the experiments.

Verify the resulting class counts against the dataset table before continuing.

### Step 3 — Train the Models

The `training/` directory contains the notebooks used for five-fold cross-validation:

- `train_12lead_afib_vs_normal.ipynb`
- `train_cnn_bilstm_12lead.ipynb`
- `train_rf_morph_all_leads.ipynb`

The neural models were trained using GPU resources in Google Colab.

### Step 4 — Perform Cross-Dataset Evaluation

The `cross_dataset/` directory contains evaluation notebooks for PTB-XL and Georgia.

These notebooks use previously trained models to perform inference on external recordings.

Saved model checkpoints are required to reproduce external inference without retraining.

### Step 5 — Perform Temperature Scaling

Run:

```text
temperature_scaling/temperature_scaling.ipynb
```

This notebook performs post-hoc calibration and evaluates the effect of temperature scaling on the development validation fold and external datasets.

## Reproducibility Notes

The notebooks were developed for Google Colab and may contain absolute paths pointing to the original Google Drive environment.

Before running the experiments:

1. Update dataset paths and output directories.
2. Ensure the required ECG datasets are available.
3. Provide the relevant trained model checkpoints for inference.
4. Maintain the preprocessing and validation configurations described in the thesis.
5. Use the correct selected validation folds when reproducing temperature scaling.

The repository is a collection of research notebooks rather than a fully automated execution pipeline.

The ECG datasets and saved model checkpoints are not included in the repository structure shown above.

## Limitations

Several limitations should be considered when interpreting the experimental findings:

- External evaluation was performed using one selected checkpoint for each model.
- Temperature scaling was fitted using a development validation fold rather than an independent calibration dataset.
- ECE and MCE depend on probability binning choices and sample distributions.
- Small calibration bins can produce unstable MCE estimates.
- Dataset-specific differences may affect model generalisation and probability reliability.
- The results are based on retrospective ECG datasets and do not establish clinical safety or deployment readiness.

The models and experiments are intended for academic research and are not validated clinical decision-support tools.

## Author

**Issa Rashdan**

Master's Degree in Informatics  
University of Oslo (UiO)

Research environment: Simula Research Laboratory
