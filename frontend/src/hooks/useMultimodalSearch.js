import { useState, useCallback } from "react";

const useMultimodalSearch = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const searchByText = useCallback(async (query, topK = 3) => {
    if (!query?.trim()) {
      throw new Error("La consulta no puede estar vacía");
    }
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        pregunta: query,
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
      }));
      setData(mapped.slice(0, topK));
      return mapped.slice(0, topK);
    } catch (err) {
    
      setData([]);
      setError("No se pudo conectar al backend, usando datos simulados.");
      return [];
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
