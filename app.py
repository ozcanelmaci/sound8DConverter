import streamlit as st
from pydub import AudioSegment
import numpy as np
import io
import math

st.set_page_config(page_title="8D Ses Dönüştürücü", layout="centered")

def apply_8d_effect(audio, pan_boundary=1.0, speed=0.05):
    """
    Sesi küçük parçalara böler ve her parçanın pan (sağ-sol) ayarını 
    bir sinüs dalgası kullanarak değiştirir.
    """
    chunk_length_ms = 50 # Sesi 50 milisaniyelik dilimlere bölüyoruz
    chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    
    output = AudioSegment.empty()
    
    for i, chunk in enumerate(chunks):
        # Sinüs dalgası ile -1.0 (Tam Sol) ve 1.0 (Tam Sağ) arasında yumuşak bir geçiş yaratıyoruz
        pan_value = math.sin(i * speed) * pan_boundary
        
        # Sadece stereo (2 kanallı) seslerde pan yapılabilir
        if chunk.channels == 1:
            chunk = chunk.set_channels(2)
            
        panned_chunk = chunk.pan(pan_value)
        output += panned_chunk
        
    return output

st.title("🎧 8D Müzik Dönüştürücü")
st.write("Yüklediğin müziği sağ ve sol hoparlörler arasında dolaşan, rahatlatıcı bir 8D formata dönüştür.")

uploaded_file = st.file_uploader("Bir ses dosyası yükle (MP3 veya WAV)", type=["mp3", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/mp3')
    
    speed = st.slider("Dönüş Hızı (Sesin sağdan sola geçiş hızı)", min_value=0.01, max_value=0.10, value=0.03, step=0.01)

    if st.button("8D'ye Dönüştür"):
        with st.spinner('Sihir gerçekleşiyor, lütfen bekle...'):
            # Sesi pydub ile oku
            audio = AudioSegment.from_file(uploaded_file)
            
            # Efekti uygula
            processed_audio = apply_8d_effect(audio, speed=speed)
            
            # Çıktıyı belleğe al (indirme ve dinletme için)
            buffer = io.BytesIO()
            processed_audio.export(buffer, format="mp3")
            buffer.seek(0)
            
            st.success("Dönüştürme Tamamlandı!")
            
            # Dönüştürülmüş hali dinlet
            st.audio(buffer, format='audio/mp3')
            
            # İndirme butonu
            st.download_button(
                label="🎵 8D Versiyonu İndir",
                data=buffer,
                file_name="8D_donusturulmus_muzik.mp3",
                mime="audio/mp3"
            )
