import streamlit as st
import os
import subprocess
import glob

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

        # Borra archivos de ejecuciones anteriores para no reproducir audio viejo
        base_path = os.path.splitext(ruta_archivo)[0]
        for ext in (".ly", ".midi", ".wav", ".mp3", ".pdf"):
            if os.path.exists(base_path + ext):
                os.remove(base_path + ext)
        for png in glob.glob(base_path + "-pagina*.png"):
            os.remove(png)

        try:
            resultado = subprocess.run(
                ["python3", "bazilio_etapa6.py", ruta_archivo],
                capture_output=True,
                text=True,
                check=True
            )
            st.success("¡Archivos generados correctamente!")

            # Avisos internos del compilador (si los hubiera)
            if resultado.stdout:
                st.code(resultado.stdout)
            if resultado.stderr:
                st.warning(f"Detalles:\n{resultado.stderr}")

            wav_path = base_path + ".wav"
            mp3_path = base_path + ".mp3"

            audio_a_reproducir = None
            if os.path.exists(mp3_path):
                audio_a_reproducir = mp3_path
            elif os.path.exists(wav_path):
                audio_a_reproducir = wav_path
                
            #NUEVO: mostrar la partitura en pantalla
            imagenes = sorted(glob.glob(base_path + "-pagina*.png"))
            if imagenes:
                st.subheader("Partitura")
                for ruta_png in imagenes:
                    st.image(ruta_png, use_container_width=True)

            if audio_a_reproducir:
                st.audio(audio_a_reproducir)
                with open(audio_a_reproducir, "rb") as file:
                    st.download_button(
                        label="Descargar Audio",
                        data=file,
                        file_name=os.path.basename(audio_a_reproducir),
                        mime="audio/mpeg" if audio_a_reproducir.endswith(".mp3") else "audio/wav"
                    )
            else:
                st.info("Se generó la partitura pero no se encontró el archivo de audio para reproducción directa.")

            # >>> NUEVO: descarga de la partitura en PDF
            pdf_path = base_path + ".pdf"
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label="Descargar Partitura (PDF)",
                        data=file,
                        file_name="partitura_bazilio.pdf",
                        mime="application/pdf"
                    )
            else:
                st.info("No se pudo generar el PDF de la partitura.")

        except subprocess.CalledProcessError as e:
            st.error(f"Error de compilación:\n{e.stderr}")