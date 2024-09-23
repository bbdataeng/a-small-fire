
# a-small-fire

**a-small-fire** is a toolkit developed by the BBMRI-IT team to support the transformation step in the ETL process, converting datasets into FHIR® (Fast Healthcare Interoperability Resources) format.

The toolkit is based on the open-source [FHIR RESOURCES](https://github.com/nazrulworld/fhir.resources) library.

![workflow](https://github.com/bbdataeng/a-small-fhir/blob/simpler-fhir/figures/asmallfire.png)

---

## Basic Model

The input dataset must contain at least the following essential fields:


- **Sampling Date**
- **Donor Birth Date**
- **Diagnosis Age Donor**
- **Gender**
- **Date of Diagnosis**
- **Diagnose ICD-10**
- **Sample Type**
- **Storage Temperature**

Additionally, identifiers for the patient and sample are required:

- **Patient_ID**
- **Sample_ID**

---

## Main Modules

The toolkit consists of several specialized modules:

### **Conversion**
The primary module, which acts as an overall wrapper. It takes an Excel file (a classic dataset table) as input and creates a FHIR-structured JSON file, ready for upload to the Biobank Locator.

### **Configuration**
This module contains various configuration values, such as the organization ID and the Biobank Locator URL.

### **Normalization**
The normalization module maps non-compliant fields to normalized MIABIS fields.

### **Input-Model**
This module contains all possible values for the input, used for validation and normalization, based on the MIABIS CDM.

### **FHIR-Model**
A high-level converter that transforms the input dataset into FHIR format, according to [BBMRI.de implementation guide](https://samply.github.io/bbmri-fhir-ig/).

### **FHIR-Resources**
Used by the FHIR-MODEL module to map each field or entity to its corresponding FHIR structure.

---

## Requirements

To install the necessary dependencies, run:

```bash
pip install -r fhir_converter/requirements.txt
```

---

## Installation

Clone the repository with the following command:

```bash
git clone https://github.com/bbdataeng/a-small-fire.git
```

---

## Configuration Files

There are two main configuration files used by the toolkit:

- **`biobank_config.yml`**: Contains general configuration information, such as organization ID, collection ID, and server URL.
- **`mapping_config.yml`**: Defines the mapping of local data fields into MIABIS CDM fields.

