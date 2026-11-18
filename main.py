import os
import re
import pandas as pd
import pdfplumber
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO

app = FastAPI(title="Sistem Komparasi SK & Data Master")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(EXPORT_DIR, exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def extract_text_from_pdf(file_bytes):
    text_data = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_data.append(text)
    return "\n".join(text_data)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.post("/compare")
async def compare_data(master_file: UploadFile = File(...), sk_file: UploadFile = File(...)):
    try:
        # 1. Baca Data Master
        master_bytes = await master_file.read()
        if master_file.filename.endswith('.csv'):
            df_master = pd.read_csv(BytesIO(master_bytes))
        else:
            df_master = pd.read_excel(BytesIO(master_bytes))

        df_master.columns = [str(c).strip().lower() for c in df_master.columns]
        nim_col = next((c for c in df_master.columns if 'nim' in c), None)
        nama_col = next((c for c in df_master.columns if 'nama' in c), None)
        
        if not nim_col or not nama_col:
            raise HTTPException(status_code=400, detail="Kolom 'NIM' atau 'Nama' wajib ada di Data Master.")

        df_master['clean_nim'] = df_master[nim_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

        # 2. Baca File SK (Excel, CSV, atau PDF)
        sk_bytes = await sk_file.read()
        sk_nim_list = set()
        total_sk_count = 0

        if sk_file.filename.endswith(('.xlsx', '.xls', '.csv')):
            df_sk = pd.read_excel(BytesIO(sk_bytes)) if not sk_file.filename.endswith('.csv') else pd.read_csv(BytesIO(sk_bytes))
            df_sk.columns = [str(c).strip().lower() for c in df_sk.columns]
            
            # Cari kolom NIM, jika tidak ada gunakan kolom pertama
            sk_nim_col = next((c for c in df_sk.columns if 'nim' in c), df_sk.columns[0])
            
            sk_series = df_sk[sk_nim_col].dropna().astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
            sk_nim_list = set(sk_series)
            total_sk_count = len(df_sk)  # Total baris data di file SK Excel
        else:
            # Jika SK berupa PDF
            pdf_text = extract_text_from_pdf(sk_bytes)
            pdf_nims = set(re.findall(r'\b\d{7,15}\b', pdf_text))
            sk_nim_list = pdf_nims.intersection(set(df_master['clean_nim']))
            total_sk_count = len(sk_nim_list) if len(sk_nim_list) > 0 else len(pdf_nims)

        # 3. Proses Komparasi (Logika Himpunan / Selisih)
        df_missing = df_master[~df_master['clean_nim'].isin(sk_nim_list)].copy()
        df_missing['keterangan'] = 'Tidak tercantum di dalam SK'

        df_matched = df_master[df_master['clean_nim'].isin(sk_nim_list)].copy()
        df_matched['keterangan'] = 'Tercantum di dalam SK'

        # 4. Simpan ke folder exports
        path_missing = os.path.join(EXPORT_DIR, "Mahasiswa_Tidak_Tercantum_di_SK.xlsx")
        path_matched = os.path.join(EXPORT_DIR, "Mahasiswa_Tercantum_di_SK.xlsx")

        df_missing.drop(columns=['clean_nim']).to_excel(path_missing, index=False, engine='openpyxl')
        df_matched.drop(columns=['clean_nim']).to_excel(path_matched, index=False, engine='openpyxl')

        print(f"[SUKSES] Total Master: {len(df_master)}, Total SK: {total_sk_count}, Masuk SK: {len(sk_nim_list)}, Belum SK: {len(df_missing)}")

        return {
            "status": "success",
            "total_master": len(df_master),
            "total_sk": total_sk_count,
            "total_in_sk": len(sk_nim_list),
            "total_missing": len(df_missing),
            "download_missing": "/download/missing",
            "download_matched": "/download/matched"
        }

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")

@app.get("/download/missing")
def download_missing():
    file_path = os.path.join(EXPORT_DIR, "Mahasiswa_Tidak_Tercantum_di_SK.xlsx")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="Mahasiswa_Tidak_Tercantum_di_SK.xlsx")
    raise HTTPException(status_code=404, detail="File belum tersedia.")

@app.get("/download/matched")
def download_matched():
    file_path = os.path.join(EXPORT_DIR, "Mahasiswa_Tercantum_di_SK.xlsx")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="Mahasiswa_Tercantum_di_SK.xlsx")
    raise HTTPException(status_code=404, detail="File belum tersedia.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)