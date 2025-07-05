import { useCallback } from "react";
import useApi from "./useApi";

const useTestData = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const createTestData = useCallback(
    async (testData) => {
      try {
        const result = await makeRequest(
          "http://localhost:8000/insert-person",
          {
            method: "POST",
            body: JSON.stringify(testData),
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

  const getDefaultTestData = () => {
    return {
      items: [
        {
          description:
            "Experto en organización de eventos y planificación de fiestas",
          name: "Juan Perez",
        },
        {
          description:
            "Especialista en resolución de problemas técnicos y debugging",
          name: "María García",
        },
        {
          description: "Consultor en estrategias de marketing digital",
          name: "Carlos López",
        },
        {
          description: "Diseñadora gráfica con experiencia en branding",
          name: "Ana Rodríguez ",
        },
        {
          description: "Ingeniero de software especializado en desarrollo web",
          name: "Luis Torres",
        },
      ],
    };
  };

  return {
    loading,
    error,
    data,
    createTestData,
    getDefaultTestData,
    reset,
  };
};

export default useTestData;
