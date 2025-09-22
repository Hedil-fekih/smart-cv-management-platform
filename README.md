# Smart CV Management Platform

An AI-powered CV analysis platform built with Flask that helps students, graduates, and recruiters analyze and search CVs effectively.

## Features

- **AI CV Analysis**: Upload PDF CVs and get instant analysis with scoring
- **Smart Search**: Search candidates by skills, experience, and CV quality
- **Real-time Statistics**: Track platform usage and performance metrics
- **Professional Reports**: Download detailed analysis reports
- **Responsive Design**: Works on all devices and screen sizes

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Run the application:
   \`\`\`bash
   python app.py
   \`\`\`

4. Access the platform at `http://localhost:5000` or `http://your-ip:5000` for network access

## Network Access

The application is configured to be accessible from any network by running on `0.0.0.0:5000`. This means:

- **Local access**: `http://localhost:5000`
- **Network access**: `http://[your-computer-ip]:5000`
- **Mobile devices**: Can access via your computer's IP address on the same network

## Usage

### For Job Seekers:
1. Go to "Upload CV" page
2. Enter your name and email
3. Upload your PDF CV
4. Get instant AI analysis with improvement suggestions
5. Download your analysis report

### For Recruiters:
1. Go to "Search Profiles" page
2. Enter search criteria (skills, keywords, minimum score)
3. Browse candidate profiles
4. Contact candidates directly via email

## File Structure

\`\`\`
cv-analyzer-english/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   ├── index.html        # Homepage
│   ├── upload.html       # CV upload page
│   └── search.html       # CV search page
├── uploads/              # Uploaded CV files (created automatically)
└── cv_platform.db        # SQLite database (created automatically)
\`\`\`

## API Endpoints

- `POST /api/upload` - Upload and analyze CV
- `POST /api/search` - Search CVs with filters
- `GET /api/stats` - Get platform statistics
- `POST /api/download-report` - Generate analysis report

## Database Schema

The platform uses SQLite with two main tables:
- **users**: Store user information
- **cvs**: Store CV files and analysis results

## Security Notes

- File uploads are restricted to PDF files only
- File size limit: 16MB
- Secure filename handling
- Input validation on all forms

## Deployment

For production deployment:
1. Set `debug=False` in app.py
2. Use a production WSGI server like Gunicorn
3. Configure proper database (PostgreSQL recommended)
4. Set up SSL/HTTPS
5. Configure firewall rules for port 5000

## Support

This platform provides a complete CV management solution with AI analysis capabilities, accessible from any device on your network.
