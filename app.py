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
VERSI_LOKAL = "1.1.3"
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

def sinkronisasi_database():
    """Menarik data_pengguna.json terbaru dari GitHub setiap kali aplikasi dibuka"""
    # Ganti URL di bawah dengan URL 'raw' file data_pengguna.json Anda di GitHub
    url_db_github = "https://raw.githubusercontent.com/Ajie1705/otomatisasi-form/main/data_pengguna.json"
    
    script_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    db_path = os.path.join(script_dir, "data_pengguna.json")
    
    try:
        # Mengunduh data json terbaru
        res = requests.get(url_db_github, timeout=5)
        
        # Jika berhasil mengunduh (Status 200), timpa file lokal yang lama
        if res.status_code == 200:
            with open(db_path, "w") as f:
                f.write(res.text)
    except:
        # Jika tidak ada internet saat aplikasi baru dibuka, abaikan error
        # dan gunakan file data_pengguna.json sisa kemarin (mode fallback)
        pass

def buka_jendela_kehadiran(grup_pilihan):
    script_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    db_path = os.path.join(script_dir, "data_pengguna.json")
    riwayat_path = os.path.join(script_dir, "riwayat.json")

    try:
        with open(db_path, "r") as f:
            semua_grup = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membaca database:\n{e}")
        return

    daftar_pengguna = semua_grup[grup_pilihan]
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
    
    # Baca riwayat lokal untuk mengecek NIK siapa saja yang sudah terkirim hari ini
    riwayat = {}
    if os.path.exists(riwayat_path):
        with open(riwayat_path, "r") as f:
            riwayat = json.load(f)

    # Mengecek apakah SEMUA orang di grup ini sudah terkirim
    sudah_terkirim_semua = all(riwayat.get(p["nik"]) == tanggal_hari_ini for p in daftar_pengguna)
    if sudah_terkirim_semua:
        messagebox.showinfo("Info", f"Seluruh personel Grup {grup_pilihan} sudah mengisi form untuk hari ini.")
        return # Hentikan proses, tidak perlu membuka pop-up

    jendela_absen = tk.Toplevel(root)
    jendela_absen.title(f"Konfirmasi Kehadiran - Grup {grup_pilihan}")
    jendela_absen.geometry("380x500")
    
    lbl_info = tk.Label(jendela_absen, text="Centang hanya personel yang akan disubmit:", font=("Arial", 9, "bold"))
    lbl_info.pack(pady=10)

    status_kehadiran = []

    for pengguna in daftar_pengguna:
        # Cek apakah NIK ini sudah dikirim hari ini
        sudah_dikirim = (riwayat.get(pengguna["nik"]) == tanggal_hari_ini)
        
        # Jika sudah dikirim, defaultnya False (hapus centang). Jika belum, True (dicentang otomatis)
        var_status = tk.BooleanVar(value=not sudah_dikirim)
        
        # Tambahkan teks penanda jika sudah terkirim
        teks_label = pengguna["nama"] + ("  (Sudah Terkirim)" if sudah_dikirim else "")
        
        chk = tk.Checkbutton(
            jendela_absen, 
            text=teks_label, 
            variable=var_status,
            font=("Arial", 9),
            anchor="w"
        )
        
        # Kunci tombol (disabled) jika orang tersebut sudah pernah terkirim hari ini
        if sudah_dikirim:
            chk.config(state="disabled", fg="gray")
            
        chk.pack(fill="x", padx=30)
        
        status_kehadiran.append((pengguna, var_status))

    btn_kirim = tk.Button(
        jendela_absen, 
        text="KIRIM DATA HADIR", 
        font=("Arial", 10, "bold"), 
        bg="#4CAF50", fg="black", 
        command=lambda: eksekusi_kirim(grup_pilihan, status_kehadiran, jendela_absen)
    )
    btn_kirim.pack(pady=20)


def eksekusi_kirim(grup_pilihan, status_kehadiran, jendela_absen):
    hari_ini = datetime.now()
    tanggal_hari_ini = hari_ini.strftime("%Y-%m-%d")
    
    # Saring HANYA personel yang kotak centangnya bernilai True
    pengguna_hadir = [orang for orang, var_status in status_kehadiran if var_status.get() == True]
    
    if len(pengguna_hadir) == 0:
        messagebox.showwarning("Peringatan", "Tidak ada personel baru yang dipilih untuk disubmit!")
        return

    jendela_absen.title("Sedang mengirim...")
    jendela_absen.update()

    script_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    riwayat_path = os.path.join(script_dir, "riwayat.json")
    
    riwayat = {}
    if os.path.exists(riwayat_path):
        with open(riwayat_path, "r") as f:
            riwayat = json.load(f)

    sukses = 0
    gagal = 0

    for pengguna in pengguna_hadir:
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
            res = requests.post(URL_FORM, data=payload, headers=HEADERS)
            # Jika Google merespons sukses, langsung catat NIK-nya
            if res.status_code == 200:
                sukses += 1
                riwayat[pengguna["nik"]] = tanggal_hari_ini
            else:
                gagal += 1
        except:
            gagal += 1
            
        time.sleep(0.5)

    # Simpan kembali seluruh catatan keberhasilan (lama + baru) ke dalam file riwayat.json
    with open(riwayat_path, "w") as f:
        json.dump(riwayat, f)

    jendela_absen.destroy()
    messagebox.showinfo("Selesai", f"Laporan Grup {grup_pilihan}:\nSusulan Sukses: {sukses}\nGagal: {gagal}")

if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()
    
    cek_pembaruan()
    sinkronisasi_database()

    root.deiconify()
    root.title("Otomatisasi Pengisian DCU Form (v" + VERSI_LOKAL + ")")
    root.geometry("410x350")
    root.resizable(False, False)

    lbl_judul = tk.Label(root, text="Pilih Grup Kerja:", font=("Arial", 12, "bold"))
    lbl_judul.pack(pady=15)

    btn_a = tk.Button(root, text="GRUP A", font=("Arial", 10, "bold"), bg="#4CAF50", fg="black", width=20, height=2, command=lambda: buka_jendela_kehadiran("A"))
    btn_a.pack(pady=5)

    btn_b = tk.Button(root, text="GRUP B", font=("Arial", 10, "bold"), bg="#2196F3", fg="black", width=20, height=2, command=lambda: buka_jendela_kehadiran("B"))
    btn_b.pack(pady=5)

    btn_c = tk.Button(root, text="GRUP C", font=("Arial", 10, "bold"), bg="#FF9800", fg="black", width=20, height=2, command=lambda: buka_jendela_kehadiran("C"))
    btn_c.pack(pady=5)

    btn_d = tk.Button(root, text="GRUP D", font=("Arial", 10, "bold"), bg="purple", fg="black", width=20, height=2, command=lambda: buka_jendela_kehadiran("D"))
    btn_d.pack(pady=5)

    lbl_status = tk.Label(root, text="Status: Menunggu pilihan...", font=("Arial", 9), fg="gray")
    lbl_status.pack(pady=10)

    root.mainloop()
