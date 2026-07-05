# CapWriter

Aplikasi web berbasis AI yang membantu pelaku UMKM menyusun caption promosi dan ide konten secara cepat dan efisien.

**[Buka Aplikasi](https://capwriter-umkm.streamlit.app)**

---

## Tentang Proyek

Banyak pelaku UMKM yang kesulitan menyusun caption promosi yang menarik dan menentukan ide konten yang relevan untuk media sosial maupun marketplace mereka. CapWriter hadir sebagai solusi berbasis AI yang memungkinkan siapa saja membuat caption promosi berkualitas hanya dengan memasukkan nama produk, gambar, dan deskripsi singkat.

---

## Fitur Utama

-  **Multi-platform caption:**  Generate caption untuk Instagram, TikTok, dan Shopee/Tokopedia
-  **Terjemahan ke Bahasa Inggris:**  Terjemahkan caption secara natural
-  **Ide konten & promo:**  Dapatkan ide konten 7 hari, ide promo, dan ide Story/Reels
-  **Riwayat permanen:**  Semua hasil generate tersimpan per akun pengguna

---

## Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Gemma 4 31B IT | Model AI untuk generate caption dan ide konten |
| Google AI Studio | Platform akses API |
| Streamlit | Framework aplikasi web |
| Supabase (PostgreSQL) | Database cloud untuk riwayat permanen |

---

## Cara Penggunaan

1. Buka aplikasi di [capwriter-umkm.streamlit.app](https://capwriter-umkm.streamlit.app)
2. Masukkan username bebas (tidak perlu registrasi)
3. Isi informasi produk di sidebar: nama produk (wajib), gambar atau deskripsi (salah satu wajib)
4. Pilih fitur melalui tab yang tersedia:
   - **Caption** → pilih platform → klik *Generate Caption*
   - **Caption** → klik *Translate to English* untuk terjemahan
   - **Ide Konten** → pilih jenis ide → klik *Generate Ide*
   - **Riwayat** → lihat semua hasil generate yang tersimpan

---

## Struktur File

```
capwriter/
├── main.py           # Aplikasi utama (UI + fungsi AI)
├── db.py             # Fungsi koneksi dan operasi database
├── requirements.txt  # Daftar dependensi
└── .gitignore        # File yang dikecualikan dari Git
```

---

## Menjalankan Secara Lokal

1. Clone repository
```bash
git clone https://github.com/R-Aziz-10/capwriter.git
cd capwriter
```

2. Install dependensi
```bash
pip install -r requirements.txt
```

3. Buat file `.streamlit/secrets.toml`
```toml
GEMINI_API_KEY = "isi_api_key_anda"
SUPABASE_URL   = "isi_supabase_url_anda"
SUPABASE_KEY   = "isi_supabase_key_anda"
```

4. Jalankan aplikasi
```bash
streamlit run main.py
```

---

## Rencana Pengembangan

- Penambahan pilihan tone/nada penulisan (formal, santai, persuasif)
- Penyesuaian panjang kata untuk pembuatan caption
- Penambahan pilihan bahasa output caption (Mandarin, Spanyol, dll)

---

## Developer

**Rizky Aziz Putra A.** — Perancangan sistem, pengembangan aplikasi, dan deployment
