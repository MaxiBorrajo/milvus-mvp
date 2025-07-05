import { useCallback } from "react";
import useApi from "./useApi";

const usePersonSearch = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const searchPerson = useCallback(
    async (question, topK = 1) => {
      if (!question?.trim()) {
        throw new Error("La pregunta no puede estar vacía");
      }

      try {
        const params = new URLSearchParams({
          query: question.trim(),
          top_k: topK.toString(),
        });

        const result = await makeRequest(
          `http://localhost:8000/find-person?${params}`,
          {
            method: "GET",
          }
        );

        return result;
      } catch (err) {
        // El error ya está manejado en useApi
        throw err;
      }
    },
    [makeRequest]
  );

  const getPersonName = () => {
    if (!data) return null;

    // Si tenemos resultados en formato lista
    if (data.results && Array.isArray(data.results)) {
      if (data.results.length === 1) {
        return (
          data.results[0].text ||
          data.results[0].content ||
          "Persona no encontrada"
        );
      }
      return data.results
        .map((result) => result.text || result.content)
        .join(", ");
    }

    // Fallback para formato anterior
    return data.person || data.result || data.name || "Persona no encontrada";
  };

  const getPersonResults = () => {
    if (!data) return [];
    return data.results || [];
  };

  return {
    loading,
    error,
    data,
    searchPerson,
    getPersonName,
    getPersonResults,
    reset,
  };
};

export default usePersonSearch;
