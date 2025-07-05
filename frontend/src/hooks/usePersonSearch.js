import { useCallback } from "react";
import useApi from "./useApi";

const usePersonSearch = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const searchPerson = useCallback(
    async (question) => {
      if (!question?.trim()) {
        throw new Error("La pregunta no puede estar vacía");
      }

      try {
        const result = await makeRequest("http://localhost:8000/find-person", {
          method: "POST",
          body: JSON.stringify({ question: question.trim() }),
        });

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
    return data.person || data.result || data.name || "Persona no encontrada";
  };

  return {
    loading,
    error,
    data,
    searchPerson,
    getPersonName,
    reset,
  };
};

export default usePersonSearch;
