import { useCallback } from "react";
import useFileApi from "./useFileApi";

const useAlterSearch = () => {
  const { loading, error, makeRequest, reset } = useFileApi();

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
