# Neurofibromatosis Type 1: Clinical Symptoms of Familial and Sporadic Cases

> **Donated:** May 11, 2025

---

## Overview

A national NF1 database with **331 probands with tumors** (167 sporadic and 142 familial cases) was evaluated to support machine learning classification of familial vs. sporadic NF1 presentations based on clinical symptoms.

---

## Dataset Characteristics

| Property | Value |
|---|---|
| **Format** | Tabular |
| **Subject Area** | Health and Medicine |
| **Associated Task** | Classification |
| **Feature Type** | Real |
| **Instances** | 331 |
| **Features** | 20 |
| **Missing Values** | No (except Age of Mother, Age of Father, Age at First Diagnosis) |

---

## Introductory Paper

> *A machine learning approach for predicting familial and sporadic disease cases based on clinical symptoms: introduction of a new dataset*
>
> **Authors:** P. Sharafi, Hilal Arslan, S. Ersoy Evans, Ali Varan, Ş. Ayter
> **Year:** 2025
> **Published in:** Turkish Bulletin of Hygiene and Experimental Biology

---

## Variables Table

| Variable Name | Role | Type | Demographic | Missing Values |
|---|---|---|---|---|
| With Tumors | Target | Binary | — | No |
| Healthy | Feature | Binary | — | No |
| Age of Mother | Feature | Integer | Age | Yes |
| Age of Father | Feature | Integer | Age | Yes |
| Age at First Diagnosis | Feature | Integer | Age | Yes |
| Café au lait (CLS) | Feature | Binary | — | No |
| Axillary Freckles | Feature | Binary | — | No |
| Inguinal Freckles | Feature | Binary | — | No |
| Lisch Nodules | Feature | Binary | — | No |
| Dermal Neurofibromins | Feature | Binary | — | No |
| Plexiform Neurofibromins | Feature | Binary | — | No |
| Optic Glioma | Feature | Binary | — | No |
| Skeletal Dysplasia | Feature | Binary | — | No |
| Learning Disability | Feature | Binary | — | No |
| Hypertension | Feature | Binary | — | No |
| Astrocytoma | Feature | Binary | — | No |
| Hamartoma | Feature | Binary | — | No |
| Scoliosis | Feature | Binary | — | No |
| Other Symptoms | Feature | Binary | — | No |
| Case Type | Feature | Binary | — | No |

---

## Class Labels & Encodings

### Target Variable

| Variable | Value | Meaning |
|---|---|---|
| Tumour Case | `0` | Without Tumours |
| Tumour Case | `1` | With Tumours |

### Case Type

| Value | Meaning |
|---|---|
| `0` | Sporadic Case |
| `1` | Familial Case |

### Clinical Features (Binary: Absent / Present)

| Feature | `0` | `1` |
|---|---|---|
| Café au lait (CLS) | Absent | Present |
| Axillary Freckles | Absent | Present |
| Inguinal Freckles | Absent | Present |
| Lisch Nodules | Absent | Present |
| Dermal Neurofibromins | Absent | Present |
| Plexiform Neurofibromins | Absent | Present |
| Optic Glioma | Absent | Present |
| Skeletal Dysplasia | Absent | Present |
| Learning Disability | Absent | Present |
| Hypertension | Absent | Present |
| Astrocytoma | Absent | Present |
| Hamartoma | Absent | Present |
| Scoliosis | Absent | Present |

### Other Symptoms

| Value | Meaning |
|---|---|
| `0` | Absent |
| `1` | At least one of the following present: Epilepsy, Rhabdomyoma, Ganglioblastoma, MPNST, Leukaemia, Noonan/Watson/Myelodysplastic Syndrome, Cranial/Brain stem tumour |

---

*Dataset sourced from a national NF1 registry. Intended for supervised classification tasks in the health and medicine domain.*
