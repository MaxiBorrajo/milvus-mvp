# Milvus Vector UI App

Este proyecto es una aplicación FastAPI que proporciona una API para interactuar con una base de datos de vectores Milvus. Permite insertar textos, que se convierten en vectores mediante un modelo de `sentence-transformers`, y luego buscar textos similares dentro de la base de datos.

## Prerrequisitos

- Docker y Docker Compose
- Python 3.8+ y pip

## Cómo ejecutar el proyecto

1.  **Iniciar los servicios de Milvus:**

    Abre una terminal en la raíz del proyecto y ejecuta el siguiente comando para iniciar Milvus y sus dependencias (etcd, Minio) en segundo plano.

    ```bash
    docker-compose up -d
    ```

    Espera unos segundos a que todos los servicios se inicien correctamente.

2.  **Instalar las dependencias de Python:**

    En la misma terminal, crea un entorno virtual (recomendado) e instala las librerías necesarias desde `requirements.txt`.

    ```bash
    # (Opcional) Crear y activar un entorno virtual
    # python -m venv venv
    # source venv/bin/activate  # En Windows: venv\Scripts\activate

    pip install -r requirements.txt
    ```

3.  **Ejecutar la aplicación FastAPI:**

    Una vez instaladas las dependencias, inicia el servidor de la API con Uvicorn.

    ```bash
    uvicorn main:app --reload
    ```

    La API estará disponible en `http://127.0.0.1:8000`.

## Endpoints de la API

Puedes interactuar con la API a través de su documentación generada automáticamente por Swagger UI en `http://127.0.0.1:8000/docs`, o utilizando herramientas como `curl`.

### `POST /insert`

Inserta uno o más textos en la colección de Milvus.

**Ejemplo con `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/insert' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "items": [
    {
      "text": "La inteligencia artificial está transformando el mundo.",
      "subject": "tecnología"
    },
    {
      "text": "El sol es la estrella más cercana a la Tierra.",
      "subject": "ciencia"
    }
  ]
}'
```

### `POST /search`

Busca textos similares a una consulta.

**Ejemplo con `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "¿Qué es la IA?",
  "top_k": 1
}'
```
