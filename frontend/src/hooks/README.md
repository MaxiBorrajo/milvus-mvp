# Custom Hooks para API

Este directorio contiene hooks personalizados para manejar las consultas a la base de datos y APIs.

## 🎯 useApi (Hook Base)

Hook general para manejar cualquier llamada a API con estados de loading, error y data.

### Uso:

```jsx
import useApi from "./hooks/useApi";

function MiComponente() {
  const { loading, error, data, makeRequest, reset } = useApi();

  const handleApiCall = async () => {
    try {
      const result = await makeRequest("http://localhost:8000/mi-endpoint", {
        method: "POST",
        body: JSON.stringify({ dato: "valor" }),
      });
      console.log("Resultado:", result);
    } catch (err) {
      // El error ya está manejado automáticamente
    }
  };

  return (
    <div>
      {loading && <p>Cargando...</p>}
      {error && <p>Error: {error}</p>}
      {data && <p>Datos: {JSON.stringify(data)}</p>}
      <button onClick={handleApiCall}>Llamar API</button>
      <button onClick={reset}>Limpiar</button>
    </div>
  );
}
```

### Propiedades retornadas:

- `loading`: Boolean - Indica si la petición está en curso
- `error`: String - Mensaje de error si algo falló
- `data`: Object - Datos de la respuesta
- `makeRequest(url, options)`: Function - Función para hacer la petición
- `reset()`: Function - Limpia todos los estados

## 🔍 usePersonSearch (Hook Específico)

Hook específico para buscar personas en el sistema.

### Uso:

```jsx
import usePersonSearch from "./hooks/usePersonSearch";

function BuscadorPersonas() {
  const { loading, error, searchPerson, getPersonName, reset } =
    usePersonSearch();

  const handleSearch = async (pregunta) => {
    try {
      await searchPerson(pregunta);
    } catch (err) {
      // Error manejado automáticamente
    }
  };

  return (
    <div>
      {loading && <p>Buscando persona...</p>}
      {error && <p>Error: {error}</p>}
      {getPersonName() && <p>Persona encontrada: {getPersonName()}</p>}
    </div>
  );
}
```

### Propiedades retornadas:

- `loading`: Boolean - Indica si la búsqueda está en curso
- `error`: String - Mensaje de error si algo falló
- `data`: Object - Datos completos de la respuesta
- `searchPerson(question)`: Function - Busca una persona por pregunta
- `getPersonName()`: Function - Obtiene el nombre de la persona encontrada
- `reset()`: Function - Limpia todos los estados

## 🎮 useGameScore (Hook para Puntuaciones)

Hook para manejar puntuaciones de juegos.

### Uso:

```jsx
import useGameScore from "./hooks/useGameScore";

function Juego() {
  const { loading, error, saveScore, getTopScores, reset } = useGameScore();

  const handleGameEnd = async (score) => {
    try {
      await saveScore("MiJuego", score, "Jugador1");
      console.log("Puntuación guardada");
    } catch (err) {
      console.error("Error al guardar:", err);
    }
  };

  const handleGetTopScores = async () => {
    try {
      await getTopScores("MiJuego", 5);
    } catch (err) {
      console.error("Error al obtener puntuaciones:", err);
    }
  };

  return (
    <div>
      {loading && <p>Guardando...</p>}
      {error && <p>Error: {error}</p>}
      <button onClick={() => handleGameEnd(100)}>Guardar Puntuación</button>
      <button onClick={handleGetTopScores}>Ver Top 5</button>
    </div>
  );
}
```

### Propiedades retornadas:

- `loading`: Boolean - Indica si la operación está en curso
- `error`: String - Mensaje de error si algo falló
- `data`: Object - Datos de la respuesta
- `saveScore(gameName, score, playerName)`: Function - Guarda una puntuación
- `getTopScores(gameName, limit)`: Function - Obtiene las mejores puntuaciones
- `getPlayerScores(playerName)`: Function - Obtiene puntuaciones de un jugador
- `reset()`: Function - Limpia todos los estados

## 🚀 Ventajas de usar estos hooks:

1. **Reutilización**: Un solo hook para múltiples componentes
2. **Consistencia**: Mismo manejo de estados en toda la app
3. **Limpieza**: Código más limpio y mantenible
4. **Separación de responsabilidades**: Lógica de API separada de la UI
5. **Testing**: Más fácil de testear
6. **Manejo de errores centralizado**: Todos los errores se manejan igual

## 📝 Crear nuevos hooks:

Para crear un nuevo hook específico:

```jsx
import { useCallback } from "react";
import useApi from "./useApi";

const useMiNuevoHook = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const miFuncion = useCallback(
    async (parametros) => {
      try {
        const result = await makeRequest("http://localhost:8000/mi-endpoint", {
          method: "POST",
          body: JSON.stringify(parametros),
        });
        return result;
      } catch (err) {
        throw err;
      }
    },
    [makeRequest]
  );

  return {
    loading,
    error,
    data,
    miFuncion,
    reset,
  };
};

export default useMiNuevoHook;
```
