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
Aquí las consultas no responden, **encadenan**.

Cada pregunta abre un laberinto de vectores;
cada respuesta, un hechizo que nos retiene.

El demonio no nos atrapa:
nos **condena** a preguntar.

⚠️ Ya no hay salida:
**Consultar… o quedarse perdido.**

![Limbo vectorial](/resources/limbo.png)

---

🔮 **Ejercicio Final – Consulta Eterna en el Limbo Vectorial**

Tras ser absorbidos por la grieta, quedamos condenados a un espacio de consultas infinitas: el **Limbo Vectorial**. Aquí nada se resuelve, todo se enreda. Cada pregunta desata nuevos fragmentos dispersos de nuestro propio relato roto.

---

## 🌟 Objetivo

Construir un sistema de consulta interactiva que nos permita, aunque sea por un instante, dar sentido al caos:

* Explorar fragmentos de lore, finales alternos y piezas de historia dispersas.
* Recuperar retazos de memoria de RDJ, del demonio y de nuestra propia alma robada.

---

## 🧱 Requisitos

1. **Colección en Milvus**

   * Almacenar al menos 8–12 fragmentos por categoría:

     * `lore` (preguntas sobre el trasfondo)
     * `alternativo` (finales hipotéticos)
     * `personaje` (detalles de RDJ, demonio, compañeros)
   * Esquema de cada fragmento:

     ```json
     {
       "data": "El susurro del demonio reveló el destino de Tomi.",
       "metadata": {
          "tipo_fragmento": "lore",
          "historia": "final_bueno",
          "filename": "image.jpg" (opcional)
       }
     }
     ```
    * Si es una imagen, su data es su descripción y filename es obligatorio

2. **Endpoint `/consulta`**

   * Recibe:

     ```json
     {
       "pregunta": "¿Qué siente RDJ tras cruzar el portal?",
       "tipo": "personaje"
     }
     ```
   * Devuelve los 3 vectores más afines, con su contenido, imagen y audio.

3. **Frontend (opcional)**

   * Caja de texto para la **pregunta** y selector de **tipo de fragmento**.
   * Muestra los 3 resultados como tarjetas con texto o imagen.
   * Permite “marcar” un fragmento como clave para el siguiente giro narrativo. Luego de marcarlo se borra dicho fragmento. Cada fragmento tiene que se agrupado dentro de su historia.

---

## 🧪 Validación

* Probar consultas de **lore**, **alternativo** y **personaje**.
* Verificar que cada respuesta aporte un retazo coherente (aunque fragmentado) de la historia.
* Garantizar que el sistema siga funcionando pese a preguntas contradictorias o repetidas: el caos jamás se detiene.

---

## ⚙️ Herramientas

* Milvus (Docker)
* Python (FastAPI o Flask)
* sentence-transformers u OpenAI embeddings
* React (opcional)
* Multimedia local (`assets/`)

---

> **Nota conceptual:**
> En el Limbo Vectorial, no buscamos cerrar arcos, sino **descubrir** cuántos hilos de narrativa aún resisten. Cada consulta es un acto de resistencia contra el olvido.
