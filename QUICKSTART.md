# Quick Start Guide - Meeting Summarizer

## TL;DR (30 seconds to running)

```bash
# 1. Make script executable
chmod +x run_meeting_summarizer.sh

# 2. Run setup and app
./run_meeting_summarizer.sh
```

Done! Visit `http://localhost:7860` in your browser.

---

## What You Need

1. **Python 3.8+** - Check: `python3 --version`
2. **FFmpeg** - Install: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)
3. **Ollama** - Install from [ollama.ai](https://ollama.ai)

### Quick Setup (3 Steps)

#### Step 1: Install Ollama & Start Server
```bash
# Install from https://ollama.ai or:
brew install ollama  # macOS

# Start Ollama in background/another terminal
ollama serve
```

#### Step 2: Get a Model
```bash
ollama pull llama2
```

#### Step 3: Run the App
```bash
chmod +x run_meeting_summarizer.sh
./run_meeting_summarizer.sh
```

---

## Using the App

1. Open `http://localhost:7860`
2. Upload an audio file (MP3, WAV, M4A)
3. Choose models:
   - Whisper: "small" (fast) or "medium" (better)
   - LLM: "llama2" (good balance)
4. Click **Submit**
5. Get transcript + summary + download link

---

## Performance

| Task | Time |
|------|------|
| Installation | 30-60 sec |
| First startup | 5-10 sec |
| Summarize 5min audio | 1-2 min |

---

## Troubleshooting

**"Failed to retrieve models"**
→ Make sure Ollama is running: `ollama serve`

**"FFmpeg not found"**
→ Install: `brew install ffmpeg` or `apt-get install ffmpeg`

**"Whisper model not found"**
→ Downloaded automatically on first run

**"Connection refused"**
→ Check Ollama is running on port 11434

---

## Next Steps

- Read `README.md` for detailed documentation
- Check `OPTIMIZATION_GUIDE.md` for advanced setup
- Look at `main.py` for code customization

---

**That's it! You're ready to go. 🚀**
