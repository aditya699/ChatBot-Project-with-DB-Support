# Multi-Purpose Chainlit Assistant

A versatile ChatBot built with Chainlit and Claude that provides multiple services through an intuitive chat interface. The assistant combines health recommendations, company policy information, and ticket management systems in one application.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Feature Details](#feature-details)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [Requirements](#requirements)
- [Support](#support)
- [License](#license)

## Features

### 1. Multiple Chat Profiles
- **General Chat**: Open-ended conversation for any topic
- **Health Advisor**: Personalized health plan recommendations based on BMI
- **Company Policies**: Information retrieval from company documentation using RAG
- **Ticket Management**: Customer service ticket tracking and statistics

### 2. Key Capabilities
- BMI-based health plan recommendations
- RAG (Retrieval Augmented Generation) for company policy queries
- Ticket management system with status tracking
- Profile-specific conversations with natural language understanding

## Prerequisites

- Python 3.8 or higher
- Required API keys:
  - Anthropic API key (for Claude)
  - Google API key (for embeddings)
- Company policy documentation in PDF format

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_google_api_key
```

4. Place your company policy PDF file:
- Name it `company_policy.pdf`
- Put it in the project root directory

## Usage

1. Start the application:
```bash
chainlit run app.py
```

2. Access the chat interface at `http://localhost:8000`

3. Select a chat profile from the dropdown menu:
   - Each profile provides specialized functionality
   - Switch between profiles at any time

### Profile Usage Guide

#### General Chat
- Free-flowing conversation on any topic
- Example queries:
  - "How does machine learning work?"
  - "Tell me about the history of Rome"
  - "What are some good productivity tips?"

#### Health Advisor
- Request health plan recommendations by providing:
  - Height in meters
  - Weight in kilograms
- Example queries:
  - "I need a health plan. I'm 1.75m tall and weigh 70kg"
  - "Can you recommend a health plan? My height is 1.65m and weight is 65kg"
  - "What health plan would suit me? I'm 1.80m and 85kg"

#### Company Policies
- Query specific company policies and guidelines
- Example queries:
  - "What is the leave policy?"
  - "Tell me about the work from home policy"
  - "What are the expense reimbursement guidelines?"

#### Ticket Management
- Available ticket IDs: TKT001 to TKT010
- Example queries:
  - "Show me the status of ticket TKT001"
  - "What are the details for TKT005?"
  - "Give me the overall ticket statistics"
  - "How many tickets are currently open?"

## Project Structure

```
project/
├── app.py                 # Main application file
├── requirements.txt       # Project dependencies
├── .env                  # Environment variables
├── company_policy.pdf    # Company documentation
└── README.md             # Documentation file
```

## Feature Details

### Health Plan System
- Calculates BMI using height and weight
- Provides four plan types:
  1. Underweight Plan (BMI < 18.5)
  2. Healthy Weight Plan (BMI 18.5-24.9)
  3. Weight Management Plan (BMI 25-29.9)
  4. Comprehensive Health Plan (BMI ≥ 30)
- Each plan includes customized recommendations

### Company Policy RAG System
- Features:
  - PDF document processing
  - Semantic search using Google embeddings
  - Context-aware responses
  - Automatic chunking of documents
  - Relevance-based retrieval

### Ticket Management System
Tracks tickets with:
- Basic Information:
  - Ticket ID
  - Customer Name
  - Issue Type
- Status Tracking:
  - Open
  - In Progress
  - Resolved
  - Closed
- Additional Metrics:
  - Priority Levels
  - Creation Date
  - Resolution Time
  - Customer Satisfaction Score


## Error Handling

The application handles various error scenarios:

### User Input Errors
- Invalid ticket IDs return clear error messages
- Missing height/weight measurements prompt for input
- Malformed queries are met with helpful guidance

### System Errors
- API failures are gracefully handled
- Database connection issues show appropriate messages
- Document processing errors are properly managed

### Data Validation
- Input validation for numerical values
- Format checking for ticket IDs
- Data type verification for all inputs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add appropriate comments
- Include tests for new features
- Update documentation as needed

## Support

For support:
1. Check the existing documentation
2. Refer to the usage examples
3. Submit an issue in the repository
4. Contact the development team


## Acknowledgments

- Chainlit for the chat interface framework
- Anthropic for Claude AI capabilities
- Google for embedding capabilities
- The open-source community for various dependencies

---

