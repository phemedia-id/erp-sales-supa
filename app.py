import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime
from streamlit_option_menu import option_menu

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ERP Sales Pro Executive V17 (High Contrast)",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM (THEME V17 - HIGH CONTRAST & VISIBILITY FIX) ---
st.markdown("""
<style>
    /* IMPORT FONT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap');

    /* 1. FORCE LIGHT MODE BACKGROUND & DARK TEXT GLOBAL */
    .stApp {
        background-color: #f8fafc; /* Very Light Grey */
        color: #0f172a !important; /* Dark Slate Blue (Hampir Hitam) */
        font-family: 'Inter', sans-serif;
    }
    
    /* 2. PAKSA SEMUA TEKS JADI GELAP */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label {
        color: #0f172a !important; 
        font-family: 'Poppins', sans-serif;
    }
    
    /* PENGECUALIAN UNTUK SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] span {
         color: #1e293b !important;
    }

    /* 3. CARD & METRIC STYLING */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #cbd5e1;
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 13px !important;
        color: #475569 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 32px !important;
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    .metric-sub {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #334155 !important;
        background-color: #f1f5f9;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
    }

    /* 4. INPUT FIELDS (TEXT BOX, SELECT BOX) - FIX BACKGROUND PUTIH */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #94a3b8 !important;
        border-radius: 8px !important;
    }
    ul[data-baseweb="menu"] li {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    /* 5. BUTTON STYLING */
    div.stButton > button {
        color: #ffffff !important;
        font-weight: 600;
        border-radius: 8px;
    }
    div.stButton > button p {
        color: #ffffff !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        border: 1px solid #94a3b8 !important;
    }
    div.stButton > button[kind="secondary"] p {
        color: #0f172a !important;
    }

    /* 6. DATAFRAME / TABEL */
    div[data-testid="stDataFrame"] {
        background-color: white !important;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
    }
    div[data-testid="stDataFrame"] div[role="grid"] div[role="row"] div {
        color: #0f172a !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        color: #0f172a !important;
        font-weight: bold !important;
        background-color: #f1f5f9 !important;
    }

    /* 7. EXPANDER */
    div[data-testid="stExpander"] {
        background-color: white !important;
        border: 1px solid #cbd5e1 !important;
        color: #000000 !important;
    }
    div[data-testid="stExpander"] summary {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    /* HIDE INDEX TABEL */
    thead tr th:first-child { display:none }
    tbody tr td:first-child { display:none }

    /* LOGIN CONTAINER */
    .login-container {
        background: #ffffff;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .login-container h2 { color: #1e3a8a !important; }
</style>
""", unsafe_allow_html=True)

# --- KONEKSI DATABASE (SUPABASE/POSTGRES) ---
# Menggunakan st.connection bawaan Streamlit
conn = st.connection("supabase", type="sql")

# --- FUNGSI HELPER ---
def run_query(query_str, params=None):
    """Fungsi pembantu untuk menjalankan query SQL (INSERT/UPDATE/DELETE)"""
    try:
        # Menggunakan session context manager untuk transaksi
        with conn.session as s:
            s.execute(text(query_str), params)
            s.commit()
    except Exception as e:
        st.error(f"Database Error: {e}")

def get_data(query_str, params=None):
    """Fungsi khusus untuk mengambil data (SELECT) menjadi DataFrame"""
    # ttl=0 artinya jangan cache data, selalu ambil yang terbaru dari server
    return conn.query(query_str, params=params, ttl=0)

def format_ribuan(value):
    """Mengubah angka menjadi string dengan pemisah ribuan titik (Format Indo)"""
    if pd.isna(value) or value == '':
        return "0"
    try:
        return "{:,.0f}".format(float(value)).replace(",", ".")
    except:
        return str(value)

NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def get_bulan_index(nama_bulan):
    try:
        return NAMA_BULAN.index(nama_bulan) + 1
    except:
        return datetime.datetime.now().month

# --- FUNGSI LOGIN (POSTGRESQL VERSION) ---
def check_login(username, password):
    # Parameter binding di SQLAlchemy pakai :nama_param
    df = get_data(
        "SELECT username, role, real_name, nama_spv FROM users WHERE username=:u AND password=:p",
        params={"u": username, "p": password}
    )
    if not df.empty:
        return df.iloc[0] # Kembalikan baris pertama
    return None

# --- SIDEBAR & NAVIGASI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.real_name = None
    st.session_state.user_spv = None

if not st.session_state.logged_in:
    # --- DESAIN LOGIN PAGE (V16 STYLE) ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.5, 1])
    with col_b:
        st.markdown("""
        <div class='login-container'>
            <div style="background: #eff6ff; width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;">
                <span style="font-size: 40px;">🏢</span>
            </div>
            <h2 style='margin-bottom: 5px; font-family: "Poppins", sans-serif; font-weight: 700;'>ERP Sales Pro</h2>
            <p style='font-size: 14px; margin-bottom: 30px;'>Executive Performance Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<h4 style='text-align: center; color: #1e293b !important;'>Sign In</h4>", unsafe_allow_html=True)
            user_input = st.text_input("Username", placeholder="Masukkan ID Pengguna")
            pass_input = st.text_input("Password", type="password", placeholder="Masukkan Kata Sandi")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("MASUK SISTEM", use_container_width=True, type="primary")
            
            if submitted:
                user = check_login(user_input, pass_input)
                if user is not None:
                    st.session_state.logged_in = True
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.session_state.real_name = user['real_name']
                    st.session_state.user_spv = user['nama_spv']
                    st.success(f"Selamat datang, {user['real_name']}")
                    st.rerun()
                else:
                    st.error("Username atau Password Salah")

else:
    # --- SETUP MENU NAVIGATION ---
    with st.sidebar:
        # Header Sidebar
        st.markdown(f"""
        <div style='text-align: center; padding: 24px 10px; background: white; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 20px;'>
            <div style="position: relative; width: 80px; height: 80px; margin: 0 auto;">
                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="80" style='border-radius: 50%; border: 3px solid #e0f2fe; padding: 2px;'>
                <div style="position: absolute; bottom: 2px; right: 2px; width: 16px; height: 16px; background: #22c55e; border-radius: 50%; border: 2px solid white;"></div>
            </div>
            <h3 style='margin-top: 15px; font-size: 16px; font-weight: 700; margin-bottom: 4px; color: #0f172a !important;'>{st.session_state.real_name}</h3>
            <span style='color: #64748b !important; font-size: 12px; font-weight: 500;'>{st.session_state.user_role.upper()}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Opsi Menu
        menu_options = ["Dashboard", "Laporan Rekap"]
        menu_icons = ["grid-1x2-fill", "file-earmark-bar-graph-fill"]
        
        if st.session_state.user_role in ['admin', 'spv']:
            menu_options.extend(["Input Target", "Kelola Pelanggan", "Upload Data", "Kelola User", "Master SPV"])
            menu_icons.extend(["crosshair", "people-fill", "cloud-arrow-up-fill", "person-lines-fill", "shield-lock-fill"])
        
        selected = option_menu(
            menu_title="NAVIGASI UTAMA", 
            options=menu_options, 
            icons=menu_icons, 
            menu_icon="cast", 
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "menu-title": {"color": "#475569", "font-size": "11px", "font-weight": "700", "margin-bottom": "10px", "padding-left": "15px"},
                "icon": {"color": "#475569", "font-size": "16px"}, 
                "nav-link": {
                    "font-size": "14px", 
                    "text-align": "left", 
                    "margin":"4px 8px", 
                    "padding": "10px 15px",
                    "color": "#334155",
                    "border-radius": "10px",
                    "font-weight": "500",
                    "transition": "all 0.2s"
                },
                "nav-link-selected": {"background-color": "#eff6ff", "color": "#2563eb", "font-weight": "600", "box-shadow": "inset 3px 0 0 #2563eb"},
            }
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Keluar Sistem", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- HALAMAN 1: DASHBOARD ---
    if selected == "Dashboard":
        # Header Modern
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <h1 style="font-size: 28px; font-weight: 700; color: #0f172a !important; letter-spacing: -0.5px;">Dashboard Executive</h1>
                <p style="color: #475569 !important; font-size: 14px;">Ringkasan performa penjualan terkini</p>
            </div>
            <div style="text-align: right;">
                <span style="background: #e0f2fe; color: #0369a1 !important; padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 600;">
                    📅 {}
                </span>
            </div>
        </div>
        """.format(datetime.date.today().strftime('%d %B %Y')), unsafe_allow_html=True)
        
        # Filter Tanggal
        now = datetime.datetime.now()
        with st.container():
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                nm_bln_pilih = st.selectbox("📅 Pilih Bulan", NAMA_BULAN, index=now.month-1)
                bulan_pilih = get_bulan_index(nm_bln_pilih) 
            with col_filter2:
                list_tahun = [2024, 2025, 2026, 2027]
                curr_year = now.year
                idx_thn = list_tahun.index(curr_year) if curr_year in list_tahun else 2
                tahun_pilih = st.selectbox("📆 Pilih Tahun", list_tahun, index=idx_thn)
            
        # Logika Pengambilan Data
        sales_to_view = []
        is_team_view = False
        
        if st.session_state.user_role == 'salesman':
            sales_to_view = [st.session_state.real_name]
        elif st.session_state.user_role == 'spv':
            is_team_view = True
            df_team = get_data("SELECT real_name FROM users WHERE nama_spv=:spv", params={"spv": st.session_state.real_name})
            sales_to_view = df_team['real_name'].tolist()
            if not sales_to_view:
                st.info("Anda belum memiliki Salesman yang terdaftar di bawah Anda.")
        else: # Admin
            is_team_view = True
            df_all = get_data("SELECT DISTINCT real_name FROM users WHERE role='salesman'")
            sales_to_view = df_all['real_name'].tolist()

        if sales_to_view:
            # === BAGIAN 1: REKAP TIM ===
            if is_team_view and sales_to_view:
                st.markdown("### 🏆 Performa Tim")
                
                total_target_qty = 0
                total_real_qty = 0
                total_target_tagihan = 0
                rank_data = [] 
                
                for s in sales_to_view:
                    # Target
                    df_tgt = get_data("SELECT target_qty, target_tagihan FROM target_sales WHERE salesman_nama=:s AND bulan=:b AND tahun=:t", 
                                      params={"s": s, "b": bulan_pilih, "t": tahun_pilih})
                    t_qty = df_tgt.iloc[0]['target_qty'] if not df_tgt.empty else 0
                    t_tag = df_tgt.iloc[0]['target_tagihan'] if not df_tgt.empty else 0
                    
                    # Realisasi (Pakai EXTRACT untuk date di Postgres)
                    query_real = """
                        SELECT SUM(qty_sls) as tot_qty 
                        FROM transactions 
                        WHERE rep_sls=:s 
                        AND EXTRACT(MONTH FROM tgl_sls) = :b 
                        AND EXTRACT(YEAR FROM tgl_sls) = :t
                        AND net_sls != 0
                    """
                    df_real = get_data(query_real, params={"s": s, "b": bulan_pilih, "t": tahun_pilih})
                    r_qty = df_real.iloc[0]['tot_qty'] if not df_real.empty and pd.notnull(df_real.iloc[0]['tot_qty']) else 0
                        
                    total_target_qty += t_qty
                    total_real_qty += r_qty
                    total_target_tagihan += t_tag
                    
                    pct = (r_qty / t_qty * 100) if t_qty > 0 else 0
                    rank_data.append({
                        "Salesman": s,
                        "Target": t_qty,
                        "Realisasi": r_qty,
                        "% Capai": pct
                    })
                
                # Metrics Tim
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <div class="metric-card" style="border-bottom: 4px solid #3b82f6;">
                        <div class="metric-label">📊 TARGET TOTAL TIM</div>
                        <div class="metric-value">{format_ribuan(total_target_qty)}</div>
                        <div class="metric-sub" style="color: #3b82f6 !important; background: #eff6ff;">Unit/Karton</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    pct_team = (total_real_qty/total_target_qty*100) if total_target_qty > 0 else 0
                    color_t = "#10b981" if pct_team >= 100 else "#f59e0b"
                    bg_t = "#ecfdf5" if pct_team >= 100 else "#fffbeb"
                    st.markdown(f"""
                    <div class="metric-card" style="border-bottom: 4px solid {color_t};">
                        <div class="metric-label">📈 REALISASI TIM</div>
                        <div class="metric-value">{format_ribuan(total_real_qty)}</div>
                        <div class="metric-sub" style="color: {color_t} !important; background: {bg_t};">Pencapaian: {pct_team:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div class="metric-card" style="border-bottom: 4px solid #8b5cf6;">
                        <div class="metric-label">💰 EST. TAGIHAN TIM</div>
                        <div class="metric-value"><span style="font-size: 20px; color: #94a3b8 !important;">Rp</span> {format_ribuan(total_target_tagihan)}</div>
                        <div class="metric-sub" style="color: #8b5cf6 !important; background: #f5f3ff;">Valuasi Rupiah</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Tabel Peringkat
                st.markdown("<br><h4 style='color:#0f172a !important;'>🥇 Peringkat Salesman Bulan Ini</h4>", unsafe_allow_html=True)
                if rank_data:
                    df_rank = pd.DataFrame(rank_data).sort_values(by="% Capai", ascending=False).reset_index(drop=True)
                    df_rank_disp = df_rank.copy()
                    df_rank_disp['Target'] = df_rank_disp['Target'].apply(format_ribuan)
                    df_rank_disp['Realisasi'] = df_rank_disp['Realisasi'].apply(format_ribuan)
                    df_rank_disp['% Capai'] = df_rank_disp['% Capai'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(df_rank_disp, use_container_width=True)
                else:
                    st.info("Data ranking belum tersedia.")
                
                st.divider()
                st.markdown("### 📋 Detail Individu Salesman")

            # === BAGIAN 2: LOOPING DETAIL (PER INDIVIDU) ===
            for salesman in sales_to_view:
                with st.expander(f"👤 {salesman}", expanded=True): 
                    # 1. Ambil TARGET
                    df_tgt_ind = get_data("SELECT target_qty, target_tagihan FROM target_sales WHERE salesman_nama=:s AND bulan=:b AND tahun=:t",
                                          params={"s": salesman, "b": bulan_pilih, "t": tahun_pilih})
                    tgt_qty = df_tgt_ind.iloc[0]['target_qty'] if not df_tgt_ind.empty else 0
                    tgt_tagihan = df_tgt_ind.iloc[0]['target_tagihan'] if not df_tgt_ind.empty else 0
                    
                    # 2. Ambil REALISASI
                    # Ambil Detail Transaksi untuk mapping customer yg sudah beli
                    query_trans_det = """
                        SELECT * FROM transactions 
                        WHERE rep_sls=:s 
                        AND EXTRACT(MONTH FROM tgl_sls) = :b 
                        AND EXTRACT(YEAR FROM tgl_sls) = :t
                        AND net_sls != 0
                    """
                    df_trans = get_data(query_trans_det, params={"s": salesman, "b": bulan_pilih, "t": tahun_pilih})
                    
                    if not df_trans.empty:
                        real_qty = df_trans['qty_sls'].sum()
                        cust_sudah_beli = df_trans['cust_id'].unique().tolist()
                    else:
                        real_qty = 0
                        cust_sudah_beli = []

                    # 3. Hitung %
                    persen_qty = (real_qty / tgt_qty * 100) if tgt_qty > 0 else 0
                    
                    # TAMPILAN METRIK INDIVIDU
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Target Qty", format_ribuan(tgt_qty))
                    col2.metric("Realisasi", format_ribuan(real_qty), f"{persen_qty:.1f}%")
                    col3.metric("Target Rp", format_ribuan(tgt_tagihan))
                    col4.metric("Status", "On Track" if persen_qty >= 80 else "Behind", delta_color="normal")
                    
                    # 4. CALL PLAN
                    st.markdown(f"<h5 style='margin-top:20px; color:#475569 !important;'>📢 Call Plan (Belum Order)</h5>", unsafe_allow_html=True)
                    
                    df_master_plg = get_data("SELECT cust_id as 'ID', nama_cst as 'Nama Toko', alamat as 'Alamat' FROM master_customer WHERE salesman_pengampu = :s", params={"s": salesman})
                    
                    if not df_master_plg.empty:
                        df_belum_beli = df_master_plg[~df_master_plg['ID'].isin(cust_sudah_beli)]
                        if not df_belum_beli.empty:
                            st.dataframe(df_belum_beli, use_container_width=True, height=350)
                        else:
                            st.success("🎉 Luar biasa! Semua pelanggan mappingan sudah order.")
                    else:
                        st.warning("Belum ada mapping pelanggan untuk sales ini.")

    # --- HALAMAN 2: LAPORAN REKAP ---
    elif selected == "Laporan Rekap":
        st.markdown("## 📑 Laporan Rekapitulasi")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            tgl_awal = st.date_input("Dari Tanggal", value=datetime.date.today().replace(day=1))
        with col_f2:
            tgl_akhir = st.date_input("Sampai Tanggal", value=datetime.date.today())
        with col_f3:
            target_salesman = []
            if st.session_state.user_role in ['admin', 'spv']:
                if st.session_state.user_role == 'spv':
                    list_team = get_data("SELECT real_name FROM users WHERE nama_spv = :spv", params={"spv": st.session_state.real_name})['real_name'].tolist()
                else:
                    list_team = get_data("SELECT DISTINCT real_name FROM users WHERE role='salesman'")['real_name'].tolist()
                
                list_team.insert(0, "SEMUA TIM")
                pilih_sales_filter = st.selectbox("Filter Salesman", list_team)
                
                if pilih_sales_filter == "SEMUA TIM":
                    target_salesman = list_team[1:]
                else:
                    target_salesman = [pilih_sales_filter]
            else:
                st.write(f"Salesman: **{st.session_state.real_name}**")
                target_salesman = [st.session_state.real_name]

        st.divider()

        if target_salesman:
            # Karena PostgreSQL di Supabase, kita gunakan tuple untuk IN clause agak tricky di parameter binding
            # Kita gunakan format string Python standard untuk list salesman karena ini aman jika list dari database sendiri
            sales_tuple = tuple(target_salesman)
            query_rekap = f"""
                SELECT * FROM transactions 
                WHERE rep_sls IN :sales_list
                AND tgl_sls BETWEEN :d1 AND :d2
                AND net_sls != 0 
            """
            # SQL Alchemy requires tuple for list params
            df_rekap = get_data(query_rekap, params={"sales_list": sales_tuple, "d1": tgl_awal, "d2": tgl_akhir})
            
            if not df_rekap.empty:
                # df_rekap['tgl_sls'] otomatis datetime jika dari Postgres
                
                tab_cust, tab_prod = st.tabs(["👥 Rekap Per Pelanggan", "📦 Rekap Per Produk"])
                
                with tab_cust:
                    df_grp_cust = df_rekap.groupby(['cust_id', 'nama_cst']).agg({
                        'qty_sls': 'sum',
                        'net_sls': 'sum'
                    }).reset_index().sort_values(by='net_sls', ascending=False)
                    
                    df_grp_cust['Total Qty'] = df_grp_cust['qty_sls'].apply(format_ribuan)
                    df_grp_cust['Total Rupiah'] = df_grp_cust['net_sls'].apply(format_ribuan)
                    
                    df_display_cust = df_grp_cust[['cust_id', 'nama_cst', 'Total Qty', 'Total Rupiah']].rename(columns={
                        'cust_id': 'Kode Pelanggan', 'nama_cst': 'Nama Pelanggan'
                    })
                    st.dataframe(df_display_cust, use_container_width=True, height=500)
                    st.markdown(f"### Total Omzet: Rp {format_ribuan(df_grp_cust['net_sls'].sum())}")

                with tab_prod:
                    df_grp_prod = df_rekap.groupby(['kode_itm', 'nama_itm']).agg({
                        'qty_sls': 'sum',
                        'net_sls': 'sum'
                    }).reset_index().sort_values(by='qty_sls', ascending=False)
                    
                    df_grp_prod['Total Qty'] = df_grp_prod['qty_sls'].apply(format_ribuan)
                    df_grp_prod['Total Rupiah'] = df_grp_prod['net_sls'].apply(format_ribuan)
                    
                    df_display_prod = df_grp_prod[['kode_itm', 'nama_itm', 'Total Qty', 'Total Rupiah']].rename(columns={
                        'kode_itm': 'Kode Item', 'nama_itm': 'Nama Produk'
                    })
                    st.dataframe(df_display_prod, use_container_width=True, height=500)
            else:
                st.warning("Tidak ada data transaksi pada periode yang dipilih.")
        else:
            st.warning("Silakan pilih Salesman terlebih dahulu.")

    # --- HALAMAN 3: INPUT TARGET ---
    elif selected == "Input Target":
        st.markdown("## 🎯 Input Target Salesman")
        
        with st.expander("➕ Form Input Target Baru", expanded=True):
            with st.form("form_target"):
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    sales_opts = get_data("SELECT real_name FROM users WHERE role='salesman'")['real_name'].tolist()
                    pilih_sales = st.selectbox("Nama Salesman", sales_opts)
                with col_t2:
                    pilih_nm_bln = st.selectbox("Bulan", NAMA_BULAN)
                    pilih_bln_angka = get_bulan_index(pilih_nm_bln)
                with col_t3:
                    pilih_thn = st.selectbox("Tahun", [2024, 2025, 2026], index=1)
                    
                col_t4, col_t5 = st.columns(2)
                with col_t4:
                    in_target_qty = st.number_input("Target Quantity (Total)", min_value=0.0)
                with col_t5:
                    in_target_tagihan = st.number_input("Target Tagihan (Rp)", min_value=0.0)
                    
                btn_save_target = st.form_submit_button("SIMPAN TARGET", type="primary")
                
                if btn_save_target:
                    # UPSERT (Insert or Update) syntax in PostgreSQL
                    q_upsert = """
                        INSERT INTO target_sales (salesman_nama, bulan, tahun, target_qty, target_tagihan)
                        VALUES (:s, :b, :t, :qty, :rp)
                        ON CONFLICT (salesman_nama, bulan, tahun) 
                        DO UPDATE SET target_qty=EXCLUDED.target_qty, target_tagihan=EXCLUDED.target_tagihan
                    """
                    run_query(q_upsert, params={
                        "s": pilih_sales, "b": pilih_bln_angka, "t": pilih_thn,
                        "qty": in_target_qty, "rp": in_target_tagihan
                    })
                    st.success(f"✅ Target untuk {pilih_sales} berhasil disimpan.")
                    st.rerun()

        st.divider()
        st.markdown("### 📝 Editor Data Target")
        
        df_tgt_view = get_data("SELECT * FROM target_sales ORDER BY tahun DESC, bulan DESC, salesman_nama ASC")
        # Kolom bantu bulan
        df_tgt_view['Nama_Bulan'] = df_tgt_view['bulan'].apply(lambda x: NAMA_BULAN[x-1] if 1 <= x <= 12 else x)
        
        edited_df = st.data_editor(
            df_tgt_view,
            column_config={
                "id": None, 
                "bulan": None,
                "Nama_Bulan": "Bulan",
                "salesman_nama": "Salesman",
                "target_qty": st.column_config.NumberColumn("Target Qty", format="%.0f"),
                "target_tagihan": st.column_config.NumberColumn("Target Rp", format="%.0f")
            },
            disabled=["salesman_nama", "Nama_Bulan", "tahun"],
            use_container_width=True,
            key="target_editor"
        )
        
        if st.button("Simpan Perubahan Tabel", type="primary"):
            # Karena st.data_editor tidak otomatis update DB, kita loop (Not Efficient for Big Data but OK here)
            # Idealnya pakai st.data_editor(..., on_change) tapi butuh session state complex.
            # Kita pakai logic sederhana: Delete Row lama & Insert Baru? Tidak, Update by ID.
            # Disini Supabase update
            with conn.session as s:
                for index, row in edited_df.iterrows():
                    q_upd = "UPDATE target_sales SET target_qty=:qty, target_tagihan=:rp WHERE id=:id"
                    s.execute(text(q_upd), {"qty": row['target_qty'], "rp": row['target_tagihan'], "id": row['id']})
                s.commit()
            st.success("Perubahan tabel berhasil disimpan!")

    # --- HALAMAN 4: KELOLA PELANGGAN ---
    elif selected == "Kelola Pelanggan":
        st.markdown("## 📍 Mapping Pelanggan")
        col_search, col_space = st.columns([1,2])
        with col_search:
            search_txt = st.text_input("🔍 Cari Nama / Alamat / ID:")
        
        # Base Query
        q_base = "SELECT * FROM master_customer"
        p_base = {}
        if search_txt:
            q_base += " WHERE nama_cst ILIKE :txt OR alamat ILIKE :txt OR cust_id ILIKE :txt" # ILIKE = Case Insensitive Postgres
            p_base = {"txt": f"%{search_txt}%"}
            
        df_cust = get_data(q_base, params=p_base)
        
        if not df_cust.empty:
            with st.container():
                st.markdown("##### Editor Mapping")
                col_edit1, col_edit2, col_edit3 = st.columns([3, 2, 1])
                with col_edit1:
                    df_cust['display_text'] = df_cust.apply(
                        lambda x: f"{x['cust_id']} - {x['nama_cst']} ({x['alamat'] if x['alamat'] else '-'})", axis=1
                    )
                    pilih_cust_str = st.selectbox("Pilih Pelanggan", df_cust['display_text'])
                    real_cust_id = pilih_cust_str.split(" - ")[0]
                
                with col_edit2:
                    list_sales = get_data("SELECT real_name FROM users WHERE role='salesman'")['real_name'].tolist()
                    list_sales.insert(0, "")
                    
                    curr_sales = df_cust[df_cust['cust_id'] == real_cust_id]['salesman_pengampu'].values[0]
                    idx_sel = list_sales.index(curr_sales) if curr_sales in list_sales else 0
                    
                    new_salesman = st.selectbox("Salesman Penanggung Jawab", list_sales, index=idx_sel)
                
                with col_edit3:
                    st.write("") 
                    st.write("") 
                    if st.button("UPDATE MAPPING", type="primary"):
                        run_query("UPDATE master_customer SET salesman_pengampu = :s WHERE cust_id = :id", 
                                  params={"s": new_salesman, "id": real_cust_id})
                        st.success(f"Updated: {real_cust_id} -> {new_salesman}")
                        st.rerun()
            
            st.dataframe(df_cust, use_container_width=True)
        else:
            st.warning("Data Master Customer tidak ditemukan.")

    # --- HALAMAN 5: UPLOAD DATA ---
    elif selected == "Upload Data":
        st.markdown("## 📂 Pusat Upload Data")
        tab1, tab2 = st.tabs(["📄 1. Master Customer", "🛒 2. Transaksi Penjualan"])
        
        # TAB 1: MASTER CUSTOMER
        with tab1:
            st.info("Upload Master Pelanggan (Insert or Update)")
            file_master = st.file_uploader("File Customer (Excel/CSV)", type=['xlsx', 'csv'], key="up_master")
            
            if file_master and st.button("Proses Upload Master", type="primary"):
                df = pd.read_csv(file_master) if file_master.name.endswith('.csv') else pd.read_excel(file_master)
                df.columns = [str(col).strip().lower() for col in df.columns]
                
                # Mapping Kolom Sederhana
                col_map = {}
                for c in df.columns:
                    if 'alam' in c or 'addr' in c: col_map[c] = 'alamat'
                    elif 'kd' in c or 'id' in c: col_map[c] = 'cust_id'
                    elif 'nama' in c: col_map[c] = 'nama_cst'
                    elif 'sale' in c: col_map[c] = 'salesman_pengampu'
                
                df.rename(columns=col_map, inplace=True)
                
                if 'cust_id' in df.columns:
                    progress = st.progress(0)
                    with conn.session as s:
                        for i, row in df.iterrows():
                            # Upsert Logic Postgres
                            q_upsert = """
                                INSERT INTO master_customer (cust_id, nama_cst, alamat, salesman_pengampu)
                                VALUES (:id, :nm, :al, :sl)
                                ON CONFLICT (cust_id) 
                                DO UPDATE SET nama_cst=EXCLUDED.nama_cst, alamat=EXCLUDED.alamat
                                -- Note: Salesman tidak di-overwrite kalau kosong di excel, logic disederhanakan utk upsert
                            """
                            # Jika ingin logic kompleks (cek existing dulu), pakai SELECT dulu.
                            # Disini kita pakai Upsert simple
                            try:
                                s.execute(text(q_upsert), {
                                    "id": str(row['cust_id']),
                                    "nm": str(row.get('nama_cst', '-')),
                                    "al": str(row.get('alamat', '-')),
                                    "sl": str(row.get('salesman_pengampu', ''))
                                })
                            except Exception as e:
                                pass
                            if i % 10 == 0: progress.progress((i+1)/len(df))
                        s.commit()
                    st.success("Selesai Upload Master!")

        # TAB 2: TRANSAKSI
        with tab2:
            st.info("Upload Transaksi (Menggunakan Kunci Unik agar tidak duplikat)")
            file_trans = st.file_uploader("File Penjualan (Excel/CSV)", type=['xlsx', 'csv'], key="up_trans")
            
            if file_trans and st.button("Proses Upload Transaksi", type="primary"):
                df_tr = pd.read_csv(file_trans) if file_trans.name.endswith('.csv') else pd.read_excel(file_trans)
                df_tr.columns = [str(c).strip().lower() for c in df_tr.columns]
                
                required_cols = ['cust_id', 'tgl_sls', 'rep_sls', 'qty_sls', 'net_sls']
                missing = [c for c in required_cols if c not in df_tr.columns]
                
                if missing:
                    st.error(f"Kolom wajib hilang: {missing}")
                else:
                    progress = st.progress(0)
                    with conn.session as s:
                        for i, row in df_tr.iterrows():
                            try:
                                raw_tgl = row['tgl_sls']
                                val_tgl = pd.to_datetime(raw_tgl).date() if pd.notnull(raw_tgl) else None
                            except: val_tgl = None
                            
                            q_ins = """
                                INSERT INTO transactions (nomdok, tgl_sls, rep_sls, nama_spv, cust_id, nama_cst, kode_itm, nama_itm, qty_sls, net_sls)
                                VALUES (:nom, :tgl, :rep, :spv, :cid, :cnm, :kitm, :nitm, :qty, :net)
                                ON CONFLICT (nomdok, kode_itm, qty_sls, net_sls) DO NOTHING
                            """
                            try:
                                s.execute(text(q_ins), {
                                    "nom": str(row.get('nomdok', '')),
                                    "tgl": val_tgl,
                                    "rep": str(row['rep_sls']),
                                    "spv": str(row.get('nama_spv', '')),
                                    "cid": str(row['cust_id']),
                                    "cnm": str(row.get('nama_cst', '')),
                                    "kitm": str(row.get('kode_itm', '')),
                                    "nitm": str(row.get('nama_itm', '')),
                                    "qty": float(row['qty_sls']) if pd.notnull(row['qty_sls']) else 0.0,
                                    "net": float(row['net_sls']) if pd.notnull(row['net_sls']) else 0.0
                                })
                                
                                # Auto Update Mapping jika kosong
                                if row['rep_sls'] and str(row['rep_sls']) != 'nan':
                                    q_up_map = """
                                        UPDATE master_customer 
                                        SET salesman_pengampu = :s 
                                        WHERE cust_id = :id AND (salesman_pengampu IS NULL OR salesman_pengampu = '')
                                    """
                                    s.execute(text(q_up_map), {"s": str(row['rep_sls']), "id": str(row['cust_id'])})
                                    
                            except Exception as e:
                                pass # Skip error row
                            
                            if i % 10 == 0: progress.progress((i+1)/len(df_tr))
                        s.commit()
                    st.success("Transaksi Berhasil Diupload!")

    # --- HALAMAN 6: KELOLA USER ---
    elif selected == "Kelola User":
        st.markdown("## 👥 Manajemen Akun")
        tab_sales, tab_spv = st.tabs(["👤 Akun Salesman", "👔 Akun Supervisor"])
        
        with tab_sales:
            col1, col2 = st.columns(2)
            with col1:
                with st.form("add_sales"):
                    s_nama = st.text_input("Nama Salesman")
                    s_spv_ref = st.selectbox("Atasan (SPV)", get_data("SELECT nama_spv FROM master_spv")['nama_spv'].tolist())
                    s_pass = st.text_input("Password", value="123456")
                    
                    if st.form_submit_button("Buat Akun Sales"):
                        if s_nama:
                            uname = s_nama.lower().replace(" ", "")
                            run_query("INSERT INTO users (username, password, role, real_name, nama_spv) VALUES (:u, :p, 'salesman', :n, :spv)",
                                      params={"u": uname, "p": s_pass, "n": s_nama, "spv": s_spv_ref})
                            st.success(f"Dibuat: {uname}")
                            st.rerun()
            with col2:
                st.dataframe(get_data("SELECT username, real_name, nama_spv FROM users WHERE role='salesman'"), use_container_width=True)

        with tab_spv:
            col3, col4 = st.columns(2)
            with col3:
                with st.form("add_spv"):
                    spv_list = get_data("SELECT nama_spv FROM master_spv")['nama_spv'].tolist()
                    pilih_real = st.selectbox("Pilih Nama SPV", spv_list)
                    u_spv = st.text_input("Username")
                    p_spv = st.text_input("Password")
                    
                    if st.form_submit_button("Buat Akun SPV"):
                        run_query("INSERT INTO users (username, password, role, real_name, nama_spv) VALUES (:u, :p, 'spv', :n, '')",
                                  params={"u": u_spv, "p": p_spv, "n": pilih_real})
                        st.success("Akun SPV Dibuat")
            with col4:
                st.dataframe(get_data("SELECT username, real_name FROM users WHERE role='spv'"), use_container_width=True)

    # --- HALAMAN 7: MASTER SPV ---
    elif selected == "Master SPV":
        st.markdown("## 👔 Master Data Supervisor")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            new_spv = st.text_input("Nama Supervisor Baru")
            if st.button("Tambah ke Master", type="primary"):
                run_query("INSERT INTO master_spv (nama_spv) VALUES (:n)", params={"n": new_spv})
                st.success("Berhasil")
                st.rerun()
        with col_s2:
            st.dataframe(get_data("SELECT * FROM master_spv"), use_container_width=True)