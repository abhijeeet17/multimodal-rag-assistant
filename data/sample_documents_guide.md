# Sample Documents Guide & Verification Prompt Checklist

To test the **Multimodal Document Intelligence & RAG Assistant**, place sample files into the `data/` directory or upload them directly via the UI dropzone:

```text
data/
├── invoice.pdf
├── annual_report.pdf
├── resume.pdf
└── financial_report.pdf
```

## Recommended Sample Test Questions

### 1. Invoices & Scanned Receipts (`invoice.pdf`)
* **Question**: *"What is the total invoice amount?"*
* **Expected Answer**: Retrieves invoice line items and totals with source citation (`invoice.pdf — Page 1`).

### 2. Annual Corporate Reports (`annual_report.pdf`)
* **Question**: *"What was the revenue in 2025?"*
* **Expected Answer**: Revenue breakdown figure with citation (`Annual_Report.pdf — Page 24`).

### 3. Resumes & CVs (`resume.pdf`)
* **Question**: *"What skills are mentioned in the resume?"*
* **Expected Answer**: Categorized technical and soft skills listed in the candidate profile.

### 4. Tabular & Salary Comparisons
* **Question**: *"Which employee has the highest salary?"*
* **Expected Answer**: Parses structured markdown table and identifies employee compensation.

### 5. Multi-Document Analysis
* **Question**: *"Compare revenue between 2024 and 2025."*
* **Expected Answer**: Cross-document vector retrieval pulling chunks from both 2024 and 2025 annual reports.
