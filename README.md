# 🔍 Data Reconciliation & Verification System (KOMPAS-SK)

Sistem berbasis web modern yang dirancang untuk mengotomatisasi proses komparasi, pencocokan (*matching*), dan rekonsiliasi antara **Data Master Utama** dengan **Dokumen Pembanding** (seperti Surat Keputusan, Daftar Hadir, Laporan Keuangan, atau Dokumen Resmi lainnya) secara instan dan akurat.

---

## 🎯 Tujuan Pembuatan Aplikasi
Dalam pengolahan administrasi skala besar, pencocokan data secara manual antara database master dan dokumen lampiran sering kali memakan waktu tinggi dan rentan terhadap *human error*. Aplikasi ini dibuat dengan tujuan:
1. **Otomatisasi Validasi:** Mempercepat proses audit dan pencocokan data menggunakan operasi himpunan (*set theory*) berbasis Python.
2. **Deteksi Dini Anomali:** Membantu mendeteksi data atau entitas apa saja yang terdaftar di master namun absen/belum tercantum di dalam dokumen lampiran.
3. **Efisiensi Administrasi:** Menyediakan rekapitulasi statistik yang transparan serta menghasilkan laporan terpisah secara otomatis untuk mempercepat proses tindak lanjut.

---

## 🌟 Fitur Utama
* **Multi-Format Document Support:** Mendukung pembacaan berkas Master dan Pembanding dalam format terstruktur (`Excel`/`CSV`) maupun dokumen tidak terstruktur berformat teks (`PDF`).
* **Pencocokan Multi-Kriteria Fleksibel:** Sistem otomatis mendeteksi kolom kunci primer secara dinamis (seperti ID unik, Nomor Induk, Kode, atau Nama) tanpa batasan struktur baku.
* **Dashboard Metrik Statistik Instan:** Menampilkan rekapitulasi lengkap yang mencakup:
  * **Total Master:** Jumlah keseluruhan data pada basis data utama.
  * **Total Pembanding:** Jumlah total data yang tertera pada dokumen pembanding.
  * **Masuk / Tercantum:** Jumlah entitas master yang valid terdeteksi di dokumen pembanding.
  * **Belum Tercantum:** Jumlah entitas master yang absen/belum masuk ke dokumen pembanding.
* **Export Management Otomatis:** Menyimpan laporan hasil analisis secara terstruktur ke dalam folder khusus (`exports/`) dalam dua file terpisah untuk memudahkan pelacakan.

---

## 🛠️ Tech Stack & Dependencies
* **Bahasa Pemrograman:** Python 3.x
* **Backend Framework:** FastAPI & Uvicorn
* **Data Processing:** Pandas & Openpyxl
* **PDF Text Extraction:** Pdfplumber
* **Frontend UI:** HTML5, Tailwind CSS, & JavaScript (Fetch API)

---

## 📂 Struktur Direktori Proyek
```text
web-komparasi-sistem/
│
├── exports/                  # Folder penyimpanan otomatis file hasil komparasi (.xlsx)
│   ├── Data_Tercantum.xlsx
│   └── Data_Tidak_Tercantum.xlsx
│
├── templates/
│   └── index.html            # Antarmuka web pengguna (Frontend)
│
├── main.py                   # Berkas utama logika Backend FastAPI
├── .gitignore                # Berkas pengecualian Git
└── README.md                 # Dokumentasi Proyek
