import requests
import json
import time
import os
import sys
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# --- KONFIGURASI (SESUAIKAN USERNAME & REPO ANDA) ---
VERSI_LOKAL = "1.0.0"
URL_VERSION_JSON = "https://raw.githubusercontent.com/Ajie1705/otomatisasi-form/main/version.json"
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfySHOBNRGk5fnY-m-nlQCZylNV7dSM_REBZl3mvpM-Vqxq6w/formResponse"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://docs.google.com/forms/d/e/1FAIpQLSfySHOBNRGk5fnY-m-nlQCZylNV7dSM_REBZl3mvpM-Vqxq6w/viewform"
}

def cek_pembaruan():
    """Fungsi mengecek pembaruan dari internet sebelum GUI utama dibuka"""
    try:
        response = requests.get(URL_VERSION_JSON, timeout=3)
        if response.status_code == 200:
            data_server = response.json()
            versi_server = data_server.get("version")
            url_exe_baru = data_server.get("download_url")
            
            if versi_server and versi_server != VERSI_LOKAL:
                tanya = messagebox.askyesno(
                    "Pembaruan Tersedia", 
                    f"Versi baru ({versi_server}) tersedia!\nApakah Anda ingin memperbarui sekarang?"
                )
                if tanya:
                    lakukan_update(url_exe_baru)
    except:
        pass

def lakukan_update(url_download):
    """Mengunduh .exe baru dan memperbaruinya secara otomatis di Windows"""
    try:
        msg_temp = tk.Tk()
        msg_temp.withdraw()
        messagebox.showinfo("Update", "Mengunduh pembaruan, aplikasi akan dimulai ulang setelah selesai.")
        
        exe_baru_path = os.path.join(os.environ['TEMP'], "app_update.exe")
        r = requests.get(url_download, stream=True)
        with open(exe_baru_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
        exe_lama_path = sys.executable
        bat_path = os.path.join(os.environ['TEMP'], "update.bat")
        with open(bat_path, "w") as bat_file:
            bat_file.write(f"""
            @echo off
            timeout /t 2 /nobreak > nul
            del /f /q "{exe_lama_path}"
            move /y "{exe_baru_path}" "{exe_lama_path}"
            start "" "{exe_lama_path}"
            del "%~f0"
            """)
            
        subprocess.Popen(bat_path, shell=True)
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Error Update", f"Gagal melakukan pembaruan otomatis: {e}")

def kirim_data_grup(grup_pilihan):
    hari_ini = datetime.now()
    script_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    db_path = os.path.join(script_dir, "data_pengguna.json")

    try:
        with open(db_path, "r") as f:
            semua_grup = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membaca file database_pengguna.json:\n{e}")
        return

    if grup_pilihan not in semua_grup:
        messagebox.showerror("Error", f"Data untuk Grup {grup_pilihan} tidak ditemukan di database.")
        return

    daftar_pengguna = semua_grup[grup_pilihan]
    
    # Nonaktifkan tombol sementara proses berjalan
    for btn in [btn_a, btn_b, btn_c, btn_d]:
        btn.config(state=tk.DISABLED)
    lbl_status.config(text=f"Sedang mengirim data Grup {grup_pilihan} ({len(daftar_pengguna)} orang)...")
    root.update()

    sukses = 0
    gagal = 0

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
        
        "entry.867285848": "Saya menyatakan bahwa data yang saya isi pada form ini benar   sesuai kondisi kesehatan saya saat ini.",
        
        "pageHistory": "0,1,2,3,4",
        "fbzx": "-3336482920283632141"
        }

        try:
            res = requests.post(URL_FORM, data=payload, headers=HEADERS)
            if res.status_code == 200:
                sukses += 1
            else:
                gagal += 1
                print(f"Status Code Error: {res.status_code}") # Untuk melacak status HTTP
        except Exception as e:
            gagal += 1
            print(f"Exception Error: {e}") # Untuk melacak error kodingan/jaringan
            
        time.sleep(0.5)

    for btn in [btn_a, btn_b, btn_c, btn_d]:
        btn.config(state=tk.NORMAL)
    lbl_status.config(text="Selesai!")
    messagebox.showinfo("Informasi", f"Pengiriman Grup {grup_pilihan} Selesai!\nSukses: {sukses}\nGagal: {gagal}")

if __name__ == "__main__":
    cek_pembaruan()
    
    root = tk.Tk()
    root.title("Otomatisasi Google Form Shift (v" + VERSI_LOKAL + ")")
    root.geometry("380x330")
    root.resizable(False, False)

    lbl_judul = tk.Label(root, text="Pilih Grup Kerja:", font=("Arial", 12, "bold"))
    lbl_judul.pack(pady=15)

    btn_a = tk.Button(root, text="GRUP A", font=("Arial", 10, "bold"), bg="#4CAF50", fg="black", width=20, height=2, command=lambda: kirim_data_grup("A"))
    btn_a.pack(pady=5)

    btn_b = tk.Button(root, text="GRUP B", font=("Arial", 10, "bold"), bg="#2196F3", fg="black", width=20, height=2, command=lambda: kirim_data_grup("B"))
    btn_b.pack(pady=5)

    btn_c = tk.Button(root, text="GRUP C", font=("Arial", 10, "bold"), bg="#FF9800", fg="black", width=20, height=2, command=lambda: kirim_data_grup("C"))
    btn_c.pack(pady=5)

    btn_d = tk.Button(root, text="GRUP D", font=("Arial", 10, "bold"), bg="purple", fg="black", width=20, height=2, command=lambda: kirim_data_grup("D"))
    btn_d.pack(pady=5)

    lbl_status = tk.Label(root, text="Status: Menunggu pilihan...", font=("Arial", 9), fg="gray")
    lbl_status.pack(pady=10)

    root.mainloop()
