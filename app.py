import streamlit as st
from pydub import AudioSegment
import numpy as np
import io
import math
import yt_dlp
import os

st.set_page_config(page_title="8D Ses Dönüştürücü", layout="centered")

def apply_8d_effect(audio, pan_boundary=1.0, speed=0.05):
    """Sesi küçük parçalara böler ve pan ayarını bir sinüs dalgası kullanarak değiştirir."""
    chunk_length_ms = 50 
    chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    
    output = AudioSegment.empty()
    
    for i, chunk in enumerate(chunks):
        pan_value = math.sin(i * speed) * pan_boundary
        if chunk.channels == 1:
            chunk = chunk.set_channels(2)
        panned_chunk = chunk.pan(pan_value)
        output += panned_chunk
        
    return output

st.title("🎧 8D Müzik Dönüştürücü")
st.write("Bilgisayarından bir müzik yükle veya YouTube linki yapıştır!")

# Kullanıcının kaynak seçimi
input_method = st.radio("Müzik Kaynağını Seçin:", ("Bilgisayardan Yükle", "YouTube Linki"))

audio_source = None
audio_name = "8D_donusturulmus_muzik.mp3"

# 1. SEÇENEK: DOSYA YÜKLEME
if input_method == "Bilgisayardan Yükle":
    uploaded_file = st.file_uploader("Bir ses dosyası yükle (MP3 veya WAV)", type=["mp3", "wav"])
    if uploaded_file is not None:
        audio_source = uploaded_file
        audio_name = f"8D_{uploaded_file.name}"
        st.audio(uploaded_file, format='audio/mp3')

# 2. SEÇENEK: YOUTUBE LİNKİ
elif input_method == "YouTube Linki":
    youtube_url = st.text_input("YouTube Video Linkini Yapıştırın:")
    
    # YouTube'dan çekilen veriyi Streamlit yeniden yüklendiğinde kaybetmemek için session_state kullanıyoruz
    if 'yt_audio_bytes' not in st.session_state:
        st.session_state.yt_audio_bytes = None
        st.session_state.yt_audio_name = "8D_youtube_audio.mp3"

    if youtube_url:
        if st.button("Sesi Getir"):
            with st.spinner("YouTube'dan ses indiriliyor ve mp3'e dönüştürülüyor..."):
                try:
                    # yt-dlp ayarları: Sadece sesi al, en iyi kaliteyi seç ve mp3'e dönüştür
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': 'temp_yt_audio.%(ext)s',
                        'quiet': True,
                        'noplaylist': True
                        #JavaScript doğrulamasını atlamak için mobil istemci kullanıyoruz
                        'extractor_args': {
                            'youtube': ['player_client=android']
                        }
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(youtube_url, download=True)
                        fetched_title = info.get('title', 'youtube_audio')
                        
                    # İndirilen mp3 dosyasını belleğe al
                    with open('temp_yt_audio.mp3', 'rb') as f:
                        st.session_state.yt_audio_bytes = f.read()
                    st.session_state.yt_audio_name = f"8D_{fetched_title}.mp3"
                    
                    st.success(f"'{fetched_title}' başarıyla getirildi!")
                    
                    # Geçici dosyayı sistemden temizle
                    if os.path.exists('temp_yt_audio.mp3'):
                        os.remove('temp_yt_audio.mp3')
                        
                except Exception as e:
                    st.error(f"Bir hata oluştu: Videoya erişilemiyor veya link hatalı. Hata detayı: {e}")

    # Bellekte YouTube sesi varsa onu oynat ve kaynak olarak ayarla
    if st.session_state.yt_audio_bytes is not None:
        st.audio(st.session_state.yt_audio_bytes, format='audio/mp3')
        audio_source = io.BytesIO(st.session_state.yt_audio_bytes)
        audio_name = st.session_state.yt_audio_name


# DÖNÜŞTÜRME İŞLEMİ (Her iki kaynak için de ortak çalışır)
if audio_source is not None:
    st.markdown("---")
    st.subheader("8D Ayarları")
    speed = st.slider("Dönüş Hızı (Sesin sağdan sola geçiş hızı)", min_value=0.01, max_value=0.10, value=0.03, step=0.01)

    if st.button("8D'ye Dönüştür"):
        with st.spinner('8D sihirleri yapılıyor, lütfen bekle...'):
            # Sesi kaynağa göre (dosya veya bellek) pydub ile oku
            audio = AudioSegment.from_file(audio_source)
            
            processed_audio = apply_8d_effect(audio, speed=speed)
            
            buffer = io.BytesIO()
            processed_audio.export(buffer, format="mp3")
            buffer.seek(0)
            
            st.success("Dönüştürme Tamamlandı!")
            
            st.audio(buffer, format='audio/mp3')
            
            st.download_button(
                label="🎵 8D Versiyonu İndir",
                data=buffer,
                file_name=audio_name,
                mime="audio/mp3"
            )
