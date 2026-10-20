---
name: mineru-pdf-to-markdown
description: Use this skill when the user wants to convert PDF files to Markdown format, extract text and images from PDFs, parse academic papers, or process document files using MinerU API. Trigger phrases include "è½¬markdown", "PDFè½¬æ¢", "è§£æžPDF", "æå–PDF", "MinerU", "æ–‡æ¡£è§£æž", "convert PDF", "parse document", "extract from PDF".
---

# MinerU PDF-to-Markdown Converter

Converts PDF files to high-quality Markdown with extracted images using the MinerU cloud API (v4 Precise API with VLM model).

## API Configuration

- **Base URL**: `https://mineru.net`
- **Auth**: Bearer token in Authorization header
- **Token**: Store in environment variable `MINERU_API_KEY` or pass directly
- **Model**: `vlm` (recommended for best quality)

## Workflow

### Step 1: Get Upload URLs (Batch)

```javascript
const response = await fetch("https://mineru.net/api/v4/file-urls/batch", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${API_TOKEN}`
  },
  body: JSON.stringify({
    files: [{ name: "document.pdf", is_ocr: false, data_id: "doc1" }],
    enable_formula: true,
    enable_table: true,
    language: "en",       // "en" for English, "ch" for Chinese
    model_version: "vlm"  // "vlm" recommended, "pipeline" faster
  })
});
// Response: { code: 0, data: { batch_id: "...", file_urls: ["https://..."] } }
```

### Step 2: Upload File to Signed URL

```javascript
// IMPORTANT: Do NOT set Content-Type header â€” OSS signature will fail
await fetch(uploadUrl, {
  method: "PUT",
  body: fileBuffer  // raw binary, no Content-Type header
});
```

### Step 3: Poll for Results (every 15s)

```javascript
const result = await fetch(
  `https://mineru.net/api/v4/extract-results/batch/${batchId}`,
  { headers: { "Authorization": `Bearer ${API_TOKEN}` } }
);
// States: waiting-file â†’ pending â†’ running â†’ done/failed
// When done: { state: "done", full_zip_url: "https://..." }
```

### Step 4: Download & Extract ZIP

The ZIP contains:
- `full.md` â€” Complete Markdown with image references
- `images/` â€” Extracted figures as JPG files
- `*_content_list.json` â€” Structured content data

## Python Implementation (Recommended)

```python
import requests, json, time, os, zipfile, glob

API_BASE = "https://mineru.net"
API_TOKEN = os.environ.get("MINERU_API_KEY", "YOUR_TOKEN_HERE")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def convert_pdfs_to_markdown(pdf_files, output_dir="markdown_output", language="en"):
    """Convert a list of PDF files to Markdown using MinerU API.

    Args:
        pdf_files: List of PDF file paths
        output_dir: Directory to save results
        language: "en" for English, "ch" for Chinese

    Returns:
        Dict mapping filename to output directory path
    """
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Get upload URLs
    files_payload = [
        {"name": os.path.basename(f), "is_ocr": False, "data_id": os.path.splitext(os.path.basename(f))[0]}
        for f in pdf_files
    ]
    payload = {
        "files": files_payload,
        "enable_formula": True,
        "enable_table": True,
        "language": language,
        "model_version": "vlm"
    }

    resp = requests.post(f"{API_BASE}/api/v4/file-urls/batch", headers=HEADERS, json=payload)
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"API error: {data}")

    batch_id = data["data"]["batch_id"]
    file_urls = data["data"]["file_urls"]
    print(f"Batch ID: {batch_id}, uploading {len(file_urls)} files...")

    # Step 2: Upload files (NO Content-Type header!)
    for i, upload_url in enumerate(file_urls):
        with open(pdf_files[i], "rb") as f:
            resp = requests.put(upload_url, data=f)
        status = "OK" if resp.status_code == 200 else f"FAILED({resp.status_code})"
        print(f"  {os.path.basename(pdf_files[i])}: {status}")

    # Step 3: Poll for results (every 15s)
    print("Polling for results...")
    poll_url = f"{API_BASE}/api/v4/extract-results/batch/{batch_id}"
    results = {}

    for attempt in range(40):  # max ~10 minutes
        time.sleep(15)
        resp = requests.get(poll_url, headers=HEADERS)
        extract_results = resp.json()["data"]["extract_result"]
        states = [r.get("state", "?") for r in extract_results]
        done_n = states.count("done")
        fail_n = states.count("failed")
        print(f"  [{attempt+1}] done={done_n} failed={fail_n} total={len(states)}")

        if done_n + fail_n == len(states):
            # Step 4: Download and extract
            for r in extract_results:
                data_id = r.get("data_id", "unknown")
                if r.get("state") == "done" and r.get("full_zip_url"):
                    zip_resp = requests.get(r["full_zip_url"])
                    zip_path = os.path.join(output_dir, f"{data_id}.zip")
                    with open(zip_path, "wb") as f:
                        f.write(zip_resp.content)

                    extract_dir = os.path.join(output_dir, data_id)
                    os.makedirs(extract_dir, exist_ok=True)
                    with zipfile.ZipFile(zip_path, "r") as z:
                        z.extractall(extract_dir)

                    results[data_id] = extract_dir
                    print(f"    {data_id}: OK ({len(zip_resp.content)//1024}KB)")
                else:
                    print(f"    {data_id}: {r.get('state')}")
                    results[data_id] = None
            break
    else:
        print("Timeout!")

    return results


def convert_single_pdf(pdf_path, output_dir="markdown_output", language="en"):
    """Convenience wrapper for a single PDF file."""
    return convert_pdfs_to_markdown([pdf_path], output_dir, language)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python convert.py <pdf_file_or_directory> [output_dir] [language]")
        print("  language: 'en' (default) or 'ch'")
        sys.exit(1)

    target = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "markdown_output"
    language = sys.argv[3] if len(sys.argv) > 3 else "en"

    if os.path.isdir(target):
        pdf_files = sorted(glob.glob(os.path.join(target, "*.pdf")))
    else:
        pdf_files = [target]

    if not pdf_files:
        print("No PDF files found!")
        sys.exit(1)

    print(f"Converting {len(pdf_files)} PDF(s) to Markdown...")
    results = convert_pdfs_to_markdown(pdf_files, output_dir, language)
    print(f"\nDone! Results in: {output_dir}/")
    for name, path in results.items():
        if path:
            print(f"  {name}: {path}/full.md")
```

## Key Notes

1. **Upload without Content-Type**: When uploading to the signed OSS URL, do NOT set any Content-Type header. The signature is pre-calculated without it â€” adding one causes 403 errors.

2. **VLM vs Pipeline**: `vlm` model gives best quality (uses vision-language model for layout understanding). `pipeline` is faster but lower quality.

3. **Batch limits**: Up to 50 files per batch, each â‰¤200MB and â‰¤200 pages.

4. **Processing time**: Typically 10-30 seconds per file with VLM model. Poll every 15 seconds.

5. **Output structure**: Each converted file produces a ZIP containing:
   - `full.md` â€” Markdown with `![](images/hash.jpg)` image references
   - `images/*.jpg` â€” All extracted figures, charts, and images
   - `*_content_list.json` â€” Structured block-level content

6. **Image references**: In `full.md`, images are referenced as `![](images/xxxx.jpg)`. The actual image files are in the `images/` subdirectory of the extracted ZIP.

7. **Language setting**: Use `"ch"` for Chinese documents, `"en"` for English. This affects OCR and layout detection.
