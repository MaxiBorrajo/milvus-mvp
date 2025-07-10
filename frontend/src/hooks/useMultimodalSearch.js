import { useState, useCallback } from "react";

const mockFragments = {
  lore: [
    {
      content: "El susurro del demonio reveló el destino de Tomi.",
      type: "text",
      metadata: { tipo_fragmento: "lore", historia: "final_bueno" },
      score: 0.95,
    },
    {
      content: "La grieta absorbió la esperanza de todos.",
      type: "text",
      metadata: { tipo_fragmento: "lore", historia: "final_malo" },
      score: 0.91,
    },
    {
      content: "El limbo vectorial se expande con cada pregunta.",
      type: "image",
      url: "/resources/limbo.png",
      filename: "limbo.png",
      metadata: { tipo_fragmento: "lore", historia: "final_caos" },
      score: 0.89,
    },
  ],
  alternativo: [
    {
      content: "RDJ nunca saltó, y el portal se cerró para siempre.",
      type: "text",
      metadata: { tipo_fragmento: "alternativo", historia: "final_bueno" },
      score: 0.93,
    },
    {
      content: "El demonio se volvió aliado inesperado.",
      type: "text",
      metadata: { tipo_fragmento: "alternativo", historia: "final_raro" },
      score: 0.88,
    },
    {
      content: "Un eco de risas quedó flotando en el limbo.",
      type: "audio",
      url: "/resources/audio_mock.mp3",
      filename: "audio_mock.mp3",
      metadata: { tipo_fragmento: "alternativo", historia: "final_caos" },
      score: 0.85,
    },
  ],
  personaje: [
    {
      content:
        "RDJ siente una mezcla de miedo y curiosidad tras cruzar el portal.",
      type: "text",
      metadata: { tipo_fragmento: "personaje", historia: "final_bueno" },
      score: 0.92,
    },
    {
      content:
        "El demonio observa desde la grieta, esperando nuevas preguntas.",
      type: "image",
      url: "/resources/demonio_1.png",
      filename: "demonio_1.png",
      metadata: { tipo_fragmento: "personaje", historia: "final_malo" },
      score: 0.89,
    },
    {
      content: "Tomi brinda con una cerveza incluso en el limbo.",
      type: "image",
      url: "/resources/tomi.png",
      filename: "tomi.png",
      metadata: { tipo_fragmento: "personaje", historia: "final_raro" },
      score: 0.87,
    },
  ],
};

const useMultimodalSearch = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const searchByText = useCallback(async (query, topK = 3, tipo = "lore") => {
    if (!query?.trim()) {
      throw new Error("La consulta no puede estar vacía");
    }
    setLoading(true);
    setError(null);
    try {
      // Normalizar tipo para el backend
      let tipoBackend = tipo;
      if (tipo === "alternativo") tipoBackend = "alternativo";
      else if (tipo === "personaje") tipoBackend = "personaje";
      else tipoBackend = "lore";
      const params = new URLSearchParams({
        pregunta: query,
        tipo_fragmento: tipoBackend,
      });
      const response = await fetch(
        `http://localhost:8000/search-by-text-multimodal?${params.toString()}`
      );
      if (!response.ok) throw new Error("Error en la API");
      const apiResults = await response.json();
      // Mapear la respuesta real del backend al formato esperado por el frontend
      const mapped = (
        Array.isArray(apiResults) ? apiResults : apiResults.results || []
      ).map((item) => ({
        id: item.id,
        content: item.data,
        type: item.type,
        url: item.url,
        filename: item.filename,
        score: item.score,
        metadata: {
          tipo_fragmento: item.tipo_fragmento,
          historia: item.tipo_fragmento, // Si tienes un campo historia real, cámbialo aquí
        },
      }));
      setData(mapped.slice(0, topK));
      return mapped.slice(0, topK);
    } catch (err) {
      // Fallback al mock si la API falla
      const fragments = mockFragments[tipo] || [];
      const results = fragments.slice(0, topK);
      setData(results);
      setError("No se pudo conectar al backend, usando datos simulados.");
      return results;
    } finally {
      setLoading(false);
    }
  }, []);

  const getSearchResults = () => {
    if (!data) return [];
    return data || [];
  };

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    loading,
    error,
    data,
    searchByText,
    getSearchResults,
    reset,
  };
};

export default useMultimodalSearch;

// Eliminar fragmento por filename (por ahora, ya que no hay endpoint directo por ID)
export async function deleteFragmentByFilename(filename) {
  const response = await fetch(
    `http://localhost:8000/documents/by-filenamePorIds/${encodeURIComponent(
      filename
    )}`,
    {
      method: "DELETE",
    }
  );
  if (!response.ok) throw new Error("No se pudo eliminar el fragmento");
  return await response.json();
}

// Eliminar fragmento por id (nuevo endpoint)
export async function deleteFragmentById(id, tipo = "text") {
  const response = await fetch(
    `http://localhost:8000/delete-vector?collection=${tipo == "text"? "text_collection" : "multimodal_collection"}&id=${id}`,
    {
      method: "DELETE",
     }
  );
  if (!response.ok) throw new Error("No se pudo eliminar el fragmento por id");
  return await response.json();
}
