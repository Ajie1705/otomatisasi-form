#!/usr/bin/env python3

import requests
import json
import time
import os
from datetime import datetime

hari_ini = datetime.now()
url = "https://docs.google.com/forms/d/e/1FAIpQLSfySHOBNRGk5fnY-m-nlQCZylNV7dSM_REBZl3mvpM-Vqxq6w/formResponse"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    "Referer": "https://docs.google.com/forms/d/e/1FAIpQLSfySHOBNRGk5fnY-m-nlQCZylNV7dSM_REBZl3mvpM-Vqxq6w/viewform"
}

# --- 1. Membaca Database Keseluruhan ---
lokasi_skrip = os.path.dirname(os.path.abspath(__file__))
file_database = os.path.join(lokasi_skrip, "data_pengguna.json")

try:
    with open(file_database, "r") as file:
        semua_grup = json.load(file)
except Exception as e:
    print(f"Gagal membaca database: {e}")
    exit(1)

# --- 2. Fase Interaktif (Meminta Input Pengguna) ---
print("=" * 40)
print("  OTOMATISASI PENGISIAN FORM DCU  ")
print("=" * 40)

# Looping validasi: akan terus bertanya sampai input valid dimasukkan
while True:
    pilihan_grup = input("Masukkan Grup yang akan diinput (A/B/C/D): ").strip().upper()
    
    if pilihan_grup in semua_grup:
        daftar_pengguna = semua_grup[pilihan_grup]
        print(f"\n=> Grup {pilihan_grup} dipilih. Memuat {len(daftar_pengguna)} pengguna...\n")
        break # Keluar dari loop jika input valid
    else:
        print("[Error] Grup tidak ditemukan. Harap masukkan huruf A, B, C, atau D.\n")

# --- 3. Fase Eksekusi Jaringan ---
for pengguna in daftar_pengguna:
    payload = {
        "entry.1146271895_year": str(hari_ini.year),
        "entry.1146271895_month": str(hari_ini.month),
        "entry.1146271895_day": str(hari_ini.day),
        
        "entry.1607140824": pengguna["nama"],
        "entry.1072553700": pengguna["nik"],
        "entry.739030352": "M. Faishal Ma'arif",
        "entry.822074195": "Operasi Pabrik III A",
        "entry.664915295": "Asam Fosfat III A",
        
        "entry.1967491262": "Tidak ada",
        "entry.1034208656": "Tidak",
        "entry.1218475249": "Tidak",
        "entry.650185261": "Tidak",
        "entry.672656689": "Tidak",
        "entry.1402632693": "Tidak",
        "entry.882530815": "Tidak",
        "entry.971335496": "Tidak",
        
        "entry.1738409079": "Ya",
        
        "entry.867285848": "Saya menyatakan bahwa data yang saya isi pada form ini benar sesuai kondisi kesehatan saya saat ini.",
        
        "pageHistory": "0,1,2,3,4",
        "fbzx": "-3336482920283632141"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            print(f"[Sukses] Data {pengguna['nama']} terkirim.")
        else:
            print(f"[Gagal] Data {pengguna['nama']} ditolak (Kode: {response.status_code})")
    except Exception as e:
        print(f"[Error Jaringan] Gagal mengirim data {pengguna['nama']}: {e}")
        
    time.sleep(1)

print("\nSeluruh antrean selesai.")
