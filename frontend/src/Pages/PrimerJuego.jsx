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
      <Header title="¿Quién es el indicado?" />

      <div className="game-content">
        <h1>🎯 ¿Quién es el indicado?</h1>
        <p>Haz una pregunta y encuentra a la persona perfecta para la tarea</p>

        <div className="game-layout">
          <div className="left-section">
            <div className="search-section">
              <div className="input-group">
                <label htmlFor="question">¿Quién es el mejor para?</label>
                <input
                  id="question"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ej: organizar una fiesta, resolver problemas técnicos..."
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
                  {loading ? "🔍 Buscando..." : "🔍 Buscar"}
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
                <h4>🧪 Datos de Prueba</h4>
                <button
                  onClick={handleCreateTestData}
                  className="test-data-btn"
                  disabled={testDataLoading}
                >
                  {testDataLoading
                    ? "⏳ Creando..."
                    : "📊 Crear Datos de Prueba"}
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
                  <p>Buscando a la persona indicada...</p>
                </div>
              )}

              {getPersonResults().length > 0 && !loading && (
                <div className="result-card">
                  <h3>🎉 ¡Encontramos a las personas indicadas!</h3>
                  <div className="persons-result">
                    {getPersonResults().map((result, index) => (
                      <div
                        key={index}
                        className="person-item clickable"
                        onClick={() => handlePersonClick(result)}
                        title="Haz clic para ver más detalles"
                      >
                        <span className="person-rank">#{index + 1}</span>
                        <span className="person-name">
                          {result.name || "Persona no especificada"}
                        </span>
                        {result.similarity !== undefined && (
                          <span className="person-score">
                            {Math.round(result.similarity * 100)}% similitud
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                  <p className="result-description">
                    Haz clic en cualquier persona para ver su descripción
                    completa. ¡Confía en su experiencia!
                  </p>
                </div>
              )}

              {!getPersonResults().length && !loading && !error && (
                <div className="placeholder">
                  <h3>🎯 ¿Quién es el indicado?</h3>

                  <div className="placeholder-examples">
                    <h4>💡 Ejemplos de preguntas:</h4>
                    <ul>
                      <li>"¿Quién puede organizar una fiesta?"</li>
                      <li>"¿Quién sabe resolver problemas técnicos?"</li>
                      <li>"¿Quién es bueno para el marketing?"</li>
                      <li>"¿Quién puede ayudarme con diseño?"</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <Link to="/" className="back-btn">
          ← Volver al Menú Principal
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
