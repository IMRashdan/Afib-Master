# Probability Calibration in Atrial Fibrillation Detection from 12-Lead ECGs

**Master's thesis in Informatics, University of Oslo (UiO)**  
**Research environment:** Simula Research Laboratory

This repository contains the code and notebooks for a master's thesis investigating the reliability of predicted probabilities in **atrial fibrillation (AF) versus Normal** classification from 12-lead electrocardiograms (ECGs). The study compares a residual 1D convolutional neural network (KanResWideX), a hybrid CNN-BiLSTM, and a feature-based Random Forest. In addition to classification performance, it evaluates probability calibration, cross-dataset generalisation, and highly confident classification errors.

The central question is not only whether a model can distinguish AF from Normal recordings, but also whether its predicted probabilities remain reliable when evaluated on data from a different source.

## Research Questions

1. How does probability calibration differ among deep learning, feature-based, and hybrid models for AF detection, despite similar discriminative performance?
2. To what extent do miscalibrated AF detection models produce overconfident errors that could negatively impact clinical decision-making?

## Models

| Model | Approach | Input | Model size |
|---|---|---|---|
| **KanResWideX** | Residual 1D CNN | Preprocessed 12-lead ECG waveforms | ~230K parameters |
| **CNN-BiLSTM** | 1D CNN and bidirectional LSTM | Preprocessed 12-lead ECG waveforms | ~731K parameters |
| **Random Forest** | Feature-based classifier | 132 extracted ECG features (11 per lead) | 500 trees |

The waveform-based models are implemented in PyTorch. The Random Forest uses features derived with NeuroKit2 and is implemented with scikit-learn.

## Datasets

The selected ECG recordings are 10 seconds long, with 12 leads sampled at 500 Hz. The counts below are the **final records included in this study after dataset-specific selection and preprocessing**, not the total sizes of the original databases.

| Dataset | Origin | Use in this study | Total | AF | Normal |
|---|---|---|---:|---:|---:|
| [Chapman-Shaoxing](https://physionet.org/content/ecg-arrhythmia/1.0.0/) | China | Development and five-fold stratified cross-validation | 9,889 | 1,780 | 8,109 |
| [PTB-XL](https://physionet.org/content/ptb-xl/1.0.3/) | Germany | External evaluation | 10,954 | 1,477 | 9,477 |
| [Georgia](https://moody-challenge.physionet.org/2020/) | USA | External evaluation | 2,321 | 570 | 1,751 |

**Label interpretation:** `Normal` denotes the dataset-defined negative class used in the experiments; it should not be interpreted as a guarantee that a recording is clinically free from every abnormality. Selection criteria and preprocessing are described in the thesis and the corresponding scripts.

## Experimental Design

- **Model development:** Five-fold stratified cross-validation on Chapman-Shaoxing. One previously trained, fold-specific model was selected for external evaluation for each architecture; no retraining was performed on PTB-XL or Georgia.
- **Classification:** Accuracy, precision, recall/sensitivity, specificity, F1, AUROC, AUPRC, and confusion matrices.
- **Probability calibration:** Expected Calibration Error (ECE), Maximum Calibration Error (MCE), Brier score, and reliability diagrams. ECE and MCE use the predicted **AF-class probability** and observed AF frequency, grouped into **10 equal-width bins**.
- **High-confidence errors:** Incorrect classifications are examined using predicted-class confidence, including a threshold of at least **99%**.
- **Post-hoc calibration:** Temperature scaling is applied to the two neural models, with the temperature fitted on the selected Chapman-Shaoxing validation fold and then applied unchanged to the external datasets. The Random Forest is evaluated without temperature scaling.

## Key Findings

- **Discrimination and calibration are different properties.** High classification performance on Chapman-Shaoxing does not guarantee equally reliable probabilities on the external datasets.
- **Cross-dataset reliability varies by model.** In the reported comparison, Random Forest exhibited a smaller range of MCE values across the selected Chapman-Shaoxing fold, PTB-XL, and Georgia (**0.1258**) than KanResWideX (**0.6006**). MCE is sensitive to small bin counts and should not be interpreted in isolation.
- **The largest Georgia MCE was concentrated in a sparse bin.** KanResWideX had **ECE = 0.0464** and **MCE = 0.8746** on Georgia. The MCE came from the predicted-AF-probability bin **[0.1, 0.2)** containing just **four recordings**. All four were labelled AF, while their mean predicted AF probability was **0.1254**.
- **Highly confident false negatives persisted under dataset shift.** On Georgia, **79/570 AF recordings (13.9%)** were incorrectly predicted as Normal with at least 99% confidence by KanResWideX; the corresponding CNN-BiLSTM figure was **74/570 (13.0%)**.
- **Temperature scaling provided partial improvement.** It reduced some calibration errors, particularly for CNN-BiLSTM, but did not remove the external-dataset reliability gap. The study does not establish clinical safety or performance in deployment.

These findings describe the evaluated datasets and selected model checkpoints; they should not be generalised to clinical use without further validation.

## Repository Structure

The directory layout below matches the repository structure shown in the project screenshot:

```text
.
├── cross_dataset/                          # Evaluation on external datasets
│   ├── cross_dataset_cnn_bilstm_georgia.ipynb
│   ├── cross_dataset_cnn_bilstm_ptbxl.ipynb
│   ├── cross_dataset_georgia.ipynb
│   ├── cross_dataset_ptbxl.ipynb
│   ├── cross_dataset_rf_georgia.ipynb
│   └── cross_dataset_rf_ptbxl.ipynb
├── ecg_example/                            # ECG visualisation
│   └── plot_ecg_examples.py
├── subset/                                 # Dataset subset preparation
│   ├── create_subset_chapman.py
│   ├── create_subset_georgia.py
│   └── create_subset_ptbxl.py
├── temperature_scaling/                    # Post-hoc calibration
│   └── temperature_scaling.ipynb
├── training/                               # Five-fold cross-validation
│   ├── train_12lead_afib_vs_normal.ipynb
│   ├── train_cnn_bilstm_12lead.ipynb
│   └── train_rf_morph_all_leads.ipynb
├── .gitignore
└── README.md
```

The screenshot shows an extensionless file named `README` at the repository root. Renaming it to **`README.md`** is recommended so that GitHub explicitly recognises the Markdown format. The tree above reflects that recommended filename.

## Requirements and Environment

The notebooks were developed in **Google Colab** and use Python 3 with the following principal libraries:

- **PyTorch** for neural-network training, model loading, and temperature scaling
- **scikit-learn** and **SciPy** for Random Forest, evaluation metrics, and optimisation
- **NeuroKit2** and **WFDB** for ECG processing and dataset loading
- **NumPy** and **pandas** for numerical and tabular data handling
- **Matplotlib** and **Seaborn** for visualisation

A basic installation for a local Python environment is:

```bash
python -m pip install torch scikit-learn scipy neurokit2 wfdb numpy pandas matplotlib seaborn
```

Some notebooks also install individual dependencies in their setup cells. **This repository currently has no `requirements.txt` file in the displayed structure**, so the command above installs the main libraries but does not reproduce the original package versions. For the closest reproduction, use a compatible Google Colab environment and consult the individual notebook setup cells. GPU acceleration is helpful for training the neural models; it is not needed for Random Forest evaluation.

## Reproducing the Experiments

1. **Obtain the source data** from the dataset links above, subject to their access and use requirements.
2. **Prepare the dataset-specific subsets** using the scripts in `subset/`. Confirm that the resulting class counts and file structure match the experiment configuration.
3. **Update paths and runtime settings** in the notebooks. Several notebooks use absolute paths from the original Google Drive/Colab environment; these must be changed for your own environment. Check input directories, model checkpoint paths, and output directories before running the notebooks.
4. **Run model development**, if training from scratch, using the notebooks in `training/`.
5. **Run external evaluation** using the notebooks in `cross_dataset/`. If you want to reproduce inference without retraining, supply the corresponding pretrained checkpoints (for example, `best_model_12lead.pth`, `best_cnn_bilstm_12lead.pth`, and `best_rf_morph_all_leads_model.pkl`).
6. **Run post-hoc calibration** using `temperature_scaling/temperature_scaling.ipynb`, ensuring that the selected validation folds and the checkpoint configurations match those used in the thesis.

The notebooks document research experiments rather than a fully automated, environment-independent pipeline. Reproducing the exact results requires the original data selections, preprocessing choices, folds, model checkpoints, and software configuration. The original datasets are hosted by their respective providers. The displayed repository structure does not include the original ECG data or trained checkpoint files; these must be supplied separately for external evaluation.

## Interpretation and Limitations

- External results were obtained from **one selected checkpoint per model**, not repeated retraining across multiple external evaluations.
- Temperature scaling was fitted on the selected development validation fold, rather than on an additional independent calibration set. Improvements measured on that same fold are therefore not an independent test of calibration generalisation.
- ECE is an average over probability bins, while MCE measures the largest observed bin-level deviation; bins containing very few examples can produce unstable MCE values.
- The study is an evaluation of retrospective ECG data and is **not a clinical decision-support system**.

## Author

**Issa Rashdan**  
Master's thesis in Informatics, University of Oslo (UiO)  
Research environment: Simula Research Laboratory
