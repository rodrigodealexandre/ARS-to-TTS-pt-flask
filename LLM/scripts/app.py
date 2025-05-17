from flask import Flask, render_template, request, jsonify
import os
import sys
import torch
from faster_whisper import WhisperModel
from TTS.api import TTS
import tempfile
import soundfile as sf
import numpy as np
import base64
import logging
import ffmpeg
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

def initialize_models():
    """Inicializa os modelos com tratamento de erros"""
    try:
        logger.info("Verificando disponibilidade de CUDA...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Usando device: {device}")

        logger.info("Inicializando modelo Whisper...")
        whisper_model = WhisperModel(
            model_size_or_path="small",  # Usando modelo menor para melhor performance
            device=device,
            compute_type="float16" if device == "cuda" else "float32",
            download_root=os.path.join(os.path.dirname(__file__), "models"),
            cpu_threads=4,  # Otimização para CPU threads
            num_workers=2   # Otimização para workers
        )
        logger.info("Modelo Whisper carregado com sucesso!")

        logger.info("Inicializando modelo TTS...")
        tts = TTS(
            model_name="tts_models/pt/cv/vits",
            gpu=True if device == "cuda" else False
        )
        logger.info("Modelo TTS carregado com sucesso!")

        return whisper_model, tts

    except Exception as e:
        logger.error(f"Erro na inicialização dos modelos: {str(e)}")
        sys.exit(1)

# Inicialização dos modelos
logger.info("Iniciando carregamento dos modelos...")
whisper_model, tts = initialize_models()
logger.info("Todos os modelos foram carregados com sucesso!")

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Erro ao renderizar template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

def convert_audio_to_wav(input_path, output_path):
    """Converte qualquer áudio para WAV 16kHz mono usando ffmpeg"""
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, ar=16000, ac=1, format='wav')
            .overwrite_output()
            .run(quiet=True)
        )
        return True
    except Exception as e:
        logger.error(f"Erro ao converter áudio com ffmpeg: {str(e)}")
        return False

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'Nenhum arquivo de áudio enviado'}), 400
    
    audio_file = request.files['audio']
    timings = {}
    
    # Criar diretório temporário para processar os arquivos
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Salvar e converter áudio
            start_time = time.time()
            
            ext = os.path.splitext(audio_file.filename)[-1] or '.webm'
            temp_input = os.path.join(temp_dir, f'input{ext}')
            audio_file.save(temp_input)
            
            # Converter para WAV com formato correto
            temp_converted = os.path.join(temp_dir, 'converted.wav')
            if not convert_audio_to_wav(temp_input, temp_converted):
                return jsonify({'error': 'Erro ao processar o arquivo de áudio'}), 500
                
            timings['audio_conversion'] = int((time.time() - start_time) * 1000)  # ms
            
            # Transcrição do áudio
            start_time = time.time()
            logger.info("Iniciando transcrição do áudio...")
            segments, info = whisper_model.transcribe(
                temp_converted,
                beam_size=3,  # Reduzido para melhor performance
                task="transcribe",
                vad_filter=True,
                initial_prompt="Transcreva o áudio em português."
            )
            
            transcription = " ".join([seg.text for seg in segments])
            logger.info(f"Transcrição concluída com sucesso: {transcription}")
            
            timings['transcription'] = int((time.time() - start_time) * 1000)  # ms
            
            # Gerar resposta em áudio
            start_time = time.time()
            response_text = f"Entendi: {transcription}"
            
            logger.info("Gerando áudio de resposta...")
            temp_response = os.path.join(temp_dir, 'response.wav')
            tts.tts_to_file(
                text=response_text,
                file_path=temp_response
            )
            
            timings['tts_generation'] = int((time.time() - start_time) * 1000)  # ms
            
            # Converter áudio para base64
            start_time = time.time()
            with open(temp_response, 'rb') as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode()
            
            timings['audio_encoding'] = int((time.time() - start_time) * 1000)  # ms
            
            # Calcular tempo total
            timings['total'] = sum(timings.values())
            
            return jsonify({
                'transcription': transcription,
                'audio_response': f'data:audio/wav;base64,{audio_base64}',
                'timings': timings
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar áudio: {str(e)}")
            return jsonify({'error': f'Erro ao processar áudio: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 