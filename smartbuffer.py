import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

def main():
    st.set_page_config(page_title="SmartBuffer", page_icon="🧪", layout="wide")
    
    # CSS styling
    st.markdown("""
    <style>
        .ph-scale {
            height: 30px;
            background: linear-gradient(to right, #e74c3c, #f39c12, #f1c40f, #2ecc71, #3498db);
            border-radius: 15px;
            margin: 20px 0;
            position: relative;
        }
        .ph-marker {
            position: absolute;
            top: -20px;
            transform: translateX(-50%);
            font-size: 12px;
        }
        .ph-indicator {
            position: absolute;
            top: -10px;
            width: 10px;
            height: 50px;
            background-color: #2c3e50;
            transform: translateX(-50%);
            border-radius: 5px;
        }
        .result-box {
            padding: 20px;
            background-color: #e8f4fc;
            border-radius: 10px;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🧪 SmartBuffer - Kalkulator pH Asam Basa")
    st.markdown("Aplikasi untuk menghitung pH berbagai jenis larutan asam-basa dan buffer")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            solution_type = st.selectbox(
                "Jenis Larutan:",
                options=[
                    "Asam Kuat",
                    "Asam Lemah",
                    "Basa Kuat",
                    "Basa Lemah",
                    "Buffer Asam",
                    "Buffer Basa"
                ],
                index=0,
                key="solution_type"
            )
            
            concentration = st.number_input(
                "Konsentrasi (M):",
                min_value=0.0,
                step=1e-3,
                format="%.3f",
                value=0.1,
                key="concentration"
            )
            
            if solution_type in ["Asam Lemah", "Buffer Asam"]:
                ka = st.number_input(
                    "Konstanta Keasaman (Ka):",
                    min_value=0.0,
                    step=1e-10,
                    format="%.10f",
                    value=1.8e-5,
                    key="ka"
                )
            
            if solution_type in ["Basa Lemah", "Buffer Basa"]:
                kb = st.number_input(
                    "Konstanta Kebasaan (Kb):",
                    min_value=0.0,
                    step=1e-10,
                    format="%.10f",
                    value=1.8e-5,
                    key="kb"
                )
            
            if solution_type in ["Buffer Asam", "Buffer Basa"]:
                salt_concentration = st.number_input(
                    "Konsentrasi Garam (M):",
                    min_value=0.0,
                    step=1e-3,
                    format="%.3f",
                    value=0.1,
                    key="salt_concentration"
                )
            
            if st.button("Hitung pH", use_container_width=True):
                result = calculate_ph(
                    solution_type,
                    concentration,
                    ka if solution_type in ["Asam Lemah", "Buffer Asam"] else None,
                    kb if solution_type in ["Basa Lemah", "Buffer Basa"] else None,
                    salt_concentration if solution_type in ["Buffer Asam", "Buffer Basa"] else None
                )
                
                with col2:
                    with st.expander("Hasil Perhitungan", expanded=True):
                        st.markdown(f"### pH = {result['ph']:.2f}")
                        
                        # Visualisasi skala pH
                        st.markdown("""
                        <div class="ph-scale">
                            <span class="ph-marker" style="left: 0%;">0</span>
                            <span class="ph-marker" style="left: 16.66%;">2</span>
                            <span class="ph-marker" style="left: 33.33%;">4</span>
                            <span class="ph-marker" style="left: 50%;">7</span>
                            <span class="ph-marker" style="left: 66.66%;">10</span>
                            <span class="ph-marker" style="left: 83.33%;">12</span>
                            <span class="ph-marker" style="left: 100%;">14</span>
                            <div class="ph-indicator" style="left: {}%; background-color: {};"></div>
                        </div>
                        """.format(
                            min(max(result['ph'] / 14 * 100, 0), 100),
                            get_ph_color(result['ph'])
                        ), unsafe_allow_html=True)
                        
                        st.markdown(f"**Penjelasan:** {result['explanation']}")
                        
                        # Grafik distribusi spesies (untuk asam/basa lemah)
                        if solution_type in ["Asam Lemah", "Basa Lemah"]:
                            plot_species_distribution(
                                solution_type,
                                concentration,
                                ka if solution_type == "Asam Lemah" else kb
                            )
            
            # Informasi tambahan
            with st.expander("Informasi Tambahan"):
                st.markdown("""
                ### Rumus yang Digunakan:
                
                - **Asam Kuat**: pH = -log[H⁺]
                - **Asam Lemah**: pH = -log(√(Ka × [HA]))
                - **Basa Kuat**: pH = 14 - (-log[OH⁻]))
                - **Basa Lemah**: pH = 14 - (-log(√(Kb × [B])))
                - **Buffer Asam**: pH = pKa + log([A⁻]/[HA])
                - **Buffer Basa**: pH = 14 - (pKb + log([BH⁺]/[B]))
                
                ### Contoh Nilai Ka dan Kb:
                
                | Senyawa | Ka/Kb |
                |---------|-------|
                | Asam asetat (CH₃COOH) | Ka = 1.8 × 10⁻⁵ |
                | Asam format (HCOOH) | Ka = 1.8 × 10⁻⁴ |
                | Amonia (NH₃) | Kb = 1.8 × 10⁻⁵ |
                | Metilamin (CH₃NH₂) | Kb = 4.4 × 10⁻⁴ |
                """)

def calculate_ph(solution_type, concentration, ka=None, kb=None, salt_concentration=None):
    result = {"ph": 7.0, "explanation": ""}
    
    try:
        if solution_type == "Asam Kuat":
            h_plus = concentration
            ph = -math.log10(h_plus)
            result["ph"] = ph
            result["explanation"] = (
                f"pH larutan asam kuat dengan konsentrasi {concentration:.3f} M adalah {ph:.2f}. "
                "Asam kuat terionisasi sempurna dalam air, sehingga [H⁺] sama dengan konsentrasi asam."
            )
        
        elif solution_type == "Asam Lemah":
            h_plus = math.sqrt(ka * concentration)
            ph = -math.log10(h_plus)
            result["ph"] = ph
            result["explanation"] = (
                f"pH larutan asam lemah dengan konsentrasi {concentration:.3f} M dan Ka = {ka:.2e} adalah {ph:.2f}. "
                "Asam lemah terionisasi sebagian dalam air, dan [H⁺] dihitung menggunakan konstanta kesetimbangan."
            )
        
        elif solution_type == "Basa Kuat":
            oh_minus = concentration
            poh = -math.log10(oh_minus)
            ph = 14 - poh
            result["ph"] = ph
            result["explanation"] = (
                f"pH larutan basa kuat dengan konsentrasi {concentration:.3f} M adalah {ph:.2f}. "
                "Basa kuat terionisasi sempurna dalam air, sehingga [OH⁻] sama dengan konsentrasi basa."
            )
        
        elif solution_type == "Basa Lemah":
            oh_minus = math.sqrt(kb * concentration)
            poh = -math.log10(oh_minus)
            ph = 14 - poh
            result["ph"] = ph
            result["explanation"] = (
                f"pH larutan basa lemah dengan konsentrasi {concentration:.3f} M dan Kb = {kb:.2e} adalah {ph:.2f}. "
                "Basa lemah terionisasi sebagian dalam air, dan [OH⁻] dihitung menggunakan konstanta kesetimbangan."
            )
        
        elif solution_type == "Buffer Asam":
            h_plus = ka * (concentration / salt_concentration)
            ph = -math.log10(h_plus)
            result["ph"] = ph
            result["explanation"] = (
                f"pH larutan buffer asam dengan konsentrasi asam {concentration:.3f} M, "
                f"konsentrasi garam {salt_concentration:.3f} M, dan Ka = {ka:.2e} adalah {ph:.2f}. "
                "Buffer asam mempertahankan pH dengan sistem kesetimbangan asam lemah dan basa konjugatnya."
            )
        
        elif solution_type == "Buffer Basa":
            oh_minus = kb * (concentration / salt_concentration)
            poh = -math.log10(oh_minus)
            ph = 14 - poh
            result["ph"] = ph
            result["explanation"] = (
                f"pH larutan buffer basa dengan konsentrasi basa {concentration:.3f} M, "
                f"konsentrasi garam {salt_concentration:.3f} M, dan Kb = {kb:.2e} adalah {ph:.2f}. "
                "Buffer basa mempertahankan pH dengan sistem kesetimbangan basa lemah dan asam konjugatnya."
            )
    
    except ValueError as e:
        st.error("Terjadi kesalahan dalam perhitungan. Pastikan input yang dimasukkan valid.")
        result["ph"] = 7.0
        result["explanation"] = "Error dalam perhitungan. Periksa nilai input Anda."
    
    return result

def get_ph_color(ph):
    if ph < 3:
        return "#e74c3c"  # Merah
    elif ph < 6:
        return "#f39c12"  # Oranye
    elif ph < 8:
        return "#f1c40f"  # Kuning
    elif ph < 11:
        return "#2ecc71"  # Hijau
    else:
        return "#3498db"  # Biru

def plot_species_distribution(solution_type, concentration, constant):
    fig, ax = plt.subplots(figsize=(8, 4))
    
    if solution_type == "Asam Lemah":
        # Hitung persentase ionisasi
        alpha = math.sqrt(constant / concentration)  # Derajat ionisasi
        ionized = alpha * 100
        unionized = 100 - ionized
        
        labels = ['Terionisasi', 'Tidak Terionisasi']
        sizes = [ionized, unionized]
        colors = ['#e74c3c', '#3498db']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title(f"Distribusi Spesies Asam Lemah (Ka = {constant:.2e})")
    
    elif solution_type == "Basa Lemah":
        # Hitung persentase ionisasi
        alpha = math.sqrt(constant / concentration)  # Derajat ionisasi
        ionized = alpha * 100
        unionized = 100 - ionized
        
        labels = ['Terionisasi', 'Tidak Terionisasi']
        sizes = [ionized, unionized]
        colors = ['#3498db', '#e74c3c']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title(f"Distribusi Spesies Basa Lemah (Kb = {constant:.2e})")
    
    st.pyplot(fig)

if __name__ == "__main__":
    main()