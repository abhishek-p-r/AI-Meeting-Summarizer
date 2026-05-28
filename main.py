import subprocess
import os
import gradio as gr
import requests
import json

OLLAMA_SERVER_URL = "http://localhost:11434"  # Replace this with your actual Ollama server URL if different
WHISPER_MODEL_DIR = "./whisper.cpp/models"  # Directory where whisper models are stored


def get_available_models() -> tuple[list[str], bool]:
    """
    Retrieves a list of all available models from the Ollama server and extracts the model names.
    Prepends 'Gemini (Google Cloud)' as the primary cloud option.

    Returns:
        A tuple of (model_names, is_connected).
    """
    default_models = ["Gemini (Google Cloud)"]
    try:
        response = requests.get(f"{OLLAMA_SERVER_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json()["models"]
            llm_model_names = default_models + [model["model"] for model in models]  # Extract model names
            return llm_model_names, True
        else:
            return default_models, True  # Return Gemini as online even if Ollama is off
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return default_models, True  # Return Gemini as online even if Ollama is off


def get_available_whisper_models() -> list[str]:
    """
    Retrieves a list of available Whisper models based on downloaded .bin files in the whisper.cpp/models directory.
    Filters out test models and only includes official Whisper models (e.g., base, small, medium, large).

    Returns:
        A list of available Whisper model names (e.g., 'base', 'small', 'medium', 'large-V3').
    """
    # List of acceptable official Whisper models
    valid_models = ["base", "small", "medium", "large", "large-V3"]

    # Get the list of model files in the models directory
    model_files = [f for f in os.listdir(WHISPER_MODEL_DIR) if f.endswith(".bin")]

    # Filter out test models and models that aren't in the valid list
    whisper_models = [
        os.path.splitext(f)[0].replace("ggml-", "")
        for f in model_files
        if any(valid_model in f for valid_model in valid_models) and "test" not in f
    ]

    # Remove any potential duplicates
    whisper_models = list(set(whisper_models))

    return whisper_models


def summarize_with_model(llm_model_name: str, context: str, text: str) -> str:
    """
    Uses a specified model on the Ollama server to generate a summary.
    Handles streaming responses by processing each line of the response.

    Args:
        llm_model_name (str): The name of the model to use for summarization.
        context (str): Optional context for the summary, provided by the user.
        text (str): The transcript text to summarize.

    Returns:
        str: The generated summary text from the model.
    """
    prompt = f"""You are an elite executive assistant and meeting summarization expert. Your task is to analyze the meeting transcript provided below and generate an EXTREMELY DETAILED, EXHAUSTIVE, COMPREHENSIVE, and premium-grade meeting summary. Do NOT write a brief summary; instead, expand extensively on every topic discussed to capture the maximum amount of detailed information possible.
 
    CRITICAL SUMMARY REQUIREMENT: Do NOT include any timestamps, time codes, or duration markers (e.g., `[00:01:15 -> 00:05:40]` or `[00:12]`) anywhere in the summary output. Write the summary chronologically as a flowing narrative, but completely omit time indicators.
 
    Optional Context provided by the user:
    ---
    {context if context else 'No additional context provided.'}
    ---
 
    Here is the full transcript:
    ---
    {text}
    ---
 
    Please format your response beautifully using clean Markdown with the following structured sections:
 
    1. **📅 OVERVIEW & CONTEXT**: A thorough, extensive paragraph summarizing the high-level purpose of the meeting, overall sentiment, and central theme. Explain the background details deeply.
    
    2. **🕒 CHRONOLOGICAL TIMELINE**: A highly detailed, step-by-step breakdown of the meeting's progression. For every logical topic or discussion change, write an extremely comprehensive, exhaustive, multi-sentence summary of what was discussed, debated, or explained. Provide deep context and exact details of all arguments, explanations, and explanations of technical features. Do NOT include any timestamps!
 
    3. **🎯 KEY DECISIONS MADE**: A detailed, comprehensive, bulleted list of all major decisions agreed upon during the meeting, expanding on the background and details of each decision. Do NOT include any timestamps or timing codes!
 
    4. **📝 ACTION ITEMS & ASSIGNMENTS**: An actionable list of tasks assigned, with designated owners (if mentioned) and explicit deadlines. Explain each action item in detail. Format as:
       - `[ ] [Owner Name] Task Description` (Do NOT include any timestamps or timing tags!)
 
    Make the summary extremely comprehensive, exhaustive, highly detailed, verbose, and professional. Capture every single nuance of the conversation in full depth while strictly keeping timestamps out of the summary!"""

    headers = {"Content-Type": "application/json"}
    data = {"model": llm_model_name, "prompt": prompt}

    response = requests.post(
        f"{OLLAMA_SERVER_URL}/api/generate", json=data, headers=headers, stream=True, timeout=15
    )

    if response.status_code == 200:
        full_response = ""
        try:
            # Process the streaming response line by line
            for line in response.iter_lines():
                if line:
                    # Decode each line and parse it as a JSON object
                    decoded_line = line.decode("utf-8")
                    json_line = json.loads(decoded_line)
                    # Extract the "response" part from each JSON object
                    full_response += json_line.get("response", "")
                    # If "done" is True, break the loop
                    if json_line.get("done", False):
                        break
            return full_response
        except json.JSONDecodeError:
            print("Error: Response contains invalid JSON data.")
            return f"Failed to parse the response from the server. Raw response: {response.text}"
    else:
        raise Exception(
            f"Failed to summarize with model {llm_model_name}: {response.text}"
        )


# --- Google Gemini API Integration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def summarize_with_gemini(context: str, transcript: str) -> str:
    """
    Generates a highly detailed, premium, impactful, and timestamped summary using Google Gemini API.
    """
    prompt = f"""You are an elite executive assistant and meeting summarization expert. Your task is to analyze the meeting transcript provided below and generate an EXTREMELY DETAILED, EXHAUSTIVE, COMPREHENSIVE, and premium-grade meeting summary. Do NOT write a brief summary; instead, expand extensively on every topic discussed to capture the maximum amount of detailed information possible.
 
    CRITICAL SUMMARY REQUIREMENT: Do NOT include any timestamps, time codes, or duration markers (e.g., `[00:01:15 -> 00:05:40]` or `[00:12]`) anywhere in the summary output. Write the summary chronologically as a flowing narrative, but completely omit time indicators.
 
    Optional Context provided by the user:
    ---
    {context if context else 'No additional context provided.'}
    ---
 
    Here is the transcript:
    ---
    {transcript}
    ---
 
    Please format your response beautifully using clean Markdown with the following structured sections:
 
    1. **📅 EXECUTIVE OVERVIEW & CONTEXT**: A thorough, professional, and extensive paragraph summarizing the high-level purpose of the meeting, overall tone, and central themes. Make it highly engaging, deep, and impactful.
    
    2. **🕒 DETAILED CHRONOLOGICAL TIMELINE**: A highly detailed, step-by-step breakdown of the meeting's progression. For every logical topic or discussion change, write an extremely comprehensive, exhaustive, multi-sentence summary of what was discussed, debated, or explained. Capture key details, numbers, arguments, technical specifications, and specific references. Do NOT include any timestamps!
 
    3. **🎯 KEY DECISIONS MADE**: A detailed, comprehensive, bulleted list of all major decisions agreed upon during the meeting, expanding fully on the details and context of each decision. Do NOT include any timestamps!
 
    4. **📝 ACTION ITEMS & ASSIGNMENTS**: An actionable list of tasks assigned, with designated owners (if mentioned) and explicit deadlines. Explain each action item in detail. Format as:
       - `[ ] [Owner Name] Task Description` (Do NOT include any timestamps or timing tags!)
 
    Make the summary extremely comprehensive, exhaustive, highly detailed, verbose, and professional. Capture every single nuance of the conversation in full depth while strictly keeping timestamps out of the summary!"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Gemini API Error: {response.text}")
    except Exception as e:
        raise RuntimeError(f"Failed to generate summary with Gemini: {str(e)}") from e


def elaborate_transcript_with_gemini(transcript: str) -> str:
    """
    Uses Google Gemini API to clean up, structure, and format a raw Whisper transcript,
    preserving exact timestamps while making the transcript professional, detailed, and complete.
    """
    prompt = f"""You are a professional, elite-level meeting transcriptionist and conversational analyst. You are given a raw Whisper meeting transcript with timestamps.
    Your task is to refine, elaborate, and format this transcript to be highly professional, polished, and comprehensive, while strictly maintaining the timing reference on every single line.

    CRITICAL REFINEMENT INSTRUCTIONS:
    1. For every single line in the raw transcript, you MUST keep the timestamp bracket (e.g., `[00:00:12.000 -> 00:00:15.000]`) followed immediately by the fully corrected, punctuated, and contextually elaborated spoken text.
    2. Contextually elaborate and fix speech-to-text spelling errors, grammatical mistakes, or garbled/incomplete words. Use the conversation's context to intelligently fill in any transcription gaps, technical jargon, or acronyms so the transcript is complete and highly informative.
    3. Do NOT merge separate timed segments into single massive paragraphs that lack individual timing. Each line of information must keep its timing!
    4. Deduced Speaker Labels: When possible, identify speaker transitions or speaker names from the conversation and insert them next to the timestamp (e.g., `[00:00:12.000 -> 00:00:15.000] Speaker A: Hello...`).
    5. The final output must be extremely detailed, complete, professional, and visually spectacular. Do NOT shorten, summarize, or skip any parts of the spoken content!

    Here is the raw transcript:
    ---
    {transcript}
    ---

    Please output the beautifully formatted, clean, and detailed transcript with the corresponding timestamps on every line:"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Gemini API Error: {response.text}")
    except Exception as e:
        raise RuntimeError(f"Failed to elaborate transcript with Gemini: {str(e)}") from e


def preprocess_audio_file(audio_file_path: str) -> str:
    """
    Converts the input audio file to a WAV format with 16kHz sample rate and mono channel.
    Optimized with -vn to discard video streams, and list-based subprocess to prevent permission/shell errors.
    Bypasses OS temp locks by copying the file locally.
    """
    # Create a local safe copy to bypass any Gradio/OS sharing locks on the temp folder
    local_temp_path = os.path.join(os.getcwd(), f"temp_input_{os.path.basename(audio_file_path)}")
    try:
        import shutil
        shutil.copy2(audio_file_path, local_temp_path)
    except Exception as copy_err:
        print(f"Warning: Local file copy failed: {copy_err}. Attempting to use original path.")
        local_temp_path = audio_file_path

    output_wav_file = os.path.join(os.getcwd(), f"converted_{os.path.splitext(os.path.basename(audio_file_path))[0]}.wav")

    # Safe list-based execution to prevent escape/permission issues on Windows
    cmd = [
        "ffmpeg",
        "-y",
        "-i", local_temp_path,
        "-vn",
        "-ar", "16000",
        "-ac", "1",
        output_wav_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
    finally:
        # Clean up the local locked-bypass copy immediately
        if local_temp_path != audio_file_path and os.path.exists(local_temp_path):
            try:
                os.remove(local_temp_path)
            except Exception as e:
                print(f"Warning: Could not remove local temp copy: {e}")

    return output_wav_file


def translate_and_summarize(
    audio_file_path: str, context: str, whisper_model_name: str, llm_model_name: str
) -> tuple[str, str, str]:
    """
    Translates the audio file into text using the whisper.cpp model and generates a summary using Ollama.
    Also provides the transcript file for download.

    Args:
        audio_file_path (str): Path to the input audio file.
        context (str): Optional context to include in the summary.
        whisper_model_name (str): Whisper model to use for audio-to-text conversion.
        llm_model_name (str): Model to use for summarizing the transcript.

    Returns:
        tuple[str, str, str]: A tuple containing the summary, full transcript, and the path to the transcript file for download.
    """
    output_file = "output.txt"

    if not audio_file_path:
        print("Warning: No audio or video file provided!")
        return (
            "⚠️ Please upload or record an audio or video file first before generating a summary!",
            "⚠️ No transcription available because no audio or video file was provided.",
            None
        )

    print("Processing audio file:", audio_file_path)

    # Convert the input file to WAV format if necessary
    audio_file_wav = preprocess_audio_file(audio_file_path)

    print("Audio preprocessed:", audio_file_wav)

    # Call the whisper.cpp binary
    whisper_executable = "whisper.cpp\\whisper-cli.exe" if os.name == 'nt' else "./whisper.cpp/whisper-cli"

    # Check if executable exists before running
    if not os.path.exists(whisper_executable):
        raise FileNotFoundError(
            f"Whisper executable not found at: {whisper_executable}. "
            "Please build whisper.cpp or install it correctly."
        )

    # Optimize thread usage dynamically based on available CPU cores
    threads = os.cpu_count() or 4
    whisper_args = [
        whisper_executable,
        "-m", f"whisper.cpp/models/ggml-{whisper_model_name}.bin",
        "-f", audio_file_wav,
        "-t", str(threads)
    ]
    
    print(f"Running Whisper transcription with {threads} threads...")
    try:
        with open(output_file, "w", encoding="utf-8") as f_out:
            subprocess.run(
                whisper_args,
                stdout=f_out,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
    except subprocess.CalledProcessError as e:
        print("Whisper.cpp failed with exit code:", e.returncode)
        print("Whisper.cpp error output:", e.stderr)
        raise RuntimeError(f"Whisper.cpp transcription failed: {e.stderr}") from e

    print("Whisper.cpp executed successfully")

    # Read the output from the transcript
    with open(output_file, "r", encoding="utf-8", errors="replace") as f:
        transcript = f.read()

    # Save the transcript to a downloadable file
    transcript_file = "transcript.txt"
    with open(transcript_file, "w", encoding="utf-8") as transcript_f:
        transcript_f.write(transcript)

    # ALWAYS elaborate the transcript first using Gemini API (with raw transcript as fallback)
    print("Elaborating transcript with Gemini API...")
    try:
        elaborated_transcript = elaborate_transcript_with_gemini(transcript)
        transcript = elaborated_transcript
        print("Transcript successfully elaborated.")
    except Exception as e:
        print(f"Warning: Gemini transcript elaboration failed: {str(e)}. Using raw transcript.")

    # Re-write the beautifully elaborated (or raw fallback) transcript to file
    with open(transcript_file, "w", encoding="utf-8") as transcript_f:
        transcript_f.write(transcript)

    # Now generate the summary using the chosen LLM model
    if llm_model_name == "Gemini (Google Cloud)":
        try:
            print("Generating detailed, impactful summary with Gemini...")
            summary = summarize_with_gemini(context, transcript)
        except Exception as e:
            summary = f"Gemini API Error: {str(e)}\n\nPlease verify your internet connection and API key."
    elif llm_model_name == "ollama not running" or not llm_model_name:
        # Fallback to Gemini if Ollama is not running
        try:
            print("Ollama is not running. Using Gemini API as a fallback to summarize...")
            summary = summarize_with_gemini(context, transcript)
            summary = "✨ *Note: Summarized using Google Gemini API fallback as local Ollama was not active.*\n\n" + summary
        except Exception as e:
            summary = (
                f"Warning: Ollama is not running locally, and Gemini API fallback failed: {str(e)}\n\n"
                "To enable local summarization, please install Ollama (https://ollama.com/) and run a model."
            )
    else:
        try:
            print(f"Generating summary with local Ollama model: {llm_model_name}...")
            summary = summarize_with_model(llm_model_name, context, transcript)
        except Exception as e:
            # Fallback to Gemini if local model fails
            try:
                print(f"Ollama execution failed ({str(e)}). Falling back to Gemini API...")
                summary = summarize_with_gemini(context, transcript)
                summary = f"✨ *Note: Local model '{llm_model_name}' failed. Automatically fell back to Google Gemini API.*\n\n" + summary
            except Exception as gem_e:
                summary = f"Summarization failed under both local Ollama and Gemini API.\nLocal Error: {str(e)}\nGemini Error: {str(gem_e)}"

    # Clean up temporary files
    try:
        os.remove(audio_file_wav)
        os.remove(output_file)
    except Exception as e:
        print(f"Warning during file cleanup: {e}")

    # Return the summary, the transcript, and the downloadable link for the transcript
    return summary, transcript, transcript_file


# Gradio interface
def gradio_app(
    audio, context: str, whisper_model_name: str, llm_model_name: str
) -> tuple[str, str, str]:
    """
    Gradio application to handle file upload, model selection, and summary generation.

    Args:
        audio: The uploaded audio file.
        context (str): Optional context provided by the user.
        whisper_model_name (str): The selected Whisper model name.
        llm_model_name (str): The selected language model for summarization.

    Returns:
        tuple[str, str, str]: A tuple containing the summary text, transcript text, and a downloadable transcript file.
    """
    return translate_and_summarize(audio, context, whisper_model_name, llm_model_name)


# Main function to launch the Gradio interface
if __name__ == "__main__":
    # Retrieve available models for Gradio dropdown input
    ollama_models, ollama_connected = get_available_models()
    whisper_models = get_available_whisper_models()

    whisper_val = whisper_models[0] if whisper_models else None
    ollama_val = ollama_models[0] if ollama_models else None

    def refresh_ollama_models():
        """Re-check Ollama server and return updated model list."""
        models, connected = get_available_models()
        if connected:
            return gr.update(choices=models, value=models[0] if models else None)
        return gr.update(choices=["ollama not running"], value="ollama not running")

    custom_css = """
    /* ===== Global & Typography ===== */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

   /* ========================= */
/* BACKGROUND */
/* ========================= */

body {
    background: linear-gradient(
        135deg,
        #fdfbfb 0%,
        #ebedee 100%
    ) !important;

    background-size: 400% 400% !important;

    animation: gradientBG 15s ease infinite !important;

    background-attachment: fixed !important;
}

body.dark {
    background: linear-gradient(
        135deg,
        #09090b 0%,
        #18181b 100%
    ) !important;

    background-size: 400% 400% !important;

    animation: gradientBG 15s ease infinite !important;

    background-attachment: fixed !important;
}

@keyframes gradientBG {

    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
}

/* ========================= */
/* CONTAINER */
/* ========================= */

.gradio-container {
    font-family: 'Outfit', 'Inter', sans-serif !important;

    max-width: 1200px !important;

    margin: 0 auto !important;
}

/* ========================= */
/* DASHBOARD */
/* ========================= */

.dashboard-container {

    text-align: center;

    padding: 8vh 20px;

    animation: fadeIn 1s cubic-bezier(
        0.25,
        0.8,
        0.25,
        1
    );

    min-height: 85vh;

    display: flex;

    flex-direction: column;

    justify-content: center;

    align-items: center;
}

@keyframes fadeIn {

    from {
        opacity: 0;
        transform: translateY(30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.dashboard-title {

    font-size: clamp(
        3rem,
        6vw,
        5rem
    ) !important;

    font-weight: 800 !important;

    background: linear-gradient(
        135deg,
        #ff007f 0%,
        #7928ca 100%
    );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

    background-clip: text;

    margin-bottom: 24px !important;

    letter-spacing: -2px;

    line-height: 1.1;
}

body.dark .dashboard-title {

    background: linear-gradient(
        to right,
        #00f2fe 0%,
        #4facfe 100%
    );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

    background-clip: text;
}

.dashboard-subtitle {

    font-size: clamp(
        1.1rem,
        2vw,
        1.4rem
    ) !important;

    color: #52525b;

    max-width: 700px;

    margin: 0 auto 50px auto !important;

    line-height: 1.6;

    font-weight: 400;
}

body.dark .dashboard-subtitle {
    color: #a1a1aa;
}

/* ========================= */
/* INFO GRID */
/* ========================= */

.info-grid {

    display: flex;

    justify-content: center;

    gap: 30px;

    margin-bottom: 50px;

    flex-wrap: wrap;

    width: 100%;

    max-width: 1100px;
}

.info-card {

    background: rgba(
        255,
        255,
        255,
        0.6
    );

    padding: 40px 30px;

    border-radius: 24px;

    flex: 1;

    min-width: 280px;

    border: 1px solid rgba(
        255,
        255,
        255,
        0.8
    );

    text-align: left;

    box-shadow:
        0 20px 40px rgba(
            0,
            0,
            0,
            0.05
        );

    backdrop-filter: blur(20px);

    -webkit-backdrop-filter: blur(20px);

    transition:
        all 0.4s cubic-bezier(
            0.25,
            0.8,
            0.25,
            1
        );

    position: relative;

    overflow: hidden;
}

body.dark .info-card {

    background: rgba(
        24,
        24,
        27,
        0.6
    );

    border: 1px solid rgba(
        255,
        255,
        255,
        0.05
    );

    box-shadow:
        0 20px 40px rgba(
            0,
            0,
            0,
            0.4
        );
}

.info-card::before {

    content: '';

    position: absolute;

    top: 0;
    left: 0;
    right: 0;

    height: 4px;

    background: linear-gradient(
        90deg,
        #ff007f,
        #7928ca
    );

    opacity: 0;

    transition: opacity 0.4s ease;
}

body.dark .info-card::before {

    background: linear-gradient(
        90deg,
        #00f2fe,
        #4facfe
    );
}

.info-card:hover {

    transform: translateY(-10px);

    box-shadow:
        0 30px 60px rgba(
            0,
            0,
            0,
            0.1
        );
}

body.dark .info-card:hover {

    box-shadow:
        0 30px 60px rgba(
            0,
            0,
            0,
            0.6
        );
}

.info-card:hover::before {
    opacity: 1;
}

.info-card h4 {

    margin-top: 0;

    font-size: 1.4rem;

    color: #18181b;

    margin-bottom: 16px;

    font-weight: 700;
}

body.dark .info-card h4 {
    color: #f4f4f5;
}

.info-card p {

    margin: 0;

    font-size: 1.05rem;

    color: #52525b;

    line-height: 1.6;
}

body.dark .info-card p {
    color: #a1a1aa;
}

/* ========================= */
/* ENTER BUTTON */
/* ========================= */

.enter-btn-container {

    display: flex;

    justify-content: center;

    margin-top: 10px;

    width: 100%;
}

.enter-btn {

    background: linear-gradient(
        135deg,
        #7928ca 0%,
        #ff007f 100%
    ) !important;

    border: none !important;

    color: white !important;

    font-size: 1.5rem !important;

    font-weight: 600 !important;

    padding: 20px 60px !important;

    border-radius: 50px !important;

    cursor: pointer !important;

    transition:
        all 0.3s ease !important;

    max-width: 400px !important;

    position: relative;

    overflow: hidden;

    z-index: 1;
}

body.dark .enter-btn {

    background: linear-gradient(
        135deg,
        #00f2fe 0%,
        #4facfe 100%
    ) !important;
}

.enter-btn:hover {

    transform:
        translateY(-5px)
        scale(1.05) !important;
}

/* ========================= */
/* THEME TOGGLE */
/* ========================= */

.theme-toggle-container {

    position: fixed !important;

    top: 2px !important;
    right: 2px !important;

    z-index: 999999 !important;

    width: 28px !important;
    height: 28px !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    margin: 0 !important;

    padding: 0 !important;

    pointer-events: none !important;

    background: transparent !important;
}

.theme-toggle-container * {
    margin: 0 !important;
    padding: 0 !important;
}

.theme-toggle-btn {

    pointer-events: auto !important;

    width: 22px !important;
    height: 22px !important;

    min-width: 22px !important;
    min-height: 22px !important;

    max-width: 22px !important;
    max-height: 22px !important;

    border-radius: 50% !important;

    font-size: 10px !important;

    line-height: 1 !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    background: rgba(
        255,
        255,
        255,
        0.16
    ) !important;

    border: 1px solid rgba(
        255,
        255,
        255,
        0.2
    ) !important;

    color: #18181b !important;

    box-shadow:
        0 1px 4px rgba(
            0,
            0,
            0,
            0.08
        ) !important;

    backdrop-filter: blur(5px);

    -webkit-backdrop-filter: blur(5px);

    transition:
        all 0.15s ease !important;
}

body.dark .theme-toggle-btn {

    background: rgba(
        0,
        0,
        0,
        0.28
    ) !important;

    border: 1px solid rgba(
        255,
        255,
        255,
        0.05
    ) !important;

    color: #f4f4f5 !important;
}

.theme-toggle-btn:hover {

    transform:
        scale(1.03) !important;
}

body.dark .theme-toggle-btn:hover {

    background: rgba(
        30,
        41,
        59,
        0.75
    ) !important;
}
 
    /* ===== Main App View Enhancements ===== */
    .hero-header { text-align: center; padding: 40px 20px 20px 20px; animation: fadeIn 0.5s ease-in-out;}
    .hero-header h1 { font-size: clamp(2rem, 4vw, 3.5rem) !important; font-weight: 800 !important; background: linear-gradient(135deg, #7928ca 0%, #ff007f 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 12px !important; letter-spacing: -1px;}
    body.dark .hero-header h1 { background: linear-gradient(to right, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;}
    .hero-header h3 { font-weight: 400 !important; color: #52525b; font-size: 1.2rem !important; max-width: 700px; margin: 0 auto !important; }
    body.dark .hero-header h3 { color: #a1a1aa; }
    
    .status-card { border-radius: 16px !important; padding: 16px 24px !important; margin: 15px auto 25px auto !important; font-size: 1rem; text-align: center; max-width: 800px; font-weight: 600; backdrop-filter: blur(10px);}
    .status-connected { background: rgba(16, 185, 129, 0.1) !important; border: 1px solid rgba(16, 185, 129, 0.3) !important; color: #059669 !important; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.15) !important;}
    body.dark .status-connected { background: rgba(16, 185, 129, 0.15) !important; color: #34d399 !important; border-color: rgba(52, 211, 153, 0.3) !important; }
    
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    body.dark @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
        100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
    }
    .status-connected::before {
        content: '';
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #10b981;
        margin-right: 10px;
        animation: pulse-glow 2s infinite;
    }
    body.dark .status-connected::before {
        background-color: #34d399;
    }
    
    .status-disconnected { background: rgba(244, 63, 94, 0.1) !important; border: 1px solid rgba(244, 63, 94, 0.3) !important; color: #e11d48 !important; box-shadow: 0 8px 20px rgba(244, 63, 94, 0.15) !important;}
    body.dark .status-disconnected { background: rgba(244, 63, 94, 0.15) !important; color: #fb7185 !important; border-color: rgba(251, 113, 133, 0.3) !important; }
    
    .steps-bar { text-align: center; padding: 10px 0 35px 0; color: #71717a; font-size: 1rem; font-weight: 500; letter-spacing: 0.5px;}
    body.dark .steps-bar { color: #a1a1aa; }
    
    .input-panel, .output-panel { 
        border-radius: 24px !important; 
        padding: 30px !important; 
        background: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.9) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        transition: all 0.3s ease;
    }
    body.dark .input-panel, body.dark .output-panel {
        background: rgba(24, 24, 27, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
    }
    
    .generate-btn { background: linear-gradient(135deg, #7928ca 0%, #ff007f 100%) !important; border: none !important; color: white !important; font-weight: 700 !important; font-size: 1.25rem !important; padding: 18px 24px !important; border-radius: 20px !important; cursor: pointer !important; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; width: 100%; margin-top: 20px; box-shadow: 0 10px 25px rgba(255, 0, 127, 0.3) !important;}
    body.dark .generate-btn { background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; box-shadow: 0 10px 25px rgba(0, 242, 254, 0.3) !important;}
    .generate-btn:hover { transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 15px 35px rgba(255, 0, 127, 0.4) !important; }
    body.dark .generate-btn:hover { box-shadow: 0 15px 35px rgba(0, 242, 254, 0.4) !important; }
    
    .secondary-btn { border-radius: 14px !important; font-size: 0.95rem !important; font-weight: 600 !important; background: rgba(0,0,0,0.05) !important; transition: all 0.2s ease !important; border: 1px solid transparent !important;}
    body.dark .secondary-btn { background: rgba(255,255,255,0.05) !important;}
    .secondary-btn:hover { background: rgba(0,0,0,0.1) !important; }
    body.dark .secondary-btn:hover { background: rgba(255,255,255,0.1) !important; }
    
    .footer { text-align: center; padding: 40px 0 20px 0; color: #a1a1aa; font-size: 0.9rem; font-weight: 500;}
    body.dark .footer { color: #52525b; }
    
    .output-tabs .tab-nav button { font-weight: 600 !important; font-size: 1.1rem !important; padding: 14px 24px !important; border-radius: 12px 12px 0 0 !important;}
    
    /* Input formatting to match premium feel */
    textarea, input[type="text"] { border-radius: 12px !important; transition: all 0.3s ease !important; border: 1px solid rgba(0,0,0,0.1) !important;}
    textarea:focus, input[type="text"]:focus { border-color: #ff007f !important; box-shadow: 0 0 0 2px rgba(255,0,127,0.2) !important;}
    body.dark textarea, body.dark input[type="text"] { border-color: rgba(255,255,255,0.1) !important; background: rgba(0,0,0,0.2) !important;}
    body.dark textarea:focus, body.dark input[type="text"]:focus { border-color: #00f2fe !important; box-shadow: 0 0 0 2px rgba(0,242,254,0.2) !important;}
    
    /* Premium smooth scrollbars for text areas */
    textarea {
        max-height: 450px !important;
        overflow-y: auto !important;
        scrollbar-width: thin !important;
        scrollbar-color: #7928ca rgba(0, 0, 0, 0.05) !important;
    }
    body.dark textarea {
        scrollbar-color: #00f2fe rgba(255, 255, 255, 0.02) !important;
    }
    textarea::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }
    textarea::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05) !important;
        border-radius: 10px !important;
    }
    body.dark textarea::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 10px !important;
    }
    textarea::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #7928ca 0%, #ff007f 100%) !important;
        border-radius: 10px !important;
    }
    body.dark textarea::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        border-radius: 10px !important;
    }
    textarea::-webkit-scrollbar-thumb:hover {
        background: #ff007f !important;
    }
    body.dark textarea::-webkit-scrollbar-thumb:hover {
        background: #00f2fe !important;
    }
    """

    toggle_theme_js = """
    function() {
        const body = document.querySelector('body');
        const html = document.documentElement;
        
        // Determine current theme state
        const isDark = body.classList.contains('dark') || html.classList.contains('dark');
        const themeBtn = document.querySelector('.theme-toggle-btn');
        
        if (isDark) {
            body.classList.remove('dark');
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            if(themeBtn) themeBtn.innerText = '🌙';
            
            // Try to set color-scheme explicitly
            html.style.colorScheme = 'light';
        } else {
            body.classList.add('dark');
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            if(themeBtn) themeBtn.innerText = '☀️';
            
            // Try to set color-scheme explicitly
            html.style.colorScheme = 'dark';
        }
        
        // Try to toggle class on any generic gradio-app elements
        const gradioApp = document.querySelector('gradio-app');
        if (gradioApp) {
            if (isDark) {
                gradioApp.classList.remove('dark');
            } else {
                gradioApp.classList.add('dark');
            }
        }
        
        return [];
    }
    """

    with gr.Blocks() as iface:
        
        with gr.Row(elem_classes=["theme-toggle-container"]):
            theme_btn = gr.Button("🌙", elem_classes=["theme-toggle-btn"], size="sm")
            theme_btn.click(None, None, None, js=toggle_theme_js)

        # ── Dashboard View ──
        with gr.Column(visible=True) as dashboard_view:
            with gr.Column(elem_classes=["dashboard-container"]):
                gr.Markdown("# AI Meeting Summarizer", elem_classes=["dashboard-title"])
                gr.Markdown(
                    "Turn your meeting recordings into actionable insights in seconds. "
                    "Processed entirely on your local machine for maximum privacy.",
                    elem_classes=["dashboard-subtitle"]
                )
                
                with gr.Row(elem_classes=["info-grid"]):
                    with gr.Column(elem_classes=["info-card"]):
                        gr.Markdown("#### 🎙️ High-Quality Transcription\n<p>Uses OpenAI's Whisper (via whisper.cpp) to accurately transcribe audio from any meeting format.</p>")
                    with gr.Column(elem_classes=["info-card"]):
                        gr.Markdown("#### 🧠 Intelligent Summarization\n<p>Powered by Ollama and local LLMs (like Llama 3) to extract key points, decisions, and action items.</p>")
                    with gr.Column(elem_classes=["info-card"]):
                        gr.Markdown("#### 🔒 100% Private & Local\n<p>No audio or text is ever sent to the cloud. Your sensitive meeting data never leaves your computer.</p>")
                
                with gr.Row(elem_classes=["enter-btn-container"]):
                    enter_btn = gr.Button("🚀 Enter Application", elem_classes=["enter-btn"])
        
        # ── Main App View ──
        with gr.Column(visible=False) as app_view:
            back_btn = gr.Button("← Back to Dashboard", elem_classes=["secondary-btn"], size="sm")
            
            # ── Hero Header ──
            gr.Markdown(
                "# 🎙️ AI Meeting Summarizer\n"
                "### Upload a meeting recording and get an instant AI-powered transcript & summary.",
                elem_classes=["hero-header"]
            )

            # ── Status Card ──
            if ollama_connected:
                gr.Markdown(
                    f"✅  **Ollama Connected** — {len(ollama_models)} model(s) ready for summarization",
                    elem_classes=["status-card", "status-connected"]
                )
            else:
                gr.Markdown(
                    "⚠️  **Ollama Not Running** — Transcription works, but summarization is disabled.  "
                    "Install [Ollama](https://ollama.com/) → run `ollama run llama3.2`",
                    elem_classes=["status-card", "status-disconnected"]
                )

            # ── Workflow Steps ──
            gr.Markdown(
                "**① Upload Audio** → **② Choose Models** → **③ Generate** → **④ Download Results**",
                elem_classes=["steps-bar"]
            )

            # ── Main Layout ──
            with gr.Row(equal_height=False):

                # ── Left: Inputs ──
                with gr.Column(scale=5, elem_classes=["input-panel"]):
                    gr.Markdown("#### 🎧 Input")
                    audio_input = gr.File(
                        type="filepath",
                        label="Meeting Recording (Audio or Video File)",
                        file_types=["audio", "video", ".mp4", ".mkv", ".avi", ".mov", ".webm", ".wav", ".mp3", ".m4a", ".flac"],
                    )

                    context_input = gr.Textbox(
                        label="Context  *(optional)*",
                        placeholder="E.g., Weekly product sync about the Q3 roadmap…",
                        lines=2,
                        max_lines=4,
                    )

                    gr.Markdown("#### ⚙️ Models")
                    with gr.Row():
                        whisper_dropdown = gr.Dropdown(
                            choices=whisper_models,
                            label="Whisper  (Transcription)",
                            value=whisper_val,
                            scale=3,
                        )
                        ollama_dropdown = gr.Dropdown(
                            choices=ollama_models,
                            label="Ollama  (Summary)",
                            value=ollama_val,
                            scale=3,
                        )
                        refresh_btn = gr.Button("🔄", scale=1, elem_classes=["secondary-btn"])

                    submit_btn = gr.Button(
                        "🚀  Generate Summary",
                        variant="primary",
                        elem_classes=["generate-btn"],
                    )

                # ── Right: Outputs ──
                with gr.Column(scale=6, elem_classes=["output-panel"]):
                    gr.Markdown("#### 📋 Results")
                    with gr.Tabs(elem_classes=["output-tabs"]):
                        with gr.Tab("📝 Summary"):
                            summary_output = gr.Textbox(
                                label="AI-Generated Summary",
                                lines=14,
                                interactive=False,
                                placeholder="Your meeting summary will appear here after processing…",
                            )
                        with gr.Tab("📄 Transcript"):
                            transcript_display = gr.Textbox(
                                label="Full Transcript (with Timestamps)",
                                lines=14,
                                interactive=False,
                                placeholder="Your transcript will appear here after processing…",
                            )
                            transcript_output = gr.File(
                                label="Download Transcript File",
                            )

            # ── Footer ──
            gr.Markdown(
                "Built with **Whisper.cpp** · **Ollama** · **Gradio** — "
                "All processing happens locally on your machine.",
                elem_classes=["footer"]
            )

            # ── Event Handlers ──
            submit_btn.click(
                fn=gradio_app,
                inputs=[audio_input, context_input, whisper_dropdown, ollama_dropdown],
                outputs=[summary_output, transcript_display, transcript_output],
            )

            refresh_btn.click(
                fn=refresh_ollama_models,
                inputs=[],
                outputs=[ollama_dropdown],
            )

        # Handle View Switching
        enter_btn.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            inputs=None,
            outputs=[dashboard_view, app_view]
        )
        back_btn.click(
            fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
            inputs=None,
            outputs=[dashboard_view, app_view]
        )

    iface.launch(
        debug=True,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="blue",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
        css=custom_css,
    )
