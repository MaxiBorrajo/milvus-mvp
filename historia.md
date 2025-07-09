RDJ nos miró con ojos que habían cruzado el umbral de la comprensión.

—Ahora lo entiendo... El portal no es una salida —susurró mientras la realidad comenzaba a plegarse como papel mojado a su alrededor—. Es el retorno. No me sigan…

Y se lanzó.

No se desvaneció. Se integró.

En el silencio antinatural que siguió, comprendimos por fin lo que el demonio venía murmurando todo este tiempo. No eran advertencias… eran **llamados**. Una invitación a rendirse. A aceptar que la elección nunca fue nuestra.

Quedamos paralizados.  
RDJ se había ido.

¿Debíamos seguirlo? ¿Buscarlo? ¿Salvarlo?

Pero entonces...

Una risa hendió el aire. No como sonido, sino como una **grieta en la lógica**.

Del portal —palpitante, vivo, descompuesto— emergió una voz. Sin idioma. Sin forma.  
Pero todos **entendimos**.

![Demonio emergente](/resources/demonio_1.png)

La silueta del demonio volvió a manifestarse. Ya no como una sombra burlona, sino como una entidad absoluta. Su sonrisa desafiaba la geometría. Sus ojos eran la intersección de realidades.

El tiempo se quebró en capas.

Con un único gesto, el demonio se replegó hacia el portal, como si retrocediera hacia su núcleo. Y entonces, la grieta —contenida hasta ese instante— **se desbordó**.

Una garra colosal emergió. No para destruir.  
Sino para **absorber**.

Y atrapó primero a Tomi, que andaba distraído tomando una cerveza.

![Tomi es atrapado](/resources/tomi.png)

Nos lanzamos sin pensar.  
La desesperación nos impulsaba más que la razón. No podíamos perder a alguien más.

![Todos nos avalanzamos a rescatar a tomi](/resources/escena_dramatica.png)

Pero fue inútil.

Nos atrapó uno a uno.  
No como presas…  
sino como **fragmentos**.

Caímos sin caer. Flotamos sin dirección.  
Las reglas físicas fueron reemplazadas por otra lógica.

Una lógica **vectorial**.

Ahora estamos en el **Limbo Vectorial**.  
Una dimensión donde las historias no se cuentan: se **calculan**.

Donde cada decisión activa un vector.  
Cada consulta es un hechizo.  
Y cada camino… es solo uno de muchos posibles.

El demonio no nos encadena.  
Nos **invita**.

⚠️ Solo queda una elección:  
**Consultar… o ser consultado.**

![Limbo vectorial](/resources/limbo.png)

---

**Y así comienza tu historia.**

# 🔮 Ejercicio Final – Consulta Vectorial Multiversal

Tras ser arrastrados al Limbo Vectorial, cada uno de nosotros quedó suspendido en una dimensión sin tiempo ni forma. Aquí, las decisiones no se toman... se calculan.

En este escenario, tu tarea es construir un sistema de consulta interactiva que permita explorar los posibles caminos narrativos fragmentados del multiverso, utilizando una base de datos **vectorial**.

---

## 🌟 Objetivo

Implementar un sistema que, dada una entrada de texto y una fase narrativa, consulte una colección **multimodal** en **Milvus**, y devuelva 3 posibles fragmentos de historia con su metadata asociada:

* Texto narrativo
* Imagen relacionada
* Música ambiental
* Fase narrativa

---

## 🧹 ¿Qué es una historia vectorial?

La historia ha sido fragmentada en múltiples piezas vectorizadas, cada una correspondiente a un momento distinto del relato:

* `introduccion`
* `nudo`
* `desenlace`
* `final`

Cada fragmento fue insertado previamente en Milvus con embeddings generados a partir del texto e indexado por similitud semántica.

---

## 🧱 Requisitos del ejercicio

### 1. Cargar la colección en Milvus

Debe contener al menos 10 fragmentos por cada fase narrativa.

Cada item insertado en Milvus debe tener el siguiente esquema:

```json
{
  "content": "El aire se volvió irrespirable cuando el portal comenzó a latir.",
  "fase_historia": "nudo",
  "path_imagen": "assets/nudo_2.png",
  "path_audio": "assets/audio_siniestro_2.mp3"
}
```

---

### 2. Crear un endpoint de consulta

El endpoint `/consulta` debe recibir un JSON con este formato:

```json
{
  "input": "Quiero saber qué hay detrás del portal",
  "fase": "desenlace"
}
```

Y devolver un array con los 3 fragmentos más cercanos semánticamente al `input`, filtrando por `fase_historia`.

Ejemplo de respuesta:

```json
[
  {
    "content": "Lo que emergió no era el demonio… era su reflejo multiplicado.",
    "fase_historia": "desenlace",
    "path_imagen": "assets/fragmento_desenlace_3.png",
    "path_audio": "assets/ambient_desenlace.mp3"
  },
  ...
]
```

---

### 3. Frontend (opcional)

Implementar en React un módulo que:

* Permita ingresar texto e indicar la fase narrativa.
* Muestre los 3 resultados devueltos (texto, imagen y audio).
* Permita elegir uno de los fragmentos como “siguiente paso” en la historia.

---

## 🧪 Validación del ejercicio

El sistema debe permitir simular una aventura completa seleccionando fragmentos por fase en el orden:

```
introduccion → nudo → desenlace → final
```

Sin embargo, se permite romper esta estructura y armar caminos **no lineales** (como piezas de rompecabezas), incentivando el caos narrativo y lo emergente.

---

## ⚙️ Herramientas habilitadas

* [x] Milvus (standalone, Docker)
* [x] Python (FastAPI o Flask)
* [x] sentence-transformers u OpenAI embeddings
* [x] React para frontend
* [x] Archivos multimedia locales (`assets/`)

---

## 🧠 Desafío conceptual

Este ejercicio no es solo técnico: propone un nuevo modelo narrativo.

Aquí, **la historia no está escrita… está vectorizada**.

Dependerá de cada espectador elegir su camino.
Dependerá de tu implementación… que ese camino tenga sentido.

---
