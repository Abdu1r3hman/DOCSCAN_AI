# 🔮 Purple Vision OCR: Agentic Digitization System

A high-fidelity document digitization platform featuring a dual-phase architecture: Traditional local OCR and Autonomous Multi-Agent System (MAS) analysis.

## 🚀 Overview
Purple Vision OCR was developed as part of a **Professional Practices in IT (PPIT)** project to solve the limitations of static OCR systems. It transitions from simple text extraction to intelligent document synthesis.

### 💎 Key Features
*   **Phase 1 (Legacy Mode)**: High-speed local processing using **PaddleOCR** and **Tesseract**. Optimized for privacy and low latency.
*   **Phase 2 (Agentic Mode)**: An autonomous Multi-Agent System featuring:
    *   **Vision Extractor**: Analyzes layout and semantic structure.
    *   **QA Reviewer**: Self-critiques and corrects extraction errors.
    *   **Master Formatter**: Synthesizes high-fidelity MS Word documents.
*   **Premium Web UI**: A glassmorphic, ultra-modern interface built with Gradio 6.

## 🛠️ Technology Stack
- **Frontend**: Gradio (Custom CSS/JS)
- **OCR Engines**: PaddleOCR, Tesseract
- **Agentic Core**: OpenAI API (via OpenRouter), Python-docx
- **Deployment**: Hugging Face Spaces

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Purple-Vision-OCR.git
   cd Purple-Vision-OCR
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file and add your API key:
   ```env
   OPENROUTER_API_KEY=your_key_here
   ```

4. **Run Locally**:
   ```bash
   python app.py
   ```

## 📜 Project Context
This project was developed to demonstrate the evolution of AI in document processing, moving from rule-based extraction to reasoning-based synthesis.

---
*Developed for the NCEAC Course Assignment.*
