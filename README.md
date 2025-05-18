# 📢 Assistente de Voz em Português (Flask + Whisper + TTS)

## Sumário

- [Descrição](#descrição)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração dos Modelos](#configuração-dos-modelos)
- [Como Usar](#como-usar)
- [Arquitetura do Projeto](#arquitetura-do-projeto)
- [Customização](#customização)
- [Dicas de Performance](#dicas-de-performance)
- [Resolução de Problemas](#resolução-de-problemas)
- [Licença](#licença)
- [Referências](#referências)

---

## Descrição

Este projeto é um assistente de voz em português, com interface web, que permite ao usuário gravar ou enviar um áudio, transcrevê-lo usando o modelo Whisper (OpenAI) e responder com áudio gerado por TTS (Text-to-Speech). O sistema é otimizado para rodar em GPU (NVIDIA) e suporta sotaque brasileiro e português europeu, dependendo do modelo TTS escolhido.

---

## Funcionalidades

- Interface web moderna (Bootstrap)
- Gravação de áudio via navegador ou upload de arquivo
- Transcrição automática de áudio usando Whisper
- Resposta em áudio gerada por TTS (Text-to-Speech)
- Exibição dos tempos de processamento de cada etapa
- Suporte a múltiplos formatos de áudio (webm, wav, mp3, etc)
- Otimizado para uso com GPU (CUDA/cuDNN)
- Fácil customização de modelos e sotaques

---

## Requisitos

### Hardware
- Placa de vídeo NVIDIA (recomendado para performance)
- 8GB+ RAM

### Sistema Operacional
- Ubuntu 22.04+ (testado também em WSL2)

### Dependências do Sistema
- Python 3.8+
- ffmpeg
- CUDA 12.x
- cuDNN compatível

---

## Instalação

### 1. Instale dependências do sistema

```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-setuptools python3-pip python3-wheel
sudo apt-get install -y build-essential libssl-dev libffi-dev
sudo apt-get install -y espeak-ng python3-espeak ffmpeg
```

### 2. Instale CUDA/cuDNN (se for usar GPU)

Siga as instruções do README ou do script `setup.sh` para instalar CUDA e cuDNN compatíveis com sua GPU.

### 3. Crie e ative o ambiente virtual

```bash
python3 -m venv LLM
source LLM/bin/activate
```

### 4. Instale as dependências Python

```bash
pip install -r LLM/scripts/requirements.txt
```

> **Nota:** O arquivo `requirements.txt` já está ordenado para evitar conflitos de dependências.

---

## Configuração dos Modelos

### Whisper (Reconhecimento de Fala)

- O modelo padrão é o `small` (bom equilíbrio entre velocidade e precisão).
- Para mais velocidade, use `base` ou `tiny`. Para mais precisão, use `medium` ou `large`.

### TTS (Síntese de Voz)

- Para português brasileiro mais natural, use:  
  `tts_models/pt/br/vits-neural`
- Para português europeu, use:  
  `tts_models/pt/cv/vits`
- Para flexibilidade e vozes diferentes, use:  
  `tts_models/multilingual/multi-dataset/your_tts`

Altere o parâmetro `model_name` na inicialização do TTS em `app.py` conforme desejado.

---

## Como Usar

1. Inicie o servidor Flask:
   ```bash
   python LLM/scripts/app.py
   ```
2. Acesse no navegador:  
   [http://localhost:5000](http://localhost:5000)

3. Grave um áudio ou faça upload de um arquivo.

4. Aguarde a transcrição e a resposta em áudio.  
   Os tempos de processamento de cada etapa aparecerão na tela.

---

## Arquitetura do Projeto

```
LLM/
├── scripts/
│   ├── app.py                # Backend Flask + lógica de processamento
│   ├── requirements.txt      # Dependências Python
│   ├── setup.sh              # Script de instalação automatizada
│   └── templates/
│       └── index.html        # Interface web (frontend)
├── static/                   # (opcional) Arquivos estáticos
├── services/                 # (opcional) Serviços auxiliares
└── README.md                 # Documentação
```

### Fluxo de Processamento

1. **Frontend**: Gravação/upload → Envio do áudio para `/process_audio`
2. **Backend**:
   - Salva e converte o áudio para WAV (ffmpeg)
   - Transcreve com Whisper
   - Gera resposta com TTS
   - Codifica resposta em base64
   - Retorna transcrição, áudio e tempos de processamento
3. **Frontend**: Exibe transcrição, toca resposta e mostra tempos

---

## Customização

### Trocar modelo Whisper
No `app.py`, altere:
```python
whisper_model = WhisperModel(
    model_size_or_path="small",  # ou "base", "tiny", "medium", "large"
    ...
)
```

### Trocar modelo TTS
No `app.py`, altere:
```python
tts = TTS(
    model_name="tts_models/pt/br/vits-neural",  # ou outro modelo
    ...
)
```

### Trocar voz (YourTTS)
```python
tts.tts_to_file(
    text=response_text,
    file_path=temp_response,
    speaker='pt_001'  # Veja tts.speakers para opções
)
```

---

## Dicas de Performance

- Use GPU (CUDA) para Whisper e TTS para máxima velocidade.
- Use modelos menores para respostas mais rápidas.
- Reduza o parâmetro `beam_size` na transcrição para acelerar.
- Ajuste `cpu_threads` e `num_workers` conforme seu hardware.

---

## Resolução de Problemas

### Erro: `Format not recognised` ao processar áudio
- Certifique-se que o ffmpeg está instalado.
- O frontend pode enviar `.webm` ou `.mp3`. O backend converte para `.wav` automaticamente.

### Erro: `Model is not multi-lingual but language is provided`
- Não passe o parâmetro `language` para modelos TTS específicos de um idioma.

### Áudio TTS muito robótico ou sotaque de Portugal
- Troque para o modelo `tts_models/pt/br/vits-neural` ou `your_tts` para voz brasileira.

### CUDA/cuDNN não reconhecido
- Verifique se as versões instaladas são compatíveis com sua GPU e PyTorch.

### Demora na transcrição
- Use modelos menores do Whisper (`small`, `base`, `tiny`).

---

## Licença

Este projeto utiliza modelos open-source sob licenças Apache 2.0 e MIT. Consulte as licenças dos modelos utilizados para detalhes.

---

## Referências

- [Whisper (OpenAI) - HuggingFace](https://huggingface.co/openai/whisper-medium/blob/main/README.md)
- [Coqui TTS - Modelos](https://github.com/coqui-ai/TTS)
- [Bootstrap](https://getbootstrap.com/)
- [ffmpeg](https://ffmpeg.org/) 