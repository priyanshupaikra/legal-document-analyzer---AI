# ClauseIQ - Legal Document Analyzer

ClauseIQ is an AI-powered legal document analyzer that helps individuals with little to no legal background understand complex legal terms, highlight potential risks, and generate plain language summaries. Built with Python (Flask), Tailwind CSS, and the Gemini API.

## Features

- Upload legal documents (PDF, DOC, DOCX)
- AI-powered clause extraction
- Plain language summaries
- Risk flagging with explanations
- Interactive clause-by-clause analysis
- Responsive web interface

## Target Users

- Law students
- Startups
- Small businesses
- Anyone needing to understand legal documents quickly

## Technologies Used

- Python 3.x
- Flask (Web Framework)
- Google Gemini API (AI Analysis)
- Tailwind CSS (Styling)
- PyPDF2 (PDF Processing)
- python-docx (DOCX Processing)

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Google Gemini API Key

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ai_legal_document_analyzer
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Gemini API key:
   - Go to [Google AI Studio](https://aistudio.google.com/) and create an API key
   - Open the `.env` file and replace `your_api_key_here` with your actual API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

### Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

### Usage

1. Click "Upload Document" and select a legal document (PDF, DOC, or DOCX)
2. Wait for the AI analysis to complete
3. Review the clause-by-clause analysis with plain language summaries and risk assessments
4. Use the insights to better understand your legal document

## Project Structure

```
ai_legal_document_analyzer/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── README.md              # This file
│
├── templates/             # HTML templates
│   ├── base.html          # Base template with header/footer
│   ├── index.html         # Home page with upload form
│   └── result.html        # Analysis results page
│
├── static/                # Static assets
│   ├── css/               # CSS files
│   ├── js/                # JavaScript files
│   └── uploads/           # Uploaded documents (gitignored)
│
└── sample documents/      # Sample documents for testing
    ├── sample_nda.txt     # Sample NDA in text format
    ├── sample_nda.docx    # Sample NDA in DOCX format
    └── sample_nda.pdf     # Sample NDA in PDF format
```

## How It Works

1. **Document Upload**: Users upload legal documents in PDF, DOC, or DOCX format
2. **Text Extraction**: The application extracts text content from the document
3. **AI Analysis**: The extracted text is sent to Google's Gemini AI for analysis
4. **Clause Identification**: Gemini identifies key clauses in the document
5. **Plain Language Translation**: Complex legal terms are translated into simple language
6. **Risk Assessment**: Potential risks in each clause are flagged and explained
7. **Results Display**: The analysis is presented in an easy-to-understand format

## Example Documents

The application works best with:
- Non-Disclosure Agreements (NDAs)
- Employment Contracts
- Service Agreements
- Lease Agreements
- Terms of Service

## Sample Documents

This repository includes sample legal documents for testing:
- `sample_nda.txt` - A text version of an NDA
- `sample_nda.docx` - A DOCX version of an NDA
- `sample_nda.pdf` - A PDF version of an NDA

## Future Enhancements

- Document comparison features
- Export to PDF/Word reports
- Multi-language support
- Enhanced risk scoring algorithms
- Integration with document storage services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for powering the AI analysis
- Tailwind CSS for the responsive UI components
- Flask for the web framework
- PyPDF2 and python-docx for document processing
- ReportLab for PDF generation