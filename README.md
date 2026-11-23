ECG-Based Sleep Apnea Detection Using ECG-Derived Respiration (EDR)

Overview

Sleep apnea is a sleep-related breathing disorder characterized by repeated interruptions or reductions in breathing during sleep. These interruptions can affect oxygen levels, sleep quality, and cardiovascular activity.

This project explores the detection of sleep apnea using Electrocardiogram (ECG) signals and ECG-Derived Respiration (EDR). Instead of relying directly on respiratory sensors, respiratory information is extracted from variations in ECG signal characteristics.

The system analyzes ECG signals, extracts respiratory-related information, studies heart rate variability, and classifies signal segments into normal and suspected apnea conditions.

Objectives

- Process ECG signals using digital signal processing techniques.
- Extract ECG-derived respiration (EDR).
- Analyze respiration-related amplitude and frequency characteristics.
- Extract heart rate variability (HRV) features.
- Detect suspected apnea segments.
- Calculate Apnea-Hypopnea Index (AHI).
- Categorize apnea severity based on AHI.
- Compare detected results with reference annotations.

System Architecture

ECG Signal  
↓  
ECG Preprocessing and Filtering  
↓  
R-Peak Detection  
↓  
ECG-Derived Respiration (EDR) Extraction  
↓  
EDR Filtering  
↓  
Respiratory Amplitude and Frequency Analysis  
↓  
HRV Feature Extraction  
↓  
Apnea Detection  
↓  
AHI Calculation and Severity Classification  
↓  
CSV Report

Methodology

1. ECG Signal Acquisition

ECG recordings are obtained from the MIT-BIH Apnea-ECG Database.

The ECG signal represents the electrical activity of the heart and contains information about heart rhythm and respiratory-related modulation.

2. ECG Preprocessing

A bandpass filter is applied to remove unwanted frequency components and improve the signal quality.

Filtering is used to isolate relevant ECG components for R-peak detection and subsequent analysis.

3. R-Peak Detection

R-peaks are identified from the ECG signal using peak detection techniques.

The detected R-peaks are used to calculate:

- RR intervals
- Heart rate
- Mean RR interval
- SDNN

4. ECG-Derived Respiration (EDR)

Respiration influences ECG characteristics through several physiological mechanisms, including:

- Changes in heart rate during breathing
- Changes in cardiac electrical axis
- Changes in ECG morphology and amplitude

The variation in R-peak amplitudes is used to derive an EDR signal.

The extracted R-peak amplitudes are interpolated to generate a continuous respiration-related signal.

5. EDR Signal Processing

The EDR signal is filtered using a respiratory frequency band to retain respiration-related variations.

The Hilbert transform is used to calculate the amplitude envelope of the filtered EDR signal.

A moving average is applied to smooth the envelope and reduce rapid fluctuations.

6. Feature Extraction

The following features are analyzed:

-EDR amplitude envelope: Represents the variation in respiratory-related signal amplitude.
-Dominant respiratory frequency: Estimated using spectral analysis and Welch's power spectral density method.
-SDNN: Standard deviation of RR intervals, used as a measure of heart rate variability.

7. Apnea Detection
The processed EDR and HRV features are evaluated within fixed time windows.

Potential apnea segments are identified using conditions associated with:

- Reduced respiratory signal amplitude
- Abnormally low dominant respiratory frequency
- Changes in RR interval variability

The output of the algorithm is a segment-level classification of normal breathing or suspected apnea.

### 8. AHI Calculation

The Apnea-Hypopnea Index is calculated as:

AHI = Number of apnea events / Recording duration in hours

AHI is used to estimate the severity category.

| AHI (events/hour)  | Classification |
|--------------------|----------------|
| Less than 5        | Normal         |
| 5 to less than 15  | Mild           |
| 15 to less than 30 | Moderate       |
| 30 or greater      | Severe         |

These thresholds are commonly used for adult sleep apnea severity categories. This project's output is an experimental signal-processing estimate and is not a medical diagnosis.

Technologies Used:

- Python
- NumPy
- Pandas
- SciPy
- WFDB
- Matplotlib

Dataset:

MIT-BIH Apnea-ECG Database

The database contains ECG recordings and corresponding apnea annotations.

The annotations are used as reference labels for comparing algorithmic detection results.

Dataset source:

https://physionet.org/content/apnea-ecg/1.0.0/

The dataset is not included in this repository.

Output:

The program generates a CSV file containing information such as:

- Record name
- Start time
- End time
- Predicted classification
- EDR amplitude feature
- Dominant respiratory frequency
- SDNN
- Reference annotation, if available

It also displays a summary containing:

- Recording duration
- Predicted apnea segments
- AHI
- Severity category
- Mean RR interval
- SDNN

 Limitations:

- EDR is indirectly derived from ECG and may not accurately represent actual airflow.
- ECG signal noise can affect R-peak detection and EDR extraction.
- Fixed thresholds may not work consistently across all recordings.
- HRV changes are not specific to sleep apnea.
- A 60-second classification window does not accurately represent the timing and duration of individual clinical apnea events.
- The algorithm is experimental and has not been clinically validated.

Future Improvements:

- Adaptive thresholds for different ECG recordings.
- Improved R-peak detection.
- More accurate EDR extraction using multiple ECG features.
- Shorter sliding windows.
- Machine learning-based classification.
- Performance evaluation using sensitivity, specificity, precision, F1-score, and confusion matrices.
- Improved event-level apnea detection.

