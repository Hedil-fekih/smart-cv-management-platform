from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import PyPDF2
import json
from datetime import datetime
import sqlite3
import re
from textblob import TextBlob
import nltk
from collections import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class CVAnalyzer:
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'html', 'css', 'react', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'git', 'docker', 'kubernetes',
            'aws', 'azure', 'machine learning', 'data science', 'artificial intelligence',
            'project management', 'leadership', 'communication', 'teamwork', 'angular',
            'vue.js', 'php', 'c++', 'c#', '.net', 'spring', 'django', 'flask',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'tableau',
            'power bi', 'excel', 'photoshop', 'illustrator', 'figma', 'sketch'
        ]
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def extract_contact_info(self, text):
        """Extract contact information from CV text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        return {
            'email': emails[0] if emails else None,
            'phone': phones[0] if phones else None
        }
    
    def extract_skills(self, text):
        """Extract skills from CV text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_experience(self, text):
        """Extract work experience information"""
        experience_keywords = ['experience', 'work', 'employment', 'career', 'position', 'job', 'role']
        lines = text.split('\n')
        
        experience_sections = []
        capture_next = False
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in experience_keywords):
                capture_next = True
            elif capture_next and line.strip():
                if len(line.strip()) > 10:  # Reasonable length for experience entry
                    experience_sections.append(line.strip())
                    if len(experience_sections) >= 5:  # Limit to 5 entries
                        break
        
        return experience_sections
    
    def calculate_score(self, analysis_result):
        """Calculate CV score based on various factors"""
        score = 0
        
        # Contact information (20 points)
        if analysis_result['contact']['email']:
            score += 10
        if analysis_result['contact']['phone']:
            score += 10
        
        # Skills (40 points)
        skills_count = len(analysis_result['skills'])
        score += min(skills_count * 4, 40)
        
        # Experience (25 points)
        exp_count = len(analysis_result['experience'])
        score += min(exp_count * 5, 25)
        
        # Text quality (15 points)
        text_length = len(analysis_result['raw_text'])
        if text_length > 1000:
            score += 15
        elif text_length > 500:
            score += 12
        elif text_length > 200:
            score += 8
        elif text_length > 100:
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def generate_recommendations(self, analysis_result):
        """Generate improvement recommendations"""
        recommendations = []
        
        if not analysis_result['contact']['email']:
            recommendations.append("Add a professional email address")
        
        if not analysis_result['contact']['phone']:
            recommendations.append("Include your phone number")
        
        if len(analysis_result['skills']) < 5:
            recommendations.append("Add more relevant technical skills")
        
        if len(analysis_result['experience']) < 2:
            recommendations.append("Include more detailed professional experience")
        
        if len(analysis_result['raw_text']) < 500:
            recommendations.append("Expand your CV with more detailed information")
        
        if len(analysis_result['skills']) > 10:
            recommendations.append("Excellent! Your CV shows great skill diversity")
        
        if not recommendations:
            recommendations.append("Excellent CV! Consider adding quantified achievements")
        
        return recommendations
    
    def analyze_cv(self, pdf_path):
        """Main analysis function"""
        text = self.extract_text_from_pdf(pdf_path)
        
        analysis = {
            'raw_text': text,
            'contact': self.extract_contact_info(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'timestamp': datetime.now().isoformat()
        }
        
        analysis['score'] = self.calculate_score(analysis)
        analysis['recommendations'] = self.generate_recommendations(analysis)
        
        return analysis

# Database setup
def init_db():
    conn = sqlite3.connect('cv_platform.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  user_type TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # CVs table
    c.execute('''CREATE TABLE IF NOT EXISTS cvs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  filename TEXT NOT NULL,
                  original_filename TEXT NOT NULL,
                  analysis_result TEXT,
                  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/api/upload', methods=['POST'])
def upload_cv():
    try:
        if 'cv_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['cv_file']
        user_name = request.form.get('user_name', 'Anonymous')
        user_email = request.form.get('user_email', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            file.save(file_path)
            
            # Analyze CV
            analyzer = CVAnalyzer()
            analysis = analyzer.analyze_cv(file_path)
            
            # Save to database
            conn = sqlite3.connect('cv_platform.db')
            c = conn.cursor()
            
            # Insert user if not exists
            c.execute("INSERT OR IGNORE INTO users (name, email, user_type) VALUES (?, ?, ?)",
                     (user_name, user_email, 'student'))
            
            # Get user ID
            c.execute("SELECT id FROM users WHERE email = ?", (user_email,))
            user_result = c.fetchone()
            user_id = user_result[0] if user_result else None
            
            # Insert CV record
            c.execute("INSERT INTO cvs (user_id, filename, original_filename, analysis_result) VALUES (?, ?, ?, ?)",
                     (user_id, unique_filename, filename, json.dumps(analysis)))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'message': 'CV uploaded and analyzed successfully!'
            })
        
        return jsonify({'error': 'Please upload a PDF file'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_cvs():
    try:
        search_query = request.json.get('query', '').lower()
        skills_filter = request.json.get('skills', [])
        min_score = request.json.get('min_score', 0)
        
        conn = sqlite3.connect('cv_platform.db')
        c = conn.cursor()
        
        c.execute("""SELECT cvs.*, users.name, users.email 
                     FROM cvs 
                     JOIN users ON cvs.user_id = users.id""")
        
        results = []
        for row in c.fetchall():
            analysis = json.loads(row[4]) if row[4] else {}
            
            # Apply filters
            if analysis.get('score', 0) < min_score:
                continue
            
            if skills_filter:
                cv_skills = [skill.lower() for skill in analysis.get('skills', [])]
                if not any(skill.lower() in cv_skills for skill in skills_filter):
                    continue
            
            if search_query:
                searchable_text = (analysis.get('raw_text', '') + ' ' + 
                                 ' '.join(analysis.get('skills', []))).lower()
                if search_query not in searchable_text:
                    continue
            
            results.append({
                'id': row[0],
                'filename': row[3],
                'user_name': row[5],
                'user_email': row[6],
                'score': analysis.get('score', 0),
                'skills': analysis.get('skills', []),
                'uploaded_at': row[5]
            })
        
        conn.close()
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'success': True,
            'results': results[:20]  # Limit to 20 results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        conn = sqlite3.connect('cv_platform.db')
        c = conn.cursor()
        
        # Get total CVs
        c.execute("SELECT COUNT(*) FROM cvs")
        total_cvs = c.fetchone()[0]
        
        # Get total users
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        # Get average score
        c.execute("SELECT analysis_result FROM cvs WHERE analysis_result IS NOT NULL")
        scores = []
        for row in c.fetchall():
            try:
                analysis = json.loads(row[0])
                scores.append(analysis.get('score', 0))
            except:
                continue
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        conn.close()
        
        return jsonify({
            'total_cvs': total_cvs,
            'total_users': total_users,
            'average_score': round(avg_score, 1)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-report', methods=['POST'])
def download_report():
    """Generate and download CV analysis report"""
    try:
        analysis_data = request.json.get('analysis')
        if not analysis_data:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        # Generate HTML report
        report_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>CV Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #667eea; padding-bottom: 20px; }}
                .score {{ font-size: 3em; color: #667eea; font-weight: bold; }}
                .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #667eea; background: #f8fafc; }}
                .skills {{ display: flex; flex-wrap: wrap; gap: 10px; }}
                .skill {{ background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; }}
                .recommendations li {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CV Analysis Report</h1>
                <div class="score">{analysis_data.get('score', 0)}/100</div>
                <p>Generated on {datetime.now().strftime('%m/%d/%Y at %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Overall Score</h2>
                <p>Your CV received a score of <strong>{analysis_data.get('score', 0)}/100</strong>.</p>
                <p>{'Excellent work!' if analysis_data.get('score', 0) >= 80 else 'Good work, some improvements possible.' if analysis_data.get('score', 0) >= 60 else 'There is room for improvements.'}</p>
            </div>
            
            <div class="section">
                <h2>🛠️ Skills Detected</h2>
                <div class="skills">
                    {' '.join([f'<span class="skill">{skill}</span>' for skill in analysis_data.get('skills', [])]) if analysis_data.get('skills') else '<p>No technical skills detected</p>'}
                </div>
            </div>
            
            <div class="section">
                <h2>💼 Professional Experience</h2>
                <p><strong>{len(analysis_data.get('experience', []))}</strong> professional experience(s) detected</p>
                {'<ul>' + ''.join([f'<li>{exp}</li>' for exp in analysis_data.get('experience', [])[:3]]) + '</ul>' if analysis_data.get('experience') else '<p>No detailed experience found</p>'}
            </div>
            
            <div class="section">
                <h2>💡 Improvement Recommendations</h2>
                <ul class="recommendations">
                    {' '.join([f'<li>{rec}</li>' for rec in analysis_data.get('recommendations', [])]) if analysis_data.get('recommendations') else '<li>Keep up the excellent work!</li>'}
                </ul>
            </div>
            
            <div class="section">
                <h2>📞 Contact Information</h2>
                <p><strong>Email:</strong> {analysis_data.get('contact', {}).get('email', 'Not detected')}</p>
                <p><strong>Phone:</strong> {analysis_data.get('contact', {}).get('phone', 'Not detected')}</p>
            </div>
            
            <div class="section">
                <h2>📈 Tips to Improve Your Score</h2>
                <ul>
                    <li>Ensure your contact information is complete and visible</li>
                    <li>Clearly list your technical skills</li>
                    <li>Detail your professional experience with concrete examples</li>
                    <li>Use relevant keywords for your field</li>
                    <li>Quantify your achievements when possible</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return jsonify({
            'success': True,
            'report_html': report_html,
            'filename': f'cv_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/<int:candidate_id>')
def get_profile(candidate_id):
    try:
        conn = sqlite3.connect('cv_platform.db')
        c = conn.cursor()
        
        c.execute("""SELECT cvs.*, users.name, users.email 
                     FROM cvs 
                     JOIN users ON cvs.user_id = users.id 
                     WHERE cvs.id = ?""", (candidate_id,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        analysis = json.loads(result[4]) if result[4] else {}
        
        profile = {
            'id': result[0],
            'user_name': result[5],
            'user_email': result[6],
            'filename': result[3],
            'uploaded_at': result[5],
            'score': analysis.get('score', 0),
            'skills': analysis.get('skills', []),
            'experience': analysis.get('experience', []),
            'contact': analysis.get('contact', {}),
            'recommendations': analysis.get('recommendations', [])
        }
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Make accessible from any network
    app.run(debug=True, host='0.0.0.0', port=5000)
