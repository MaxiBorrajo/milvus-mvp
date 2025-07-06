import React, { useState } from "react";
import { Link } from "react-router-dom";
import Header from "../Components/Header";
import usePersonSearch from "../hooks/usePersonSearch";
import useTestData from "../hooks/useTestData";
import VectorModal from "../Components/VectorModal";

// Componente Modal
const PersonModal = ({ person, isOpen, onClose }) => {
  if (!isOpen || !person) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>👤 {person.name}</h3>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          <div className="person-info">
            <h4>📝 Descripción:</h4>
            <p>{person.description}</p>
            {person.similarity !== undefined && (
              <div className="similarity-info">
                <h4>🎯 Coincidencia:</h4>
                <p>{Math.round(person.similarity * 100)}% de similitud</p>
                <small>(Mayor similitud = Mejor coincidencia)</small>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default function PrimerJuego() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(1);
  const [metricType, setMetricType] = useState("COSINE");
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isVectorModalOpen, setIsVectorModalOpen] = useState(false);
  const { loading, error, searchPerson, getPersonResults } = usePersonSearch();
  const {
    loading: testDataLoading,
    error: testDataError,
    createTestData,
    getDefaultTestData,
  } = useTestData();

  const handleSubmit = async () => {
    if (!query.trim()) {
      return;
    }

    try {
      await searchPerson(query, topK, metricType);
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

  const handleCreateTestData = async () => {
    try {
      const testData = getDefaultTestData();
      const result = await createTestData(testData);
      alert(
        `✅ Datos de prueba creados exitosamente!\nInsertados: ${result.inserted} elementos`
      );
    } catch (error) {
      console.error("Error creando datos de prueba:", error);
      alert(`❌ Error al crear datos de prueba: ${error.message}`);
    }
  };

  const handlePersonClick = (person) => {
    setSelectedPerson(person);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedPerson(null);
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

                <div className="top-k-selector">
                  <label htmlFor="topK">Cantidad de personas:</label>
                  <select
                    id="topK"
                    value={topK}
                    onChange={(e) => setTopK(parseInt(e.target.value))}
                    className="top-k-select"
                    disabled={loading}
                  >
                    <option value={1}>1 persona</option>
                    <option value={2}>2 personas</option>
                    <option value={3}>3 personas</option>
                    <option value={5}>5 personas</option>
                    <option value={10}>10 personas</option>
                  </select>
                </div>

                <div className="metric-selector">
                  <label htmlFor="metricType">Algoritmo de búsqueda:</label>
                  <select
                    id="metricType"
                    value={metricType}
                    onChange={(e) => setMetricType(e.target.value)}
                    className="metric-select"
                    disabled={loading}
                  >
                    <option value="COSINE">Coseno (Recomendado)</option>
                    <option value="L2">Distancia Euclidiana</option>
                    <option value="IP">Producto Interno</option>
                  </select>
                </div>

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

              {testDataError && (
                <div className="error-message">
                  <span>⚠️ Error en datos de prueba: {testDataError}</span>
                </div>
              )}

              <div className="test-data-section">
                <h4>🌌 Complementa el abismo</h4>
                <button
                  onClick={handleCreateTestData}
                  className="test-data-btn"
                  disabled={testDataLoading}
                >
                  {testDataLoading
                    ? "⏳ Alimentando..."
                    : "💀 Alimenta al abismo"}
                </button>
              </div>

              <div className="visualization-section">
                <h4>📊 Visualización</h4>
                <button
                  onClick={() => setIsVectorModalOpen(true)}
                  className="visualization-btn"
                >
                  🎯 Ver Gráfico de Personas
                </button>
                {getPersonResults().length > 0 && (
                  <p className="visualization-info">
                    Última búsqueda:{" "}
                    {getPersonResults()
                      .slice(0, 3)
                      .map((r) => r.name)
                      .join(", ")}
                    {getPersonResults().length > 3 &&
                      ` y ${getPersonResults().length - 3} más`}
                    <br />
                  </p>
                )}
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

              {getPersonResults().length > 0 && !loading && (
                <div className="result-card">
                  <h3>🎉 ¡Encontramos a la persona perfecta!</h3>
                  <div className="person-result">
                    <span className="person-name">{getPersonName()}</span>
                  </div>
                  <p className="result-description">
                    Esta persona es ideal para tu consulta. ¡Confía en su
                    experiencia!
                  </p>
                </div>
              )}

              {!getPersonResults().length && !loading && !error && (
                <div className="placeholder">
                  <h3>💡 ¿Cómo funciona?</h3>
                  <ul>
                    <li>Escribe una pregunta sobre qué necesitas</li>
                    <li>Haz clic en "Buscar" o presiona Enter</li>
                    <li>El sistema encontrará a la persona más indicada</li>
                    <li>¡Confía en la recomendación!</li>
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

      {/* Modal */}
      <PersonModal
        person={selectedPerson}
        isOpen={isModalOpen}
        onClose={closeModal}
      />

      {/* Modal de Vectores */}
      <VectorModal
        isOpen={isVectorModalOpen}
        onClose={() => setIsVectorModalOpen(false)}
        getPersonResults={getPersonResults}
      />
    </div>
  );
}
