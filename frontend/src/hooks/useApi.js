import { useState, useCallback } from "react";

const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const makeRequest = useCallback(async (url, options = {}) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const defaultOptions = {
        // headers: {
        //   "Content-Type": "application/json",
        // },
        ...options,
      };

      const response = await fetch(url, defaultOptions);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
      return result;
    } catch (err) {
      const errorMessage =
        err.message || "Error en la conexión con el servidor";
      setError(errorMessage);
      console.error("API Error:", err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);

  return {
    loading,
    error,
    data,
    makeRequest,
    reset,
  };
};

export default useApi;
