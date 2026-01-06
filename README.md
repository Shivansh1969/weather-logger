#  Automated Weather Data Logger (MLOps Pipeline)

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-blue?logo=github-actions)
![Hugging Face](https://img.shields.io/badge/Data-Hugging_Face-yellow?logo=huggingface)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Active-success)

##  Overview

This repository hosts the **Automated Data Engineering** module of my **IoT-Enabled Weather Prediction MLOps Pipeline**.

It serves as a "CI/CD-style" data logger that automates the extraction of daily weather sensor data and maintains a continuous, live historical record. Instead of manual uploads, this system uses **GitHub Actions** to fetch real-time data from the **Open-Meteo API** and commits it directly to a **Hugging Face Dataset**.

This ensures that the downstream Machine Learning models (LSTM & SVM) always have access to the latest data for training and inference.

##  Key Features

* [cite_start]**Automated Ingestion:** Runs on a daily schedule using GitHub Actions CRON triggers[cite: 35].
* [cite_start]**API Integration:** Fetches precision weather data (temperature, humidity, pressure) from the Open-Meteo API[cite: 35].
* [cite_start]**Cloud Storage:** Automatically pushes and versions data to the Hugging Face Hub, treating data as code[cite: 35].
* **Zero-Maintenance:** Once deployed, the pipeline runs entirely serverless within the GitHub ecosystem.

## LINK
https://huggingface.co/datasets/Shivansh1969/pi-sensor-log

##  Architecture

```mermaid
graph LR
    A[GitHub Actions Trigger] -- Daily CRON --> B(Python Script)
    B -- Request Data --> C{Open-Meteo API}
    C -- JSON Response --> B
    B -- Process & Format --> D[Pandas DataFrame]
    D -- Push to Hub --> E[Hugging Face Dataset]
    E -- Syncs With --> F[ML Training Pipeline]
