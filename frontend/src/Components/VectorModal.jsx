import React, { useState, useEffect } from "react";
import SimpleVectorChart from "./SimpleVectorChart";
import useSimpleVectors from "../hooks/useSimpleVectors";

const VectorModal = ({ isOpen, onClose, getPersonResults }) => {
  const { loading, error, data, getPersonVectors } = useSimpleVectors();
  // eslint-disable-next-line
  const [hasLoaded, setHasLoaded] = useState(false);
  const [currentResults, setCurrentResults] = useState([]);

  useEffect(() => {
    if (isOpen) {
      loadVectors();
      // Ejecutar la función para obtener los resultados actuales
      const results = getPersonResults();
      const resultNames = results.map((result) => result.name).filter(Boolean);
      setCurrentResults(resultNames);
      setHasLoaded(true);
    }
    // eslint-disable-next-line
  }, [isOpen, getPersonResults]);

  const loadVectors = async () => {
    try {
      await getPersonVectors();
      setHasLoaded(true);
    } catch (err) {
      console.error("Error loading vectors:", err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content vector-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>📊 Visualización de Acólitos</h3>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Cargando visualización...</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              <span>⚠️ Error: {error}</span>
            </div>
          )}

          {!loading && !error && data && (
            <div className="vector-content">
              <div className="vector-info">
                <p>
                  <span className="info-label">🟢 Verde:</span> Resultados de la
                  búsqueda actual ({currentResults.length})
                </p>
                <p>
                  <span className="info-label">⚫ Gris:</span> Otras personas
                </p>
                <p className="info-tip">
                  💡 Pasa el mouse sobre los puntos para ver información
                </p>
              </div>

              <SimpleVectorChart
                key={`chart-${currentResults.join("-")}`}
                data={data}
                currentResults={currentResults}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VectorModal;
