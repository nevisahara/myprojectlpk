# Import pustaka
import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

def utama():
    st.set_page_config(page_title="SmartBuffer", page_icon="🧪", layout="wide")

    # Styling CSS
    st.markdown("""
    <style>
        .skala-ph {
            height: 30px;
            background: linear-gradient(to right, #e74c3c, #f39c12, #f1c40f, #2ecc71, #3498db);
            border-radius: 15px;
            margin: 20px 0;
            position: relative;
        }
        .penanda-ph {
            position: absolute;
            top: -20px;
            transform: translateX(-50%);
            font-size: 12px;
        }
        .indikator-ph {
            position: absolute;
            top: -10px;
            width: 10px;
            height: 50px;
            background-color: #2c3e50;
            transform: translateX(-50%);
            border-radius: 5px;
        }
        .kotak-hasil {
            padding: 20px;
            background-color: #e8f4fc;
            border-radius: 10px;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title(":test_tube: SmartBuffer - Kalkulator pH Asam Basa")
    st.markdown("Aplikasi untuk menghitung pH berbagai jenis larutan asam-basa dan buffer")

    with st.container():
        kolom1, kolom2 = st.columns(2)

        with kolom1:
            jenis_larutan = st.selectbox(
                "Pilih Jenis Larutan:",
                options=["Asam Kuat", "Asam Lemah", "Basa Kuat", "Basa Lemah", "Buffer Asam", "Buffer Basa"],
                index=0,
                key="jenis_larutan"
            )

            konsentrasi = st.number_input("Konsentrasi (M):", min_value=0.0, step=1e-3, format="%.3f", value=0.1, key="konsentrasi")

            if jenis_larutan in ["Asam Lemah", "Buffer Asam"]:
                ka = st.number_input("Konstanta Keasaman (Ka):", min_value=0.0, step=1e-10, format="%.10f", value=1.8e-5, key="ka")

            if jenis_larutan in ["Basa Lemah", "Buffer Basa"]:
                kb = st.number_input("Konstanta Kebasaan (Kb):", min_value=0.0, step=1e-10, format="%.10f", value=1.8e-5, key="kb")

            if jenis_larutan in ["Buffer Asam", "Buffer Basa"]:
                kons_garam = st.number_input("Konsentrasi Garam (M):", min_value=0.0, step=1e-3, format="%.3f", value=0.1, key="garam")

            if st.button("Hitung pH", use_container_width=True):
                hasil = hitung_ph(jenis_larutan, konsentrasi, ka if jenis_larutan in ["Asam Lemah", "Buffer Asam"] else None,
                                  kb if jenis_larutan in ["Basa Lemah", "Buffer Basa"] else None,
                                  kons_garam if jenis_larutan in ["Buffer Asam", "Buffer Basa"] else None)

                with kolom2:
                    with st.expander("Hasil Perhitungan", expanded=True):
                        st.markdown(f"### pH = {hasil['ph']:.2f}")
                        st.markdown("""
                        <div class="skala-ph">
                            <span class="penanda-ph" style="left: 0%;">0</span>
                            <span class="penanda-ph" style="left: 16.66%;">2</span>
                            <span class="penanda-ph" style="left: 33.33%;">4</span>
                            <span class="penanda-ph" style="left: 50%;">7</span>
                            <span class="penanda-ph" style="left: 66.66%;">10</span>
                            <span class="penanda-ph" style="left: 83.33%;">12</span>
                            <span class="penanda-ph" style="left: 100%;">14</span>
                            <div class="indikator-ph" style="left: {}%; background-color: {};"></div>
                        </div>
                        """.format(min(max(hasil['ph'] / 14 * 100, 0), 100), warna_ph(hasil['ph'])), unsafe_allow_html=True)
                        st.markdown(f"**Penjelasan:** {hasil['penjelasan']}")

                        if jenis_larutan in ["Asam Lemah", "Basa Lemah"]:
                            grafik_spesies(jenis_larutan, konsentrasi, ka if jenis_larutan == "Asam Lemah" else kb)

        with st.expander("Informasi Tambahan"):
            st.markdown("""
            ### Rumus yang Digunakan:
            - **Asam Kuat**: pH = -log[H⁺]
            - **Asam Lemah**: pH = -log(√(Ka × [HA]))
            - **Basa Kuat**: pH = 14 - (-log[OH⁻])
            - **Basa Lemah**: pH = 14 - (-log(√(Kb × [B])))
            - **Buffer Asam**: pH = pKa + log([A⁻]/[HA])
            - **Buffer Basa**: pH = 14 - (pKb + log([BH⁺]/[B]))
            """)

def hitung_ph(jenis, kons, ka=None, kb=None, garam=None):
    hasil = {"ph": 7.0, "penjelasan": ""}
    try:
        if jenis == "Asam Kuat":
            h = kons
            ph = -math.log10(h)
            hasil["ph"] = ph
            hasil["penjelasan"] = f"Asam kuat terionisasi sempurna sehingga [H⁺] = {kons:.3f} M, maka pH = {ph:.2f}"

        elif jenis == "Asam Lemah":
            h = math.sqrt(ka * kons)
            ph = -math.log10(h)
            hasil["ph"] = ph
            hasil["penjelasan"] = f"Asam lemah sebagian terionisasi, [H⁺] dihitung dari √(Ka×[HA]) = {h:.3e}, pH = {ph:.2f}"

        elif jenis == "Basa Kuat":
            oh = kons
            poh = -math.log10(oh)
            ph = 14 - poh
            hasil["ph"] = ph
            hasil["penjelasan"] = f"Basa kuat terionisasi sempurna, [OH⁻] = {kons:.3f} M, maka pH = {ph:.2f}"

        elif jenis == "Basa Lemah":
            oh = math.sqrt(kb * kons)
            poh = -math.log10(oh)
            ph = 14 - poh
            hasil["ph"] = ph
            hasil["penjelasan"] = f"Basa lemah sebagian terionisasi, [OH⁻] = {oh:.3e}, pH = {ph:.2f}"

        elif jenis == "Buffer Asam":
            ph = -math.log10(ka) + math.log10(garam / kons)
            hasil["ph"] = ph
            hasil["penjelasan"] = f"Buffer asam dihitung dari pH = pKa + log([A⁻]/[HA]) = {ph:.2f}"

        elif jenis == "Buffer Basa":
            poh = -math.log10(kb) + math.log10(garam / kons)
            ph = 14 - poh
            hasil["ph"] = ph
            hasil["penjelasan"] = f"Buffer basa dihitung dari pOH = pKb + log([BH⁺]/[B]), maka pH = {ph:.2f}"

    except:
        hasil["ph"] = 7.0
        hasil["penjelasan"] = "Terjadi kesalahan input."
    return hasil

def warna_ph(ph):
    if ph < 3:
        return "#e74c3c"
    elif ph < 6:
        return "#f39c12"
    elif ph < 8:
        return "#f1c40f"
    elif ph < 11:
        return "#2ecc71"
    else:
        return "#3498db"

def grafik_spesies(jenis, kons, konstanta):
    fig, ax = plt.subplots(figsize=(6, 4))
    alpha = math.sqrt(konstanta / kons)
    terionisasi = alpha * 100
    tidak_terionisasi = 100 - terionisasi
    label = ['Terionisasi', 'Tidak Terionisasi']
    ukuran = [terionisasi, tidak_terionisasi]
    warna = ['#e74c3c', '#3498db'] if jenis == "Asam Lemah" else ['#3498db', '#e74c3c']
    ax.pie(ukuran, labels=label, colors=warna, autopct='%1.1f%%', startangle=90)
    ax.set_title(f"Distribusi Spesies {jenis} (K = {konstanta:.2e})")
    st.pyplot(fig)

if __name__ == "__main__":
    utama()
