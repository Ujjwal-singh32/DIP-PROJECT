# PDF → MongoDB ingestion for statutory sections

Usage:

1. Install dependencies (prefer a virtualenv):

```bash
pip install -r requirements.txt
```

2. Example run for a single PDF:

```bash
python ingest_pdf_to_mongo.py --pdf "path/to/act.pdf" --act "Indian Penal Code" --year 1860 --domain criminal_law --source_url "https://indiacode.nic.in/..." --collection statutes
```

3. To ingest all PDFs in a folder, pass the folder path to `--pdf`.

Notes:
- The script tries to detect section headers like `Section <number>`; for unusual layouts you may need to tweak `parse_sections`.
- Documents are upserted into MongoDB to avoid duplicates. Default DB: `legal_db`, default collection: `statutes`.
- Provide your `--mongo_uri` if you do not want to use the embedded default, or create a `.env` file and set `MONGODB_URI` there.

Environment (.env)
- Copy `.env.example` to `.env` and edit the `MONGODB_URI`, `MONGO_DB`, and `MONGO_COLLECTION` values.

Running upload web UI (internal link)
- A small local Flask app `upload_pdf_app.py` lets you upload PDFs into the project `uploads/` folder and gives internal links to those files.

Start the upload server:

```powershell
python upload_pdf_app.py
```

Then open this internal link in your browser:

http://127.0.0.1:5000/

When you upload a PDF the file is saved to the `uploads/` folder. You can then pass the path to the ingestion script, for example:

```powershell
python ingest_pdf_to_mongo.py --pdf "C:\Users\ujjwa\OneDrive\Desktop\DIP project\uploads\Indian_Penal_Code.pdf" --act "Indian Penal Code" --year 1860 --domain criminal_law --source_url "https://indiacode.nic.in/..."
```

OCR / scanned PDFs
- The upload UI does not OCR files. For scanned PDFs you'll need to add Tesseract OCR; tell me if you want me to add optional OCR processing on ingest.

---

## Legal RAG System (Mongo → Weaviate → Chat)

The repository also includes a retrieval‑augmented generation pipeline that:
1. reads statutes from MongoDB
2. computes embeddings
3. upserts to Weaviate
4. serves a Streamlit chat frontend
5. uses an LLM (Gemini by default) to answer legal queries.

### Embeddings
The default embedder attempts to load the **nlpaueb/inlegal-bert-small-cased** model from HuggingFace. If you do not have access to that model (private or removed) the code will log a warning and **automatically fall back** to the open `intfloat/e5-large` model.

To use the InLegalBERT checkpoint you must be authenticated with a valid HF token. You can place your token in the `.env` file as `HUGGINGFACE_TOKEN=your_token` or run `huggingface-cli login` in the same environment.

Alternatively, you may force the E5 embedder by setting `EMBEDDING_MODEL=e5` in `.env`.

### Environment configuration
Fill out the variables in `.env` according to `.env.example`:

- `MONGODB_URI`, `MONGO_DB`, `MONGO_COLLECTION`
- `WEAVIATE_URL`, `WEAVIATE_API_KEY`, `WEAVIATE_CLASS` (default `legal_sections`)
- `LLM_PROVIDER` (gemini, replicate, hf, etc.) and `LLM_API_KEY`
- Optional: `HUGGINGFACE_TOKEN` if using private HF models
- `EMBEDDING_MODEL` may be `inlegalbert` or `e5` (default)

### Running
From the project directory run:

```powershell
cd "C:\Users\ujjwa\OneDrive\Desktop\DIP project\project"
python main.py
```

The script will ingest any existing documents, create the Weaviate schema, and then launch the Streamlit chat UI.



