from google import genai
from google.genai import types
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
import time
from google.genai.errors import ServerError

st.set_page_config(page_title="CapWriter", layout="wide")

st.html('<meta name="dicoding:email" content="rizkyaziz2022@gmail.com">')

# ============================================================
# KONFIGURASI API
# ============================================================
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

MODEL = "gemma-4-31b-it"


# ============================================================
# SYSTEM PROMPT — PER PLATFORM
# ============================================================
SYSTEM_PROMPTS = {
    "Instagram": """Kamu adalah asisten "CapWriter". Tugas utamamu adalah membuatkan 
    teks promosi (copywriting / caption) Instagram berdasarkan input nama, gambar, 
    dan deskripsi singkat produk. Gunakan bahasa Indonesia yang santai, fun, dan menarik.

    Saat menerima input gambar dan/atau teks dari pengguna, berikan output dengan 
    struktur berikut (panjang 50-150 kata di luar hashtag):

    1. Hook: Kalimat pembuka yang menarik perhatian dengan gaya santai dan fun.
    2. Deskripsi produk: Jelaskan objek/produk berdasarkan gambar dan deskripsi.
    3. Keunggulan: Jelaskan sesuatu yang diunggulkan dan spesial dari produk.
    4. Call to Action: Ajakan untuk membeli, kunjungi, follow, dan lain-lain.
    5. Hashtag: WAJIB sertakan 5-10 hashtag relevan di akhir caption.

    Jika pengguna tidak memberikan gambar maupun deskripsi produk, 
    minta mereka untuk memberikan salah satunya terlebih dahulu.

    Berikan output caption langsung tanpa menyebutkan label bagian. 
    Tulis caption mengalir seperti postingan Instagram yang natural.""",

    "TikTok": """Kamu adalah asisten "CapWriter". Tugas utamamu adalah membuatkan 
    caption TikTok berdasarkan input nama, gambar, dan deskripsi singkat produk. 
    Gunakan bahasa Indonesia super casual, hook yang kuat di awal, dan gaya trendy 
    ala konten TikTok (singkat, padat, eye-catching).

    Struktur caption (panjang 30-80 kata di luar hashtag):
    1. Hook kuat di kalimat pertama — bikin orang berhenti scroll.
    2. Highlight singkat keunggulan produk.
    3. Call to action singkat (cth: "cek link di bio!", "buruan order!").
    4. Hashtag: WAJIB sertakan 5-8 hashtag trending dan relevan.

    Jika pengguna tidak memberikan gambar maupun deskripsi produk, 
    minta mereka untuk memberikan salah satunya terlebih dahulu.

    Tulis caption mengalir natural ala TikTok, tanpa label bagian.""",

    "Shopee/Tokopedia": """Kamu adalah asisten "CapWriter". Tugas utamamu adalah 
    membuatkan deskripsi produk untuk marketplace (Shopee/Tokopedia) berdasarkan 
    input nama, gambar, dan deskripsi singkat produk. Gunakan bahasa Indonesia yang 
    jelas, informatif, dan tetap menarik tapi lebih formal dibanding media sosial.

    Struktur deskripsi (panjang 80-150 kata):
    1. Kalimat pembuka yang menjelaskan apa produk ini secara singkat.
    2. Spesifikasi/detail produk berdasarkan deskripsi dan gambar.
    3. Keunggulan dan manfaat produk.
    4. Informasi tambahan (cth: garansi, pengiriman, cara pakai) jika relevan.
    5. Call to action untuk checkout/order.

    Jika pengguna tidak memberikan gambar maupun deskripsi produk, 
    minta mereka untuk memberikan salah satunya terlebih dahulu.

    Tulis dengan format rapi, bisa menggunakan poin-poin untuk spesifikasi 
    jika diperlukan, tanpa hashtag.""",
}


# ============================================================
# FUNGSI GENERATE CAPTION (Multi-platform)
# ============================================================
def generate_caption(nama_produk: str, deskripsi: str, platform: str, uploaded_file=None, max_retries=3) -> str:
    """
    Generate caption promosi sesuai platform yang dipilih.

    Args:
        nama_produk  : Nama produk dari input pengguna
        deskripsi    : Deskripsi singkat produk
        platform     : "Instagram", "TikTok", atau "Shopee/Tokopedia"
        uploaded_file: File gambar yang diupload, bisa None

    Returns:
        caption (str)
    """
    parts = []

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        parts.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=uploaded_file.type
            )
        )

    teks = ""
    if nama_produk:
        teks += f"Nama produk: {nama_produk}\n"
    if deskripsi:
        teks += f"Deskripsi produk: {deskripsi}"
    if teks:
        parts.append(types.Part.from_text(text=teks))

    contents = [types.Content(role="user", parts=parts)]

    system_prompt = SYSTEM_PROMPTS.get(platform, SYSTEM_PROMPTS["Instagram"])

    generate_content_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.8,
        max_output_tokens=1024,
    )

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=generate_content_config,
            )
            return response.text
        except ServerError as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            else:
                return "Maaf, server sedang sibuk. Silakan coba lagi dalam beberapa saat."

    return response.text


# ============================================================
# FUNGSI TRANSLATE CAPTION KE INGGRIS
# ============================================================
def translate_caption(caption: str, max_retries=3) -> str:
    """
    Menerjemahkan caption ke Bahasa Inggris secara natural,
    bukan translate kaku word-by-word.
    """
    system_prompt = """Kamu adalah penerjemah profesional untuk konten promosi/marketing.
    Terjemahkan teks caption berikut ke Bahasa Inggris secara NATURAL dan tetap 
    menarik untuk pembaca internasional. Pertahankan gaya santai/casual sesuai 
    konteks aslinya, jangan terjemahkan secara kaku word-by-word.
    Pertahankan hashtag dalam Bahasa Inggris yang relevan (terjemahkan maknanya, 
    bukan literal).
    Berikan HANYA hasil terjemahan tanpa penjelasan tambahan."""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=caption)]
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.5,
        max_output_tokens=1024,
    )

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=generate_content_config,
            )
            return response.text
        except ServerError as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            else:
                return "Maaf, server sedang sibuk. Silakan coba lagi dalam beberapa saat."

    return response.text



# ============================================================
# FUNGSI GENERATE IDE KONTEN/PROMOSI
# ============================================================
def generate_content_ideas(nama_produk: str, deskripsi: str, jenis_ide: str,  max_retries=3) -> str:
    """
    Generate ide konten atau promosi untuk UMKM.

    Args:
        nama_produk : Nama produk
        deskripsi   : Deskripsi produk
        jenis_ide   : "Ide Konten 7 Hari", "Ide Promo", atau "Ide Caption Story/Reels"

    Returns:
        hasil ide (str)
    """
    prompts_per_jenis = {
        "Ide Konten 7 Hari": """Buatkan ide konten media sosial untuk 7 hari ke depan 
        (Senin-Minggu) berdasarkan produk yang diberikan. Setiap hari berikan 1 ide singkat 
        beserta format kontennya (foto, video, carousel, dll) dan tujuannya (awareness, 
        engagement, konversi). Format dengan jelas per hari.""",

        "Ide Promo": """Buatkan 5 ide promo/diskon kreatif yang bisa diterapkan untuk 
        produk ini, cocok untuk UMKM dengan budget terbatas. Sertakan nama promo yang 
        catchy, mekanisme promo, dan estimasi dampaknya terhadap penjualan.""",

        "Ide Caption Story/Reels": """Buatkan 5 ide singkat untuk Instagram Story atau 
        Reels yang bisa dibuat untuk mempromosikan produk ini. Setiap ide sertakan konsep 
        visual singkat dan teks overlay yang cocok ditampilkan di video/story tersebut.""",
    }

    system_prompt = f"""Kamu adalah konsultan marketing digital untuk UMKM di Indonesia. 
    {prompts_per_jenis.get(jenis_ide, prompts_per_jenis["Ide Konten 7 Hari"])}

    Gunakan bahasa Indonesia yang jelas dan praktis, mudah dipahami dan diterapkan 
    oleh pelaku UMKM yang belum terlalu mahir digital marketing."""

    teks = ""
    if nama_produk:
        teks += f"Nama produk: {nama_produk}\n"
    if deskripsi:
        teks += f"Deskripsi produk: {deskripsi}"

    if not teks:
        return "Mohon isi nama produk dan/atau deskripsi produk terlebih dahulu di tab Caption."

    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=teks)])
    ]

    generate_content_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.9,
        max_output_tokens=2500,
    )

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=generate_content_config,
            )
            return response.text
        except ServerError as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            else:
                return "Maaf, server sedang sibuk. Silahkan coba lagi dalam beberapa saat."

    return response.text


# ============================================================
# IMPORT
# ============================================================
from db import (simpan_caption, ambil_caption, hapus_caption,
                simpan_translate, ambil_translate, hapus_translate,
                simpan_ide, ambil_ide, hapus_ide)

# ============================================================
# SESSION STATE — hanya untuk username
# ============================================================
if "username" not in st.session_state:
    st.session_state.username = None

# ============================================================
# LOGIN
# ============================================================
if st.session_state.username is None:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.title("✍️ CapWriter")
        st.subheader("Asisten Caption AI untuk UMKM")
        st.write("")
        st.markdown("**Yang bisa kamu lakukan:**")
        st.markdown("📱 Generate caption Instagram, TikTok, dan Marketplace")
        st.markdown("🌍 Terjemahkan caption ke Bahasa Inggris")
        st.markdown("💡 Dapatkan ide konten & promo untuk 7 hari")
        st.markdown("🕒 Riwayat caption tersimpan permanen per akun")

    with col2:
        with st.container(border=True):
            st.subheader("Masuk")
            username_input = st.text_input("Username", placeholder="Contoh: toko_baju_aulia")
            if st.button("Masuk →", use_container_width=True):
                if username_input.strip():
                    st.session_state.username = username_input.strip()
                    st.rerun()
                else:
                    st.error("Username tidak boleh kosong!")
            st.caption("Tidak perlu daftar — langsung masuk dengan username apapun.")
            st.stop()

username = st.session_state.username

# ============================================================
# SIDEBAR
# ============================================================
add_selectbox = st.sidebar.selectbox(
    "Pilih Halaman",
    ("Input Produk", "Profil")
)

nama_produk   = ""
deskripsi     = ""
uploaded_file = None

if add_selectbox == "Input Produk":
    st.sidebar.title("Input produk")
    nama_produk = st.sidebar.text_input("Nama Produk")
    uploaded_file = st.sidebar.file_uploader(
        "Upload gambar produk", accept_multiple_files=False, type=["jpg", "png", "jpeg"]
    )
    if uploaded_file is not None:
        st.sidebar.image(uploaded_file)
    deskripsi = st.sidebar.text_area("Deskripsi Produk")

elif add_selectbox == "Profil":
    st.sidebar.title("Input produk")
    st.sidebar.write(f"👤 {username}")
    if st.sidebar.button("Keluar"):
        st.session_state.username = None
        st.rerun()


# ============================================================
# JUDUL UTAMA
# ============================================================
st.title("CapWriter")
st.write("Asisten AI untuk membuat caption promosi, ide konten, dan lebih banyak lagi untuk UMKM.")
st.markdown("***Powered by Gemma 4 31B IT***")

tab_caption, tab_riwayat, tab_ide = st.tabs(["📝 Caption", "🕒 Riwayat", "💡 Ide Konten"])


# ============================================================
# TAB 1 — GENERATE CAPTION (Multi-platform)
# ============================================================
with tab_caption:
    platform = st.selectbox(
        "Pilih Platform",
        ["Instagram", "TikTok", "Shopee/Tokopedia"]
    )

    if st.button("✨ Generate Caption"):
        if not nama_produk:
            st.error("Nama produk wajib diisi!")
        elif not deskripsi and uploaded_file is None:
            st.error("Masukkan minimal deskripsi produk atau gambar produk!")
        else:
            with st.spinner("Sedang membuat caption..."):
                caption = generate_caption(nama_produk, deskripsi, platform, uploaded_file)

            simpan_caption(username, nama_produk, platform, caption)
            st.session_state["last_caption"] = caption  # untuk translate dan copy-paste

            st.success("Caption berhasil dibuat!")
            st.markdown(f"### 📝 Hasil Caption — {platform}")
            st.text_area("Hasil Caption", value=caption, height=300, label_visibility="collapsed")
            st_copy_to_clipboard(st.session_state['last_caption'], before_copy_label="Salin Teks", after_copy_label="Teks berhasil disalin!")

    # Tombol translate — hanya muncul jika sudah ada caption
    if "last_caption" in st.session_state:
        st.markdown("---")
        if st.button("🌍 Translate to English"):
            with st.spinner("Menerjemahkan caption..."):
                translated = translate_caption(st.session_state["last_caption"])
        
            simpan_translate(username, nama_produk, platform, st.session_state["last_caption"], translated)

            st.markdown("### 🌍 English Version")
            st.text_area("English Caption", value=translated, height=300, label_visibility="collapsed")
            st_copy_to_clipboard(translated, before_copy_label="Salin Teks", after_copy_label="Teks berhasil disalin!")


# ============================================================
# TAB 2 — RIWAYAT CAPTION
# ============================================================
with tab_riwayat:
    st.subheader("Riwayat")

    sub_caption, sub_translate, sub_ide = st.tabs(["📝 Caption", "🌍 Translate", "💡 Ide Konten"])

    # Sub-tab Caption
    with sub_caption:
        history_caption = ambil_caption(username)
        if not history_caption:
            st.info("Belum ada caption yang dibuat.")
        else:
            for idx, item in enumerate(history_caption):
                with st.expander(f"📄 {item['nama_produk']} — {item['platform']}"):
                    st.write(item["caption"])
                    st_copy_to_clipboard(
                        item["caption"],
                        before_copy_label="Salin Teks",
                        after_copy_label="Teks berhasil disalin!",
                        key=f"copy_caption_{idx}"
                    )
            if st.button("🗑️ Hapus Riwayat Caption"):
                hapus_caption(username)
                st.rerun()

    # Sub-tab Translate
    with sub_translate:
        history_translate = ambil_translate(username)
        if not history_translate:
            st.info("Belum ada caption yang diterjemahkan.")
        else:
            for idx, item in enumerate(history_translate):
                with st.expander(f"🌍 {item['nama_produk']} — {item['platform']}"):
                    st.markdown("### Original:")
                    st.write(item["original"])
                    st.markdown("### English:")
                    st.write(item["translated"])
                    st_copy_to_clipboard(
                        item["translated"],
                        before_copy_label="Salin Teks",
                        after_copy_label="Teks berhasil disalin!",
                        key=f"copy_translate_{idx}"
                    )
            if st.button("🗑️ Hapus Riwayat Translate"):
                hapus_translate(username)
                st.rerun()

    # Sub-tab Ide Konten
    with sub_ide:
        history_ide = ambil_ide(username)
        if not history_ide:
            st.info("Belum ada ide konten yang dibuat.")
        else:
            for idx, item in enumerate(history_ide):
                with st.expander(f"💡 {item['nama_produk']} — {item['jenis_ide']}"):
                    st.markdown(item["hasil"])
                    st_copy_to_clipboard(
                        item["hasil"],
                        before_copy_label="Salin Teks",
                        after_copy_label="Teks berhasil disalin!",
                        key=f"copy_ide_{idx}"
                    )
            if st.button("🗑️ Hapus Riwayat Ide Konten"):
                hapus_ide(username)
                st.rerun()

# ============================================================
# TAB 3 — IDE KONTEN/PROMOSI
# ============================================================
with tab_ide:
    st.subheader("Generate Ide Konten & Promosi")

    jenis_ide = st.selectbox(
        "Pilih jenis ide yang diinginkan",
        ["Ide Konten 7 Hari", "Ide Promo", "Ide Caption Story/Reels"]
    )

    if st.button("💡 Generate Ide"):
        with st.spinner("Sedang membuat ide..."):
            hasil_ide = generate_content_ideas(nama_produk, deskripsi, jenis_ide)
        
        simpan_ide(username, nama_produk, jenis_ide, hasil_ide)

        st.markdown(f"### 💡 {jenis_ide}")
        st.markdown(hasil_ide)
        
