from supabase import create_client
import streamlit as st

# Koneksi Supabase
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# Caption
def simpan_caption(username, nama_produk, platform, caption):
    supabase.table("riwayat_caption").insert({
        "username"    : username,
        "nama_produk" : nama_produk,
        "platform"    : platform,
        "caption"     : caption,
    }).execute()

def ambil_caption(username):
    res = supabase.table("riwayat_caption")\
        .select("*")\
        .eq("username", username)\
        .order("created_at", desc=True)\
        .execute()
    return res.data

def hapus_caption(username):
    supabase.table("riwayat_caption")\
        .delete()\
        .eq("username", username)\
        .execute()

# Translate
def simpan_translate(username, nama_produk, platform, original, translated):
    supabase.table("riwayat_translate").insert({
        "username"    : username,
        "nama_produk" : nama_produk,
        "platform"    : platform,
        "original"    : original,
        "translated"  : translated,
    }).execute()

def ambil_translate(username):
    res = supabase.table("riwayat_translate")\
        .select("*")\
        .eq("username", username)\
        .order("created_at", desc=True)\
        .execute()
    return res.data

def hapus_translate(username):
    supabase.table("riwayat_translate")\
        .delete()\
        .eq("username", username)\
        .execute()

# Ide Konten
def simpan_ide(username, nama_produk, jenis_ide, hasil):
    supabase.table("riwayat_ide").insert({
        "username"    : username,
        "nama_produk" : nama_produk,
        "jenis_ide"   : jenis_ide,
        "hasil"       : hasil,
    }).execute()

def ambil_ide(username):
    res = supabase.table("riwayat_ide")\
        .select("*")\
        .eq("username", username)\
        .order("created_at", desc=True)\
        .execute()
    return res.data

def hapus_ide(username):
    supabase.table("riwayat_ide")\
        .delete()\
        .eq("username", username)\
        .execute()