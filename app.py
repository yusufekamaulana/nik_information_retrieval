from flask import Flask, request, render_template
import pandas as pd
import re
from datetime import datetime

app = Flask(__name__)

file_path = 'kodewilayah.txt'  # Ganti dengan path file txt Anda
data = pd.read_csv(file_path, header=None, names=['Kode', 'Nama'], sep=',')

# Fungsi untuk menghitung umur berdasarkan tanggal lahir
def hitung_umur(tanggal_lahir):
    today = datetime.today()
    tanggal_lahir = datetime.strptime(tanggal_lahir, "%d-%m-%Y")
    umur = today.year - tanggal_lahir.year - ((today.month, today.day) < (tanggal_lahir.month, tanggal_lahir.day))
    return umur

# Fungsi untuk mengidentifikasi wilayah berdasarkan kode NIK
def identifikasi_wilayah(kode_provinsi, kode_kota, kode_kecamatan, df_wilayah):
    provinsi_row = df_wilayah[df_wilayah['Kode'] == kode_provinsi]
    kota_row = df_wilayah[df_wilayah['Kode'] == kode_kota]
    kecamatan_row = df_wilayah[df_wilayah['Kode'] == kode_kecamatan]

    nama_provinsi = provinsi_row['Nama'].values[0] if not provinsi_row.empty else "Provinsi tidak ditemukan. Mohon isi dengan kode yang benar"
    nama_kota = kota_row['Nama'].values[0] if not kota_row.empty else "Kabupaten/Kota tidak ditemukan. Mohon isi dengan kode yang benar"
    nama_kecamatan = kecamatan_row['Nama'].values[0] if not kecamatan_row.empty else "Kecamatan tidak ditemukan. Mohon isi dengan kode yang benar"

    return nama_provinsi, nama_kota, nama_kecamatan

# Fungsi utama untuk mengidentifikasi dan menghasilkan output NIK
def identifikasi_nik(nik, df_wilayah):
    pattern = r'(?P<kode_provinsi>\d{2})(?P<kode_kota>\d{2})(?P<kode_kecamatan>\d{2})(?P<tanggal>\d{2})(?P<bulan>\d{2})(?P<tahun>\d{2})\d{4}'
    match = re.match(pattern, nik)

    if match:
        kode_provinsi = match.group('kode_provinsi')
        kode_kota = f"{kode_provinsi}.{match.group('kode_kota')}"
        kode_kecamatan = f"{kode_kota}.{match.group('kode_kecamatan')}"

        nama_provinsi, nama_kota, nama_kecamatan = identifikasi_wilayah(kode_provinsi, kode_kota, kode_kecamatan, df_wilayah)
        
        tanggal = int(match.group('tanggal'))
        tahun = int(match.group('tahun'))

        if tanggal > 40:
            jenis_kelamin = 'Perempuan'
            tanggal -= 40
        else:
            jenis_kelamin = 'Laki-laki'

        bulan = match.group('bulan')
        tahun_lahir = tahun + 2000 if tahun <= 25 else tahun + 1900
        tanggal_lahir = "Tanggal lahir tidak valid" if not (1 <= int(bulan) <= 12) else f"{tanggal:02d}-{bulan}-{tahun_lahir}"

        umur = "Tidak dapat dihitung. Pastikan memasukkan bulan yang benar" if not (1 <= int(bulan) <= 12) else hitung_umur(tanggal_lahir)

        hasil = None if len(nik)>16 else {
            "NIK": nik,
            "Provinsi": nama_provinsi,
            "Kota/Kabupaten": nama_kota,
            "Kecamatan": nama_kecamatan,
            "Tanggal Lahir": tanggal_lahir,
            "Umur": umur,
            "Jenis Kelamin": jenis_kelamin
        }
        return hasil
    else:
        return "Format NIK tidak valid."

# Route untuk input dan output NIK
@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    if request.method == 'POST':
        nik = request.form['nik']
        hasil = identifikasi_nik(nik, data)

    return render_template('index.html', hasil=hasil)

if __name__ == '__main__':
    app.run(debug=True)
