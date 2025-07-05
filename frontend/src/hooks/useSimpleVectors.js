import { useCallback, useState } from "react";
import useApi from "./useApi";

const useSimpleVectors = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const getPersonVectors = useCallback(async () => {
    try {
      const result = await makeRequest(
        "http://localhost:8000/vectors?collection=persons&dim=2",
        {
          method: "GET",
        }
      );

      return result;
    } catch (err) {
      throw err;
    }
  }, [makeRequest]);

  return {
    loading,
    error,
    data,
    getPersonVectors,
    reset,
  };
};

export default useSimpleVectors;
