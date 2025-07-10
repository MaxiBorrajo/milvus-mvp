import { useState, useCallback } from "react";

const useMultimodalSearch = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  // Datos mock completos para la historia interactiva
  const mockData = {
    "¿Qué pasó después?": [
      {
        content:
          "El portal comenzó a brillar con una luz intensa, revelando un mundo completamente diferente al otro lado. Los colores eran imposibles de describir, como si la realidad misma se hubiera doblado.",
        type: "text",
        filename: null,
        url: null,
        score: 0.95,
      },
      {
        content:
          "Una figura sombría emergió del portal, sus ojos brillaban como estrellas en la oscuridad. Vestía ropas que parecían hechas de sombra y tiempo.",
        type: "text",
        filename: null,
        url: null,
        score: 0.87,
      },
      {
        content:
          "El suelo tembló mientras el portal se expandía, absorbiendo todo a su alrededor. Los libros de la biblioteca flotaban en el aire como hojas en el viento.",
        type: "text",
        filename: null,
        url: null,
        score: 0.82,
      },
    ],
    "¿Quién era esa figura?": [
      {
        content:
          "Era el guardián del portal, una entidad ancestral que protegía los secretos del multiverso. Había estado esperando miles de años para que alguien encontrara el portal.",
        type: "text",
        filename: null,
        url: null,
        score: 0.93,
      },
      {
        content:
          "La figura resultó ser una versión alternativa de uno mismo, venida del futuro. Tenía la misma voz pero con una sabiduría que solo los años podían dar.",
        type: "text",
        filename: null,
        url: null,
        score: 0.89,
      },
      {
        content:
          "Era el demonio que había estado observando todo el tiempo, finalmente revelando su verdadera forma. Pero en lugar de ser malvado, parecía... triste.",
        type: "text",
        filename: null,
        url: null,
        score: 0.85,
      },
    ],
    "¿Qué secretos guardaba?": [
      {
        content:
          "El portal contenía el conocimiento de todas las realidades posibles, cada una más extraña que la anterior. Era como una biblioteca infinita de universos paralelos.",
        type: "text",
        filename: null,
        url: null,
        score: 0.91,
      },
      {
        content:
          "Era una biblioteca infinita de historias, donde cada libro contaba una versión diferente de la realidad. Algunos eran felices, otros trágicos, pero todos eran verdaderos.",
        type: "text",
        filename: null,
        url: null,
        score: 0.88,
      },
      {
        content:
          "Los secretos incluían la fórmula para viajar entre dimensiones y el poder de cambiar la realidad misma. Pero cada cambio tenía un precio terrible.",
        type: "text",
        filename: null,
        url: null,
        score: 0.84,
      },
    ],
    "¿Cómo terminó todo?": [
      {
        content:
          "El portal se cerró, pero la experiencia cambió para siempre la percepción de la realidad de todos los presentes. Ya no podían ver el mundo de la misma manera.",
        type: "text",
        filename: null,
        url: null,
        score: 0.94,
      },
      {
        content:
          "Todos fueron absorbidos por el portal, iniciando una nueva aventura en un mundo completamente diferente. Pero prometieron regresar algún día.",
        type: "text",
        filename: null,
        url: null,
        score: 0.9,
      },
      {
        content:
          "El demonio se desvaneció, pero dejó una puerta abierta para futuras aventuras interdimensionales. Y una nota que decía: 'La verdadera magia está en las preguntas, no en las respuestas'.",
        type: "text",
        filename: null,
        url: null,
        score: 0.86,
      },
    ],
    "¿Qué vieron del otro lado?": [
      {
        content:
          "Vieron un mundo donde la gravedad funcionaba al revés, donde las ciudades flotaban en el cielo y los ríos corrían hacia arriba. Era hermoso y aterrador al mismo tiempo.",
        type: "text",
        filename: null,
        url: null,
        score: 0.92,
      },
      {
        content:
          "Era un lugar donde el tiempo no existía, donde el pasado, presente y futuro se mezclaban en una danza eterna. Los habitantes vivían en todos los momentos a la vez.",
        type: "text",
        filename: null,
        url: null,
        score: 0.88,
      },
      {
        content:
          "Vieron versiones de sí mismos de otras realidades, algunos felices, otros tristes, todos viviendo vidas completamente diferentes pero igualmente válidas.",
        type: "text",
        filename: null,
        url: null,
        score: 0.85,
      },
    ],
    "¿Qué pasó con los amigos?": [
      {
        content:
          "Cada uno eligió un camino diferente en el multiverso. Algunos se quedaron a explorar, otros regresaron para contar la historia, y algunos se perdieron para siempre.",
        type: "text",
        filename: null,
        url: null,
        score: 0.93,
      },
      {
        content:
          "Se mantuvieron unidos a través de un vínculo mágico que les permitía comunicarse a través de las dimensiones. Su amistad se había vuelto más fuerte que nunca.",
        type: "text",
        filename: null,
        url: null,
        score: 0.89,
      },
      {
        content:
          "Algunos se convirtieron en guardianes del portal, protegiendo el secreto de otros que no estaban listos para conocer la verdad sobre la realidad.",
        type: "text",
        filename: null,
        url: null,
        score: 0.86,
      },
    ],
  };

  const searchByText = useCallback(async (query, topK = 3) => {
    if (!query?.trim()) {
      throw new Error("La consulta no puede estar vacía");
    }

    // Simular delay de carga
    setLoading(true);
    setError(null);

    try {
      // Simular delay de red
      await new Promise((resolve) => setTimeout(resolve, 800));

      // Buscar en datos mock
      const mockResults =
        mockData[query.trim()] || mockData["¿Qué pasó después?"];
      const results = mockResults.slice(0, topK);

      setData(results);
      return results;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getSearchResults = () => {
    if (!data) return [];
    return data || [];
  };

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    loading,
    error,
    data,
    searchByText,
    getSearchResults,
    reset,
  };
};

export default useMultimodalSearch;
