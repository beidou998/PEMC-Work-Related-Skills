"""
MinerU PDF-to-Markdown Converter
Converts PDF files to high-quality Markdown with extracted images.

Usage:
    python convert.py <pdf_file_or_directory> [output_dir] [language]

Examples:
    python convert.py paper.pdf
    python convert.py ./papers/ markdown_output ch
    python convert.py document.pdf output en
"""
import requests
import json
import time
import os
import zipfile
import glob
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_BASE = "https://mineru.net"
API_TOKEN = os.environ.get("MINERU_API_KEY", "")
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
    if not API_TOKEN:
        raise ValueError("MINERU_API_KEY environment variable not set. "
                        "Set it with: export MINERU_API_KEY='your_token'")

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

    print(f"Requesting batch upload URLs for {len(pdf_files)} file(s)...")
    resp = requests.post(f"{API_BASE}/api/v4/file-urls/batch", headers=HEADERS, json=payload, verify=False)
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"API error: {data}")

    batch_id = data["data"]["batch_id"]
    file_urls = data["data"]["file_urls"]
    print(f"Batch ID: {batch_id}")

    # Step 2: Upload files (NO Content-Type header!)
    print(f"Uploading {len(file_urls)} file(s)...")
    for i, upload_url in enumerate(file_urls):
        filename = os.path.basename(pdf_files[i])
        filesize = os.path.getsize(pdf_files[i]) / (1024 * 1024)
        print(f"  {filename} ({filesize:.1f} MB)...", end=" ")
        with open(pdf_files[i], "rb") as f:
            resp = requests.put(upload_url, data=f, verify=False)
        print("OK" if resp.status_code == 200 else f"FAILED({resp.status_code})")

    # Step 3: Poll for results (every 15s)
    print("\nWaiting for conversion...")
    poll_url = f"{API_BASE}/api/v4/extract-results/batch/{batch_id}"
    results = {}

    for attempt in range(40):  # max ~10 minutes
        time.sleep(15)
        resp = requests.get(poll_url, headers=HEADERS, verify=False)
        result_data = resp.json()
        if result_data.get("code") != 0:
            print(f"  Poll error: {result_data.get('msg')}")
            continue

        extract_results = result_data["data"]["extract_result"]
        states = [r.get("state", "?") for r in extract_results]
        done_n = states.count("done")
        fail_n = states.count("failed")
        total = len(states)
        print(f"  [{attempt+1}] done={done_n} failed={fail_n} total={total}")

        if done_n + fail_n == total:
            # Step 4: Download and extract
            print("\nDownloading results...")
            for r in extract_results:
                data_id = r.get("data_id", "unknown")
                if r.get("state") == "done" and r.get("full_zip_url"):
                    zip_resp = requests.get(r["full_zip_url"], verify=False)
                    zip_path = os.path.join(output_dir, f"{data_id}.zip")
                    with open(zip_path, "wb") as f:
                        f.write(zip_resp.content)

                    extract_dir = os.path.join(output_dir, data_id)
                    os.makedirs(extract_dir, exist_ok=True)
                    with zipfile.ZipFile(zip_path, "r") as z:
                        z.extractall(extract_dir)

                    results[data_id] = extract_dir
                    print(f"  {data_id}: OK ({len(zip_resp.content)//1024} KB)")
                else:
                    print(f"  {data_id}: {r.get('state')} (skipped)")
                    results[data_id] = None
            break
    else:
        print("Timeout waiting for results!")

    return results


def convert_single_pdf(pdf_path, output_dir="markdown_output", language="en"):
    """Convenience wrapper for a single PDF file."""
    return convert_pdfs_to_markdown([pdf_path], output_dir, language)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
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

    print(f"Converting {len(pdf_files)} PDF(s) to Markdown (language={language})...")
    print(f"Output directory: {output_dir}/\n")

    results = convert_pdfs_to_markdown(pdf_files, output_dir, language)

    print(f"\n{'='*50}")
    print(f"Done! {len([v for v in results.values() if v])} file(s) converted successfully.")
    print(f"Results in: {output_dir}/")
    for name, path in results.items():
        if path:
            md_file = os.path.join(path, "full.md")
            images_dir = os.path.join(path, "images")
            n_images = len(glob.glob(os.path.join(images_dir, "*"))) if os.path.isdir(images_dir) else 0
            print(f"  {name}/full.md ({n_images} images)")
