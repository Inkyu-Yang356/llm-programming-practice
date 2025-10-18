import pymupdf
import os

pdf_file_path = "/Users/Inkyu_Yang/20242402/jpt/LLM/ViT-test.pdf"

doc = pymupdf.open(pdf_file_path)

full_text = ""

for page in doc:
    text = page.get_text()
    full_text += text

print(full_text)

pdf_file_name = os.path.basename(pdf_file_path)
pdf_file_name = os.path.splitext(pdf_file_name)[0] # 확장자 제거

os.makedirs("output", exist_ok=True)
txt_file_path = f"output/{pdf_file_name}.txt"

with open(txt_file_path, "w", encoding="utf-8") as f:  # Write mode
    f.write(full_text)