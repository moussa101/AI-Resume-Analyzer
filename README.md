# AI Resume Analyzer

A powerful, AI-powered tool that analyzes resumes against job descriptions to provide intelligent scoring, skill extraction, and detailed feedback. Now featuring enhanced profile analysis for GitHub and LinkedIn.

![AI Resume Analyzer Dashboard](https://github.com/user-attachments/assets/placeholder-image)

## Key Features

*   **Intelligent Matching**: Uses advanced NLP (spaCy + Sentence Transformers) to calculate semantic similarity scores between resumes and job descriptions.
*   **Skill Extraction**: Automatically identifies technical skills, programming languages, and tools from resumes.
*   **Keyword Analysis**: Highlights missing keywords and skills that are critical for the specific job role.
*   **Profile Analysis (NEW)**:
    *   **GitHub**: Extracts GitHub handles and uses the GitHub API to fetch rich profile data (stars, repos, followers, recent activity) and calculate a developer "Profile Score".
    *   **LinkedIn**: Identifies and links to LinkedIn profiles.
*   **Security & Anti-Cheat**: Detects invisible text, extensive copy-pasting, and other adversarial attempts to "game" the system.
*   **Modern UI**: Clean, Apple-inspired interface built with Next.js and Tailwind CSS, featuring drag-and-drop file upload and interactive results.
*   **File Support**: Supports PDF, DOCX, and TXT resume formats.

## Tech Stack

*   **Frontend**: Next.js 14, React, Tailwind CSS, TypeScript
*   **Backend**: NestJS, TypeScript, PostgreSQL (Prisma ORM)
*   **ML Service**: FastAPI, Python, spaCy, Sentence-Transformers, PyMuPDF
*   **Infrastructure**: Docker, Docker Compose

## Prerequisites

*   **Docker Desktop**: Ensure Docker and Docker Compose are installed and running.
*   **GitHub Token (Optional)**: For higher rate limits on GitHub profile analysis.

## Quick Start

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd AI-Resume-Analyzer
    ```

2.  **Environment Setup**:
    The project creates necessary `.env` files automatically, but you can configure them if needed.

    *   **GitHub Token (Recommended)**:
        Add your GitHub Personal Access Token to `ml_service/.env` or the root `.env` to increase API rate limits (from 60 to 5000 requests/hr).
        ```env
        GITHUB_TOKEN=your_github_token_here
        ```

3.  **Run with Docker**:
    Build and start all services with a single command:
    ```bash
    docker compose up --build
    ```

4.  **Access the Application**:
    *   **Frontend Dashboard**: [http://localhost:3001](http://localhost:3001)
    *   **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Usage Guide

1.  **Navigate to the Dashboard**: Open [http://localhost:3001](http://localhost:3001).
2.  **Upload Resume**: Drag and drop a PDF, DOCX, or TXT file, or click to select one.
3.  **Enter Job Description**: Paste the job description text for the role you are targeting.
4.  **Analyze**: Click the "Analyze Resume" button.
5.  **View Results**:
    *   **Match Score**: See how well the resume matches the job.
    *   **Profile Analysis**: View GitHub stats (repos, stars, followers) and distinct profile insights if a GitHub link is found.
    *   **Skills & Keywords**: Review found skills and identifying missing keywords.
    *   **Suggestions**: Read actionable feedback to improve the resume.

## Testing

The project includes a comprehensive test suite with real-world scenarios.

1.  **Run Automated Tests**:
    ```bash
    python3 test_data/real_world/run_tests.py
    ```
    This script tests the analyzer against varying candidate profiles (Senior SWE, Data Scientist, Junior Dev) and job descriptions (Google, Amazon, Meta) to verify scoring accuracy.

## Project Structure

```
AI-Resume-Analyzer/
├── frontend/             # Next.js Frontend application
├── backend/              # NestJS Backend API (Application Logic)
├── ml_service/           # Python/FastAPI ML Service (Analysis Core)
│   ├── analyzer.py       # Core NLP analysis logic
│   ├── profile_analyzer.py # GitHub/LinkedIn profile extraction
│   └── main.py           # API Endpoints
├── test_data/            # Test resumes and job descriptions
└── docker-compose.yml    # Docker orchestration
```

## Security Features

The analyzer includes specific checks to prevent common resume "hacks":
*   **Invisible Text Detection**: Flags text colored white or matching the background.
*   **Homoglyph Attacks**: Detects character substitution attempts.
*   **Copy-Paste Detection**: Flags unusually high 95%+ matches that suggest direct copying of the JD.

## License

This project is licensed under the MIT License.