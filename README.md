# Milvus Vector Search API

Una aplicación FastAPI que proporciona una API REST para búsqueda de similitud de vectores utilizando Milvus. Permite insertar textos que se convierten en vectores mediante el modelo `sentence-transformers`, y luego realizar búsquedas semánticas para encontrar textos similares.

## 🚀 Características

- **Búsqueda de similitud semántica**: Encuentra textos similares basándose en su significado
- **API REST simple**: Endpoints fáciles de usar para insertar y buscar textos
- **Base de datos vectorial**: Utiliza Milvus para almacenamiento y búsqueda eficiente de vectores
- **Modelo de embeddings**: Usa `paraphrase-albert-small-v2` para generar vectores de alta calidad
- **Documentación automática**: Swagger UI integrado para probar la API

## 📋 Prerrequisitos

- **Docker y Docker Compose** - Para ejecutar Milvus y sus dependencias
- **Python 3.8+** - Para ejecutar la aplicación FastAPI
- **Git** - Para clonar el repositorio

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd milvus-mvp
```

### 2. Iniciar los servicios de Milvus

Ejecuta el siguiente comando para iniciar Milvus y sus dependencias (etcd, Minio) en segundo plano:

```bash
docker-compose up -d
```

Espera unos segundos a que todos los servicios se inicien correctamente. Puedes verificar el estado con:

```bash
docker-compose ps
```

### 3. Instalar las dependencias de Python

Crea un entorno virtual (recomendado) e instala las librerías necesarias:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

Inicia el servidor de la API con Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

## 📚 Documentación de la API

Puedes acceder a la documentación interactiva de la API en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔌 Endpoints

### POST /insert

Inserta uno o más textos en la colección de Milvus. Los textos se convierten automáticamente en vectores usando el modelo de embeddings.

**Request Body:**
```json
{
  "texts": [
    "La inteligencia artificial está transformando el mundo.",
    "El sol es la estrella más cercana a la Tierra.",
    "La programación es el arte de resolver problemas."
  ]
}
```

**Response:**
```json
{
  "inserted": 3
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/insert" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "La inteligencia artificial está transformando el mundo.",
      "El sol es la estrella más cercana a la Tierra."
    ]
  }'
```

### POST /search

Busca textos similares a una consulta dada, retornando los `top_k` resultados más similares.

**Request Body:**
```json
{
  "query": "¿Qué es la inteligencia artificial?",
  "top_k": 3
}
```

**Response:**
```json
{
  "results": [
    "La inteligencia artificial está transformando el mundo.",
    "La programación es el arte de resolver problemas.",
    "El sol es la estrella más cercana a la Tierra."
  ]
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es la IA?",
    "top_k": 2
  }'
```

## 🏗️ Estructura del Proyecto

```
milvus-mvp/
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── milvus_client.py     # Cliente y operaciones de Milvus
│   └── data.py              # Funciones de procesamiento de datos
├── docker-compose.yml       # Configuración de servicios Docker
├── requirements.txt         # Dependencias de Python
├── render.yaml             # Configuración para despliegue en Render
└── README.md               # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

El proyecto utiliza las siguientes configuraciones por defecto:

- **Milvus URI**: `http://milvus-standalone:19530` (para Docker)
- **Puerto de la API**: `8000`
- **Modelo de embeddings**: `paraphrase-albert-small-v2`
- **Dimensión de vectores**: `768`

### Personalización

Para cambiar la configuración, modifica los valores en `app/milvus_client.py`:

```python
# Cambiar la URI de Milvus
client = MilvusClient(uri="tu_uri_de_milvus")

# Cambiar el modelo de embeddings
model = SentenceTransformer("tu_modelo_preferido")
```

## 🚀 Despliegue

### Render

El proyecto incluye configuración para despliegue automático en Render. El archivo `render.yaml` contiene la configuración necesaria.

### Docker

Para ejecutar en producción con Docker:

```bash
# Construir la imagen
docker build -t milvus-api .

# Ejecutar el contenedor
docker run -p 8000:8000 milvus-api
```

## 🧪 Pruebas

Para probar la API después de iniciarla:

1. **Insertar algunos textos de ejemplo:**
```bash
curl -X POST "http://localhost:8000/insert" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "La inteligencia artificial revoluciona la tecnología moderna.",
      "Los algoritmos de machine learning mejoran con más datos.",
      "La computación en la nube facilita el desarrollo de software."
    ]
  }'
```

2. **Buscar textos similares:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo funciona la IA?",
    "top_k": 2
  }'
```

## 🛑 Detener los Servicios

Para detener todos los servicios de Docker:

```bash
docker-compose down
```

Para detener y eliminar también los volúmenes:

```bash
docker-compose down -v
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la documentación de la API en `http://localhost:8000/docs`
2. Verifica que todos los servicios de Docker estén ejecutándose
3. Revisa los logs de Docker: `docker-compose logs`

## 🔗 Enlaces Útiles

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Milvus](https://milvus.io/docs)
- [Documentación de Sentence Transformers](https://www.sbert.net/)
