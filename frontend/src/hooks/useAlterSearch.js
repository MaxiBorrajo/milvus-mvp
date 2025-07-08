import { useCallback } from "react";
import useApi from "./useApi";

const useAlterSearch = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const searchEgo = useCallback(
    async (file) => {
      if (!file) {
        throw new Error("La imagen no fue subida");
      }

      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("top_k", "1");

        await makeRequest("http://localhost:8000/search-images", {
          method: "POST",
          body: formData,
        });

        return data;
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
