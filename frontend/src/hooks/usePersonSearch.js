import { useCallback } from "react";
import useApi from "./useApi";

const usePersonSearch = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const searchPerson = useCallback(
    async (question, topK = 1, metricType = "COSINE") => {
      if (!question?.trim()) {
        throw new Error("La pregunta no puede estar vacía");
      }

      try {
        const params = new URLSearchParams({
          query: question.trim(),
          top_k: topK.toString(),
          metric_type: metricType,
        });

        const result = await makeRequest(
          `http://localhost:8000/find-person?${params}`,
          {
            method: "GET",
          }
        );

        return result;
      } catch (err) {
        throw err;
      }
    },
    [makeRequest]
  );

  const getPersonResults = () => {
    if (!data) return [];
    return data.results || [];
  };

  return {
    loading,
    error,
    data,
    searchPerson,
    getPersonResults,
    reset,
  };
};

export default usePersonSearch;
