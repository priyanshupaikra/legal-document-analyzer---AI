from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(filepath):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = Document(filepath)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_text_from_doc(filepath):
    """Extract text from DOC file (simplified)"""
    # For now, we'll treat DOC similar to DOCX
    # In a production environment, you might want to use antiword or similar
    return extract_text_from_docx(filepath)

def clean_json_response(response_text):
    """Clean and extract JSON from Gemini response"""
    # Remove markdown code block markers if present
    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]  # Remove ```json
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]  # Remove ```
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]  # Remove ```
    
    # Try to find JSON object in the response
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return cleaned

def analyze_legal_document(text):
    """Analyze legal document using Gemini AI"""
    if not model:
        return {"error": "Gemini API key not configured"}
    
    try:
        # Prompt for legal document analysis
        prompt = f"""
        You are a legal expert AI assistant. Analyze the following legal document and provide:
        1. A brief overall summary of the document (2-3 sentences)
        2. A list of key clauses with:
           - Clause title
           - Plain language summary (explain in simple terms what this clause means)
           - Risk level (High/Medium/Low) with explanation
           - Suggestions for improvement (if any)
        
        Document text:
        {text[:4000]}  # Limit text to avoid token limits
        
        IMPORTANT: Respond ONLY with valid JSON in this exact format:
        {{
            "document_summary": "Brief overall summary of the document",
            "clauses": [
                {{
                    "title": "Clause title",
                    "summary": "Plain language explanation",
                    "risk_level": "High/Medium/Low",
                    "risk_explanation": "Explanation of the risk",
                    "suggestions": "Suggestions for improvement or None"
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt, stream=False)
        
        # Try to parse the response as JSON
        try:
            # Clean the response text
            cleaned_response = clean_json_response(response.text)
            analysis_result = json.loads(cleaned_response)
            return analysis_result
        except json.JSONDecodeError as je:
            # If JSON parsing fails, return the raw response for debugging
            return {
                "error": "Failed to parse AI response",
                "document_summary": "Analysis completed but formatting issue occurred.",
                "clauses": [
                    {
                        "title": "Response Format Error",
                        "summary": "The AI response could not be formatted correctly.",
                        "risk_level": "Medium",
                        "risk_explanation": "There was an issue parsing the AI response.",
                        "suggestions": "Try re-uploading the document or contact support."
                    }
                ],
                "raw_response": response.text[:500] + "..." if len(response.text) > 500 else response.text
            }
    except Exception as e:
        return {
            "error": f"Error analyzing document: {str(e)}",
            "document_summary": "",
            "clauses": []
        }

def is_legal_question(question):
    """Check if the question is related to legal topics"""
    # For now, we'll allow all questions by returning True
    # In a production environment, you might want to implement content filtering
    return True

def answer_legal_question(question, document_context):
    """Answer legal questions about the document using Gemini AI"""
    if not model:
        return {"error": "Gemini API key not configured"}
    
    # Since we're allowing all questions now, we'll skip the legal topic check
    # The function name is kept for consistency with the existing code
    
    try:
        # Create a prompt that includes the document context and the user's question
        prompt = f"""
        You are a legal expert AI assistant helping a user understand a legal document. 
        Use the following document context to answer the user's question accurately:
        
        Document Summary: {document_context.get('summary', 'N/A')}
        
        Key Clauses:
        {json.dumps(document_context.get('clauses', []), indent=2)}
        
        User's Question: {question}
        
        Please provide a clear, concise, and helpful answer based on the document context.
        If the question cannot be answered with the given context, politely explain that.
        Do not make up information that is not in the document.
        """
        
        response = model.generate_content(prompt, stream=False)
        return {"response": response.text}
        
    except Exception as e:
        return {"error": f"Error processing your question: {str(e)}"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    if 'document' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['document']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext == 'pdf':
            document_text = extract_text_from_pdf(filepath)
        elif file_ext == 'docx':
            document_text = extract_text_from_docx(filepath)
        elif file_ext == 'doc':
            document_text = extract_text_from_doc(filepath)
        
        # Analyze document with Gemini AI
        analysis_result = analyze_legal_document(document_text)
        
        # For display purposes, limit the preview text
        preview_text = document_text[:500] + "..." if len(document_text) > 500 else document_text
        
        return render_template('result.html', filename=filename, preview=preview_text, analysis=analysis_result)
    else:
        flash('Invalid file type. Please upload a PDF, DOC, or DOCX file.')
        return redirect(url_for('home'))

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages about the legal document"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        document_context = data.get('document_context', {})
        
        # Process the message and get a response
        response = answer_legal_question(message, document_context)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/examples')
def examples():
    return render_template('examples.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)