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
      await new Promise((resolve) => setTimeout(resolve, 800));
      // Simular búsqueda por tipo y devolver fragmentos mock
      const fragments = mockFragments[tipo] || [];
      const results = fragments.slice(0, topK);
      setData(results);
      return results;
    } catch (err) {
      setError(err.message);
      throw err;
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
