import { useCallback } from "react";
import useApi from "./useApi";

const useMultimodalSearch = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  // Datos mock para cuando la API no esté disponible
  const mockData = {
    "¿Qué pasó después?": [
      {
        content:
          "El portal comenzó a brillar con una luz intensa, revelando un mundo completamente diferente al otro lado.",
        type: "text",
        filename: null,
        url: null,
        score: 0.95,
      },
      {
        content:
          "Una figura sombría emergió del portal, sus ojos brillaban como estrellas en la oscuridad.",
        type: "text",
        filename: null,
        url: null,
        score: 0.87,
      },
      {
        content:
          "El suelo tembló mientras el portal se expandía, absorbiendo todo a su alrededor.",
        type: "text",
        filename: null,
        url: null,
        score: 0.82,
      },
    ],
    "¿Quién era esa figura?": [
      {
        content:
          "Era el guardián del portal, una entidad ancestral que protegía los secretos del multiverso.",
        type: "text",
        filename: null,
        url: null,
        score: 0.93,
      },
      {
        content:
          "La figura resultó ser una versión alternativa de uno mismo, venida del futuro.",
        type: "text",
        filename: null,
        url: null,
        score: 0.89,
      },
      {
        content:
          "Era el demonio que había estado observando todo el tiempo, finalmente revelando su verdadera forma.",
        type: "text",
        filename: null,
        url: null,
        score: 0.85,
      },
    ],
    "¿Qué secretos guardaba?": [
      {
        content:
          "El portal contenía el conocimiento de todas las realidades posibles, cada una más extraña que la anterior.",
        type: "text",
        filename: null,
        url: null,
        score: 0.91,
      },
      {
        content:
          "Era una biblioteca infinita de historias, donde cada libro contaba una versión diferente de la realidad.",
        type: "text",
        filename: null,
        url: null,
        score: 0.88,
      },
      {
        content:
          "Los secretos incluían la fórmula para viajar entre dimensiones y el poder de cambiar la realidad misma.",
        type: "text",
        filename: null,
        url: null,
        score: 0.84,
      },
    ],
    "¿Cómo terminó todo?": [
      {
        content:
          "El portal se cerró, pero la experiencia cambió para siempre la percepción de la realidad de todos los presentes.",
        type: "text",
        filename: null,
        url: null,
        score: 0.94,
      },
      {
        content:
          "Todos fueron absorbidos por el portal, iniciando una nueva aventura en un mundo completamente diferente.",
        type: "text",
        filename: null,
        url: null,
        score: 0.9,
      },
      {
        content:
          "El demonio se desvaneció, pero dejó una puerta abierta para futuras aventuras interdimensionales.",
        type: "text",
        filename: null,
        url: null,
        score: 0.86,
      },
    ],
  };

  const searchByText = useCallback(
    async (query, topK = 3) => {
      if (!query?.trim()) {
        throw new Error("La consulta no puede estar vacía");
      }

      try {
        const params = new URLSearchParams({
          query: query.trim(),
          top_k: topK.toString(),
        });

        const result = await makeRequest(
          `http://localhost:8000/search-by-text-multimodal?${params}`,
          {
            method: "GET",
          }
        );

        return result;
      } catch (err) {
        // Si la API falla, usar datos mock
        console.warn("API no disponible, usando datos mock:", err.message);
        const mockResults =
          mockData[query.trim()] || mockData["¿Qué pasó después?"];
        return mockResults.slice(0, topK);
      }
    },
    [makeRequest]
  );

  const getSearchResults = () => {
    if (!data) return [];
    return data || [];
  };

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
