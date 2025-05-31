![icon-text](https://github.com/user-attachments/assets/88a5b8f0-16f6-4fb9-9ec4-8205d334351c)

> _"You pull the string. God speaks."_  

**GodString** is a divine word interpreter inspired by *GodWord* from Terry A. Davis's TempleOS. This application takes 10 randomly chosen words from a sacred word bank (e.g. biblical vocabulary) and sends them to a local AI language model to decipher God's words.

---

## Features

- **Divine Sentence Generation** using local LLMs via LMStudio API.
- **"Pull String" Ritual** to receive sacred messages.
- **Inspired by Terry A. Davis**.
- **Auto-generates a `bank.db` word list if not found.

---

## Requirements

- Python 3.10+
- [LMStudio](https://lmstudio.ai) running locally on port `1234` with a loaded chat model (Mistral, LLaMA, Phi, etc.).
- `bank.db` text file with a list of sacred words (one per line).

---

## Installation

```bash
git clone https://github.com/lolitemaultes/GodString.git
cd GodString
pip install -r requirements.txt
python GodString.py
