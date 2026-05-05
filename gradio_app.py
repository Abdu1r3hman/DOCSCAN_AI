import gradio as gr
import os
import subprocess
import threading
import time
import uuid
from PIL import Image

# ==============================================================================
# ULTRA-PREMIUM "VIBE" UI CONFIGURATION
# ==============================================================================
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&family=Fira+Code&display=swap');

:root {
    --primary: #c084fc;
    --primary-glow: rgba(192, 132, 252, 0.5);
    --secondary: #6366f1;
    --accent: #f472b6;
    --bg-dark: #05020a;
    --glass-bg: rgba(15, 7, 26, 0.7);
    --glass-border: rgba(192, 132, 252, 0.2);
}

body {
    background-color: var(--bg-dark);
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(124, 58, 237, 0.1) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.1) 0%, transparent 40%);
    color: #e0d5f0;
    font-family: 'Outfit', sans-serif;
}

/* Glassmorphism Cards */
.glass-card {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 28px !important;
    padding: 30px !important;
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.glass-card:hover {
    border-color: rgba(192, 132, 252, 0.4) !important;
    box-shadow: 0 12px 60px 0 rgba(192, 132, 252, 0.1) !important;
}

/* Title Animation */
#title-container {
    text-align: center;
    padding: 60px 0;
    margin-bottom: 20px;
}

#title-container h1 {
    font-family: 'Space Grotesk', sans-serif;
    background: linear-gradient(90deg, #f472b6, #c084fc, #6366f1);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4.5rem;
    font-weight: 800;
    letter-spacing: -3px;
    animation: shine 5s linear infinite, float 6s ease-in-out infinite;
}

@keyframes shine {
    to { background-position: 200% center; }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* Premium Buttons */
.action-btn {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    border-radius: 16px !important;
    padding: 20px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    cursor: pointer !important;
}

.action-btn:hover {
    transform: scale(1.02) translateY(-2px) !important;
    box-shadow: 0 0 30px var(--primary-glow) !important;
}

.action-btn:active {
    transform: scale(0.98) !important;
}

/* Status Badges */
.status-badge {
    background: rgba(192, 132, 252, 0.1) !important;
    border: 1px solid var(--primary) !important;
    padding: 10px 20px !important;
    border-radius: 99px !important;
    color: var(--primary) !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    font-size: 0.9rem !important;
    letter-spacing: 1px;
    display: inline-block;
}

/* Customizing Input/Outputs */
.gradio-input, .gradio-output {
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.log-viewer textarea {
    background-color: rgba(10, 5, 20, 0.8) !important;
    color: #a78bfa !important;
    font-family: 'Fira Code', monospace !important;
    border-radius: 12px !important;
    border: 1px solid rgba(192, 132, 252, 0.1) !important;
    font-size: 0.9rem !important;
}

/* Animation for the "Digitizing" feel */
.scan-line {
    position: absolute;
    width: 100%;
    height: 2px;
    background: var(--primary);
    box-shadow: 0 0 15px var(--primary);
    top: 0;
    left: 0;
    z-index: 10;
    animation: scan 3s linear infinite;
    display: none;
}

@keyframes scan {
    0% { top: 0%; }
    100% { top: 100%; }
}
"""

# ==============================================================================
# OPTIMIZED ENGINE WRAPPERS
# ==============================================================================

def process_with_logs(image, mode, engine, lang, progress=gr.Progress(track_tqdm=True)):
    if image is None:
        yield "", "### ⚠️ Error: No image uploaded", "### ❌ Error", None
        return

    # Create unique session ID
    session_id = str(uuid.uuid4())[:8]
    temp_img_path = f"web_in_{session_id}.png"
    image.save(temp_img_path)
    
    logs = ""
    output_text = ""
    output_docx = ""
    
    # 1. UI Setup
    progress(0, desc="🌟 Awakening Vision Engines...")
    
    if mode == "Phase 2 (Agentic)":
        cmd = ["python", "-u", "agentic_pipeline.py", temp_img_path]
        output_docx = temp_img_path.replace(".png", "_agentic_output.docx")
        status_msg = "🛰️ AGENTIC WORKFLOW ACTIVE"
    else:
        doc_type = "handwritten" if engine == "Handwritten (Paddle)" else "printed"
        cmd = ["python", "-u", "ocr_pipeline.py", temp_img_path, "--type", doc_type, "--lang", lang]
        output_docx = temp_img_path.replace(".png", "_final.docx")
        status_msg = f"⚡ PHASE 1 ({doc_type.upper()})"

    # 2. Parallel Execution & Log Streaming
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True, 
        encoding='utf-8', 
        errors='replace',
        bufsize=1
    )
    
    capturing_final = False
    final_text_lines = []
    
    # Track progress based on output
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
            
        if line:
            line_clean = line.strip()
            if not line_clean: continue
            
            if "=== FINAL_OUTPUT_START ===" in line_clean:
                capturing_final = True
                progress(0.9, desc="✨ Polishing Document...")
                continue
            elif "=== FINAL_OUTPUT_END ===" in line_clean:
                capturing_final = False
                continue
                
            if capturing_final:
                final_text_lines.append(line_clean)
                output_text = "\n".join(final_text_lines)
            else:
                logs += f"[{time.strftime('%H:%M:%S')}] {line_clean}\n"
                
                # Intelligent Progress Logic
                if "Initializing" in line_clean: progress(0.1, desc="🚀 Initializing Agents...")
                if "PaddleOCR" in line_clean: progress(0.3, desc="🧠 Loading Paddle Models...")
                if "Tesseract" in line_clean: progress(0.3, desc="🧠 Calibrating Tesseract...")
                if "VisionExtractor" in line_clean: progress(0.5, desc="👁️ Analyzing Image Structure...")
                if "QAReviewer" in line_clean: progress(0.7, desc="🔍 Performing Quality Audit...")
                if "Formatter" in line_clean: progress(0.85, desc="✍️ Formatting Output...")
            
            yield logs, output_text, status_msg, None

    process.wait()
    
    # 3. Finalization Logic
    if process.returncode == 0:
        # Standardize output path search
        actual_output = None
        # Check standard names
        possible_files = [
            output_docx,
            temp_img_path.replace(".png", "_agentic_output.docx"),
            temp_img_path.replace(".png", "_final.docx"),
            "temp_input_agentic_output.docx",
            "temp_input_final.docx"
        ]
        for pf in possible_files:
            if os.path.exists(pf):
                actual_output = pf
                break
        
        if not output_text and mode == "Phase 1 (Traditional)":
             output_text = "### ✅ Processing Complete\n\nYour high-fidelity document has been synthesized. Use the download link below to retrieve the formatted MS Word file."

        yield logs, output_text, "✨ DIGITIZATION COMPLETE", actual_output
    else:
        yield logs, output_text, "❌ ENGINE FAILURE", None

# ==============================================================================
# FRONT-END ASSEMBLY
# ==============================================================================

with gr.Blocks(title="Purple Vision OCR") as demo:
    with gr.Column(elem_id="title-container"):
        gr.Markdown("# 🔮 PURPLE VISION OCR")
        gr.Markdown("### Next-Gen Document Digitization & Agentic Analysis")
    
    with gr.Row():
        # LEFT: CONTROLS
        with gr.Column(scale=4):
            with gr.Column(elem_classes="glass-card"):
                input_image = gr.Image(
                    label="Source Document", 
                    type="pil", 
                    elem_id="source-img",
                    height=400
                )
                
                with gr.Group():
                    mode_select = gr.Radio(
                        ["Phase 1 (Traditional)", "Phase 2 (Agentic)"], 
                        label="Digitization Strategy", 
                        value="Phase 1 (Traditional)",
                        info="Phase 1 uses local OCR; Phase 2 uses Autonomous AI Agents."
                    )
                    
                    with gr.Row():
                        engine_select = gr.Dropdown(
                            ["Handwritten (Paddle)", "Printed (Tess)"], 
                            label="Legacy Engine", 
                            value="Handwritten (Paddle)",
                            scale=2
                        )
                        lang_select = gr.Dropdown(
                            ["en", "ch"], 
                            label="Lang", 
                            value="en",
                            scale=1
                        )
                
                run_btn = gr.Button("⚡ START SYNTHESIS", elem_classes="action-btn")
        
        # RIGHT: RESULTS
        with gr.Column(scale=6):
            with gr.Column(elem_classes="glass-card"):
                with gr.Row():
                    status_label = gr.Markdown("### 🛰️ STATUS: IDLE", elem_classes="status-badge")
                
                with gr.Tabs():
                    with gr.TabItem("📄 Synthesized Output"):
                        output_display = gr.Markdown(
                            label="Preview", 
                            value="*The digitized text will materialize here...*"
                        )
                        gr.Markdown("---")
                        with gr.Row():
                            download_file = gr.File(
                                label="📥 Download MS Word Document", 
                                elem_id="download-box"
                            )
                            
                    with gr.TabItem("🤖 Agent Intelligence"):
                        log_display = gr.Textbox(
                            label="Neural Logs", 
                            lines=18, 
                            elem_classes="log-viewer",
                            placeholder="Awaiting input signals..."
                        )

    # Event Handlers
    run_btn.click(
        process_with_logs, 
        inputs=[input_image, mode_select, engine_select, lang_select], 
        outputs=[log_display, output_display, status_label, download_file]
    )

if __name__ == "__main__":
    # Use 0.0.0.0 to ensure accessibility in all environments
    demo.launch(server_name="0.0.0.0", server_port=7860, css=custom_css, theme=gr.themes.Default())
