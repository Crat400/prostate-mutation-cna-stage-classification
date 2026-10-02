# Prostate Mutation CNA Stage Classification

## Overview

Machine learning project using the MSK 2024 prostate cancer cohort to classify Stage 1-3 vs Stage 4 disease. Compares somatic mutations, copy-number alterations (CNAs), and combined genomic features across multiple models to evaluate their relative predictive value for advanced prostate cancer.

This project investigates whether genomic alteration profiles can distinguish Stage 4 prostate cancer from Stage 1-3 disease using machine learning.

We will compare three genomic feature sets:
- Somatic mutations
- Copy-number alterations (CNAs)
- Combined mutations + CNAs

## Dataset

**Dataset:** Prostate Cancer (MSK, Clinical Cancer Research 2024)  
**Source:** cBioPortal  
**Study ID:** prostate_msk_2024

The cohort contains genomic and clinical data from approximately 2,260 prostate cancer samples.

For the primary analysis: (Samples with unknown or unavailable stage will be excluded)
- Stage 1-3: 943 samples
- Stage 4: 1,024 samples

## Problem

The goal is to determine whether genomic alteration patterns can distinguish Stage 4 from Stage 1-3 prostate cancer, and whether combining mutations and CNAs improves classification performance.

## Why It Matters

Advanced prostate cancer is associated with genomic changes that may differ from earlier-stage disease. Comparing mutations and CNAs may help identify which types of genomic alterations are most informative for advanced disease classification.

## Task Type

**Binary classification**
**Input:** Somatic mutations, CNAs, or combined genomic features  
**Target:** Stage 1-3 vs Stage 4 prostate cancer

## Planned Models

Each model will be evaluated using mutation-only, CNA-only, and combined feature sets (total of 6 models will be compared).
1. Logistic regression
2. Random forest

## Use of Generative AI Statement

Generative AI tools, including OpenAI ChatGPT, were used to support dataset selection and organization of the repository documentation.

## Licences

The code in this repository is licensed under the MIT License.

The project uses data obtained from the cBioPortal Public Datahub. The underlying data remain subject to the applicable cBioPortal and study-specific licensing and attribution requirements. The dataset itself is not distributed with this repository.

## CRediT Contributions

**Huibin Benny Ji (Crat400):** Model lead  
**Mehdi Haghi (mehdihaghi11-dev):** Data lead  
**Sachsin Sinnathurai (SachsinSinnathurai):** Writing lead  
**Parvinder Ahlawat (ParvinderAhlawat92):** Interface lead  
