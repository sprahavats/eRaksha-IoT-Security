# eRaksha — Agentic AI-Powered IoT Security System

**Team:** Aegis  
**Author:** Spraha Vats  
**Institution:** Indian Institute of Technology Delhi

## Achievement

**7th Place Nationwide — e-Raksha National Cybersecurity Hackathon 2026**

Team Aegis secured **7th place among approximately 1,500 teams across India** in a 36-hour national cybersecurity hackathon conducted by the CyberPeace Foundation in collaboration with the Ministry of Home Affairs.

The hackathon challenged participants to develop cybersecurity solutions under a demanding 36-hour development timeline. Our team worked on **eRaksha, an agentic AI-powered IoT security system**, exploring device discovery, network anomaly detection, video analytics and deception-based threat intelligence.

The project was developed as a cybersecurity prototype focused on monitoring IoT environments and identifying potentially suspicious behaviour.

## Project Overview

eRaksha is a modular IoT security prototype combining device inventory, network-flow simulation, unsupervised anomaly detection, SQLite persistence and a local monitoring dashboard.

The current reproducible implementation focuses on synthetic network-flow analysis and simulated device discovery. It provides a foundation for evaluating anomaly detection and visualising potentially suspicious activity, while the broader hackathon concept explores multiple complementary security agents.

## Core Components

- **Device Discovery Agent:** Designed to identify and catalogue devices and their network characteristics.
- **Network Anomaly Detection Agent:** Uses an Isolation Forest model to identify unusual patterns in network-flow features.
- **Video Analytics Agent — proposed extension:** Explores camera-based object detection and behavioural analysis.
- **Deception Intelligence Agent — proposed extension:** Explores honeypot-based collection of suspicious interaction signals.
- **Monitoring Dashboard:** Displays device inventory, stored flows and flagged observations through a local Flask interface.

*Implementation note: the current tested codebase implements synthetic device discovery, network-flow simulation, anomaly scoring, database persistence and dashboard monitoring. The video analytics, honeypot and live-network capabilities are broader project directions and should not be interpreted as fully implemented features.*

## Technology Stack

- Python
- NumPy
- scikit-learn — Isolation Forest
- SQLite
- Flask
- pytest

## Current Prototype Features

- Reproducible generation of synthetic normal and suspicious network flows.
- Unsupervised anomaly detection trained on normal reference traffic.
- Persisted anomaly scores, flags and human-readable explanations.
- Device inventory with simulated/observed provenance labels.
- Local monitoring dashboard with device inventory and anomaly alerts.
- Automated tests for core functionality and dashboard endpoints.

## Evaluation

The detector is evaluated using held-out synthetic data with known labels. Metrics include precision, recall, F1 score and false-positive rate.

These results measure performance on the synthetic dataset only and do not establish equivalent performance on real-world IoT networks.

## Security and Limitations

- Synthetic traffic is explicitly labelled as simulated.
- Anomaly flags indicate unusual behaviour, not confirmed attacks.
- Live network discovery and real-world validation remain future work.
- The dashboard is intended for local development and binds to `127.0.0.1`.
- API keys, `.env` files, local databases and other sensitive information must not be committed to version control.

## Future Work

- Implement authorised, opt-in local-network discovery.
- Validate the detector using appropriately collected and labelled real IoT traffic.
- Explore video analytics and honeypot-based threat intelligence.
- Evaluate lightweight deployment on edge hardware.
- Improve alert prioritisation and per-device behavioural analysis.

## Project Status

A tested prototype for synthetic IoT-flow anomaly detection and local security monitoring, developed from the broader eRaksha hackathon concept.
