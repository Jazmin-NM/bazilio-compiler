import streamlit as st
import os
import subprocess

st.title("Generador Musical - Bazilio")
st.write("Escribe tus notas en Bazilio y genera partituras y audio directamente desde la web.")

notas_usuario = st.text_area("Acordes o notas:", value="B C A", height=150)

if st.button("Generar y Reproducir Audio"):
    if not notas_usuario.strip():
        st.warning("Por favor, ingresa algunas notas.")
    else:
        codigo_bazilio = f"Main |:\n    (:){{{notas_usuario}}}\n:|"
        
        os.makedirs("programas", exist_ok=True)
        ruta_archivo = "programas/web_dinamico.bzl"
        
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(codigo_bazilio)
            
        try:
            resultado = subprocess.run(
                ["python3", "bazilio_etapa6.py", ruta_archivo],
                capture_output=True,
                text=True,
                check=True
            )
            st.success("¡Archivos generados correctamente!")
            # Muestra los avisos internos del compilador si los hubiera
            if resultado.stdout:
                st.info(f"Mensajes del compilador:\n{resultado.stdout}")

            base_path, _ = os.path.splitext(ruta_archivo)
            wav_path = base_path + ".wav"
            mp3_path = base_path + ".mp3"
            
            audio_a_reproducir = None
            if os.path.exists(mp3_path):
                audio_a_reproducir = mp3_path
            elif os.path.exists(wav_path):
                audio_a_reproducir = wav_path
                
            if audio_a_reproducir and os.path.exists(audio_a_reproducir):
                st.audio(audio_a_reproducir)
                with open(audio_a_reproducir, "rb") as file:
                    st.download_button(
                        label="Descargar Audio",
                        data=file,
                        file_name=os.path.basename(audio_a_reproducir),
                        mime="audio/mp3"
                    )
            else:
                st.info("Se generó la partitura pero no se encontró el archivo de audio para reproducción directa.")
                
        except subprocess.CalledProcessError as e:
            st.error(f"Error de compilación:\n{e.stderr}")