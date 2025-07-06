import React, { useState } from "react";
import { Link } from "react-router-dom";
import Header from "../Components/Header";
import usePersonSearch from "../hooks/usePersonSearch";

export default function PrimerJuego() {
  const [query, setQuery] = useState("");
  const { loading, error, searchPerson, getPersonName } = usePersonSearch();

  const handleSubmit = async () => {
    if (!query.trim()) {
      return;
    }

    try {
      await searchPerson(query);
    } catch (err) {
      // El error ya está manejado en el hook
      console.error("Error en handleSubmit:", err);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  const handleCreateTestData = () => {
    // TODO: Implementar creación de datos de prueba
    console.log("Creando datos de prueba...");
    alert("Función de crear datos de prueba - Implementar según necesidades");
  };

  return (
    <div className="game-container">
      <Header title="Primer Ritual" />

      <div className="game-content">
        <h1>🗪 ¿Quién ha sido señalado por las sombras?</h1>
        <p>
          Susurra tu duda al vacío... y alguien, en algún rincón olvidado,
          sentirá el llamado.
        </p>

        <div className="game-layout">
          <div className="left-section">
            <div className="search-section">
              <div className="input-group">
                <label htmlFor="question">
                  ¿A quién ha elegido el abismo entre las estrellas?
                </label>
                <input
                  id="question"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ej: usar de sacrificio, resolver problemas técnicos..."
                  className="search-input"
                  disabled={loading}
                />

                <button
                  onClick={handleSubmit}
                  className="search-btn"
                  disabled={loading || !query.trim()}
                >
                  {loading ? "🔍 Consultando..." : "🔍 Consultar"}
                </button>
              </div>

              {error && (
                <div className="error-message">
                  <span>⚠️ {error}</span>
                </div>
              )}

              <div className="test-data-section">
                <h4>🌌 Complementa el abismo</h4>
                <button
                  onClick={handleCreateTestData}
                  className="test-data-btn"
                >
                  💀 Alimenta al abismo
                </button>
              </div>
            </div>
          </div>

          <div className="right-section">
            <div className="result-section">
              {loading && (
                <div className="loading">
                  <div className="spinner"></div>
                  <p>Buscando respuestas...</p>
                </div>
              )}

              {getPersonName() && !loading && (
                <div className="result-card">
                  <h3>🕀 ¡Encontramos al acólito perfecto!</h3>
                  <div className="person-result">
                    <span className="person-name">{getPersonName()}</span>
                  </div>
                  <p className="result-description">
                    Esta persona es ideal para tu proposito. ¡Confía
                    completamente en su experiencia!
                  </p>
                </div>
              )}

              {!getPersonName() && !loading && !error && (
                <div className="placeholder">
                  <h3>🕯 ¿Cómo funciona?</h3>
                  <ul>
                    <li>Escribe una pregunta sobre qué necesitas</li>
                    <li>Envia tu solicitud al abismo</li>
                    <li>
                      Alguien o algo que pertenezca a la oscuridad te dara la
                      respuesta
                    </li>
                    <li>¡Confía ciegamente en la recomendación!</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>

        <Link to="/" className="back-btn">
          ← Volver al calabozo
        </Link>
      </div>
    </div>
  );
}
