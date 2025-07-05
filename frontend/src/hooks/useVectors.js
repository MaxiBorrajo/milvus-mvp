import { useCallback, useState } from "react";
import useApi from "./useApi";

const useVectors = () => {
  const { loading, error, data, makeRequest, reset } = useApi();
  const [selectedPoints, setSelectedPoints] = useState([]);

  const getVectors = useCallback(
    async (collection = "texts", limit = 100, dim = null) => {
      try {
        const params = new URLSearchParams({
          collection,
          limit: limit.toString(),
        });

        if (dim) {
          params.append("dim", dim.toString());
        }

        const result = await makeRequest(
          `http://localhost:8000/vectors?${params.toString()}`,
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

  const getVectors2D = useCallback(
    async (collection = "texts", limit = 100) => {
      try {
        const params = new URLSearchParams({
          collection,
          limit: limit.toString(),
        });

        const result = await makeRequest(
          `http://localhost:8000/vectors?${params.toString()}&dim=2`,
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

  const getVectors3D = useCallback(
    async (collection = "texts", limit = 100) => {
      try {
        const params = new URLSearchParams({
          collection,
          limit: limit.toString(),
        });

        const result = await makeRequest(
          `http://localhost:8000/vectors?${params.toString()}&dim=3`,
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

  const selectPoint = useCallback((point) => {
    setSelectedPoints((prev) => {
      const exists = prev.find((p) => p.id === point.id);
      if (exists) {
        return prev.filter((p) => p.id !== point.id);
      } else {
        return [...prev, point];
      }
    });
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedPoints([]);
  }, []);

  const selectByType = useCallback(
    (type) => {
      if (!data || !data.data) return;

      const pointsOfType = data.data.filter((point) => point.type === type);
      setSelectedPoints(pointsOfType);
    },
    [data]
  );

  const selectBySearch = useCallback(
    (searchTerm) => {
      if (!data || !data.data) return;

      const matchingPoints = data.data.filter(
        (point) =>
          point.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          point.label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          point.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setSelectedPoints(matchingPoints);
    },
    [data]
  );

  return {
    loading,
    error,
    data,
    selectedPoints,
    getVectors,
    getVectors2D,
    getVectors3D,
    selectPoint,
    clearSelection,
    selectByType,
    selectBySearch,
    reset,
  };
};

export default useVectors;
