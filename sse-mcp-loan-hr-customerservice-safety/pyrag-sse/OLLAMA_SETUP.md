# Ollama Setup Guide for PyRAGDoc SSE

## Quick Start with Docker Compose (Recommended)

Docker Compose จะจัดการทุกอย่างให้อัตโนมัติ รวมถึง:
- รัน Ollama service
- ดาวน์โหลด embedding model (nomic-embed-text)
- เชื่อมต่อกับ PyRAGDoc

```bash
# รันทั้งหมดพร้อมกัน
docker-compose up
```

## Manual Ollama Setup

ถ้าต้องการรัน Ollama แยกต่างหาก:

### 1. ติดตั้ง Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Docker:**
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 2. เริ่ม Ollama Service

```bash
# รัน Ollama service
ollama serve
```

### 3. ดาวน์โหลด Embedding Model

```bash
# Pull embedding model ที่ใช้ (768 dimensions)
ollama pull nomic-embed-text
```

### 4. ตรวจสอบ Model

```bash
# ดูรายการ models ที่ติดตั้งแล้ว
ollama list

# ทดสอบ embedding
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "test embedding"
}'
```

## Embedding Models ที่รองรับ

| Model | Dimensions | Size | คำแนะนำ |
|-------|------------|------|---------|
| **nomic-embed-text** | 768 | 274MB | ✅ Default - แนะนำ, สมดุลระหว่างคุณภาพและขนาด |
| all-minilm | 384 | 46MB | เล็ก, เร็ว แต่คุณภาพต่ำกว่า |
| e5-small | 384 | 70MB | เล็ก, ภาษาอังกฤษดี |
| e5-large | 1024 | 1.3GB | คุณภาพสูง แต่ใหญ่และช้า |

## การตั้งค่าใน .env

```env
# Embedding Configuration
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
OLLAMA_URL=http://localhost:11434  # หรือ http://ollama:11434 ถ้าใช้ Docker
```

## Troubleshooting

### 1. Connection refused to Ollama

```bash
# ตรวจสอบว่า Ollama ทำงานอยู่
curl http://localhost:11434/api/tags

# ถ้าใช้ Docker, ตรวจสอบ container
docker ps | grep ollama
docker logs pyrag-ollama
```

### 2. Model not found

```bash
# ดาวน์โหลด model ใหม่
ollama pull nomic-embed-text

# หรือถ้าใช้ Docker
docker exec pyrag-ollama ollama pull nomic-embed-text
```

### 3. Out of memory

```bash
# ใช้ model ที่เล็กกว่า
EMBEDDING_MODEL=all-minilm ollama pull all-minilm
```

### 4. Slow embedding generation

- ตรวจสอบ CPU/Memory usage
- พิจารณาใช้ GPU (ถ้ามี)
- ใช้ model ที่เล็กกว่า

## Performance Tips

1. **Pre-pull models**: ดาวน์โหลด models ก่อนใช้งานจริง
2. **Use GPU**: ถ้ามี GPU, Ollama จะใช้อัตโนมัติ
3. **Batch processing**: ประมวลผลเอกสารเป็นกลุ่ม
4. **Cache embeddings**: PyRAGDoc จะ cache ใน Qdrant อัตโนมัติ

## Vector Database Compatibility

nomic-embed-text (768 dims) ทำงานได้ดีกับ:
- ✅ Qdrant (default)
- ✅ Pinecone
- ✅ Weaviate
- ✅ Milvus
- ✅ ChromaDB

## Security Notes

- Ollama API ไม่มี authentication by default
- ใน production ควรใช้ reverse proxy + authentication
- จำกัดการเข้าถึง ports (11434)
