import { useCallback } from "react";
import useApi from "./useApi";

const useAlterSearch = () => {
  const { loading, error, makeRequest, reset } = useApi();

  const searchEgo = useCallback(
    async (file) => {
      if (!file) {
        throw new Error("La imagen no fue subida");
      }

      try {
        const formData = new FormData();
        formData.append("file", file);

        const result = await makeRequest(
          `http://localhost:8000/search-images?top_k=${1}`,
          {
            method: "POST",
            body: formData,
          }
        );
        return result;
      } catch (err) {
        // El error ya está manejado en useApi
        throw err;
      }
    },
    // eslint-disable-next-line
    [makeRequest]
  );

  return {
    loading,
    error,
    searchEgo,
    reset,
  };
};

export default useAlterSearch;
