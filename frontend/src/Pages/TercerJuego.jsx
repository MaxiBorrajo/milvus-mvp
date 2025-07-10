import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Header from "../Components/Header";
import useMultimodalSearch, {
  deleteFragmentByFilename,
  deleteFragmentById,
} from "../hooks/useMultimodalSearch";

const TercerJuego = () => {
  const [currentStory, setCurrentStory] = useState("");
  const [storyHistory, setStoryHistory] = useState([]);
  const [userQuery, setUserQuery] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);
  const [fragmentType, setFragmentType] = useState("lore");
  const [removedOptions, setRemovedOptions] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const { loading, error, searchByText, getSearchResults, reset } =
    useMultimodalSearch();

  // Historia base inicial
  const baseStory = (
    <>
      RDJ se desvaneció en el portal, Tomi fue secuestrado por una fuerza
      desconocida y ahora el grupo está atrapado en el Limbo Vectorial.
      <br />
      Solo las preguntas pueden abrir el camino…
    </>
  );

  useEffect(() => {
    if (!currentStory) {
      setCurrentStory(baseStory);
      setStoryHistory([{ text: baseStory }]);
    }
  }, []);

  const handleQuery = async () => {
    if (!userQuery.trim()) return;

    try {
      await searchByText(userQuery, 3, fragmentType);
      setSelectedOption(null);
    } catch (err) {
      console.error("Error en la búsqueda:", err);
    }
  };

  const handleOptionSelect = async (option) => {
    setSelectedOption(option);
    // Eliminar en backend si tiene id o filename
    if (option.id) {
      try {
        await deleteFragmentById(
          option.id,
          option.type === "image" ? "image" : "text"
        );
      } catch (err) {
        alert(
          "No se pudo eliminar el fragmento en el backend por id: " +
            err.message
        );
      }
    } else if (option.filename) {
      try {
        await deleteFragmentByFilename(option.filename);
      } catch (err) {
        alert(
          "No se pudo eliminar el fragmento en el backend por filename: " +
            err.message
        );
      }
    }
    setRemovedOptions((prev) => [...prev, option]);
    // Agregar la opción seleccionada a la historia
    const newStoryEntry = {
      text: option.content,
      type: option.type,
      url: option.url,
      score: option.score,
    };
    setStoryHistory((prev) => [...prev, newStoryEntry]);
    setCurrentStory((prev) => prev + " " + option.content);
    reset();
    setUserQuery("");
  };

  const handleRemoveOption = (option) => {
    setRemovedOptions((prev) => [...prev, option]);
    // Si el fragmento marcado es el seleccionado, deseleccionarlo
    if (selectedOption === option) setSelectedOption(null);
  };

  const restartGame = () => {
    setCurrentStory("");
    setStoryHistory([]);
    setUserQuery("");
    setSelectedOption(null);
    setRemovedOptions([]);
    reset();
  };

  const searchResults = getSearchResults();

  return (
    <div className="game-container">
      <Header title="Tercer Ritual" />

      <div className="game-content">
        <h1>📖 Historia Interactiva</h1>
        {baseStory}
        {/* Botón para cargar items.json a la BDD */}
        <div style={{ margin: "16px 0", textAlign: "right" }}>
          <button
            onClick={async () => {
              setUploading(true);
              setUploadResult(null);
              try {
                const res = await fetch(
                  "http://localhost:8000/cargar-items-json",
                  { method: "POST" }
                );
                const data = await res.json();
                setUploadResult(
                  data.inserted
                    ? `Se insertaron ${data.inserted} fragmentos.`
                    : JSON.stringify(data)
                );
              } catch (err) {
                setUploadResult("Error: " + err.message);
              } finally {
                setUploading(false);
              }
            }}
            disabled={uploading}
            style={{
              background: "#222",
              color: "#ffd700",
              border: "1.5px solid #ffd700",
              borderRadius: 8,
              padding: "6px 18px",
              fontWeight: 600,
              fontSize: "1rem",
              cursor: uploading ? "not-allowed" : "pointer",
              marginBottom: 8,
            }}
          >
            {uploading
              ? "Cargando items.json..."
              : "Cargar items.json a la BDD"}
          </button>
          {uploadResult && (
            <div
              style={{
                color: uploadResult.startsWith("Error") ? "red" : "#ffd700",
                marginTop: 4,
              }}
            >
              {uploadResult}
            </div>
          )}
        </div>

        <div className="story-section">
          <h3>📚 Historia Actual:</h3>
          <div className="story-text">
            {storyHistory.length === 0 ? (
              <p style={{ color: "#bbb", fontStyle: "italic" }}>
                Aquí aparecerán los fragmentos de la historia a medida que
                avances...
              </p>
            ) : (
              storyHistory.map((entry, index) => (
                <div key={index} className="story-entry">
                  {entry.type === "image" && entry.url && (
                    <img
                      src={entry.url}
                      alt="Story"
                      className="story-image"
                      style={{ maxWidth: "200px", margin: "10px 0" }}
                    />
                  )}
                  <p>{entry.text}</p>
                  {entry.score && (
                    <small className="story-score">
                      Relevancia: {Math.round(entry.score * 100)}%
                    </small>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="query-section">
          <h3>🤔 ¿Qué quieres saber?</h3>
          <div className="input-group">
            <select
              value={fragmentType}
              onChange={(e) => setFragmentType(e.target.value)}
              className="fragment-type-selector"
              disabled={loading}
              style={{
                marginRight: 8,
                padding: "8px 12px",
                borderRadius: "6px",
                border: "1.5px solid #ffd700",
                background: "rgba(30, 10, 30, 0.85)",
                fontSize: "1rem",
                color: "#ffd700",
                outline: "none",
                boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
                transition: "border 0.2s",
                minWidth: 140,
                cursor: loading ? "not-allowed" : "pointer",
                height: 40,
                verticalAlign: "middle",
                fontWeight: 600,
                letterSpacing: "0.5px",
              }}
            >
              <option value="lore">Lore</option>
              <option value="alternativo">Final alternativo</option>
              <option value="personaje">Personaje</option>
            </select>
            <input
              type="text"
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
              placeholder="Ej: ¿Qué pasó después? ¿Quién era esa figura?"
              className="query-input"
              disabled={loading}
              onKeyPress={(e) => e.key === "Enter" && handleQuery()}
            />
            <button
              onClick={handleQuery}
              className="query-btn"
              disabled={loading || !userQuery.trim()}
            >
              {loading ? "🔍 Buscando..." : "🔍 Consultar"}
            </button>
          </div>

          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
            </div>
          )}

          {searchResults.length > 0 && (
            <div className="options-section">
              <h4>🎯 Opciones para continuar:</h4>
              <div className="options-grouped">
                {Object.entries(
                  searchResults
                    .filter(
                      (option) =>
                        !removedOptions.includes(option) ||
                        selectedOption === option
                    )
                    .reduce((acc, option) => {
                      const historia =
                        option.metadata && option.metadata.historia
                          ? option.metadata.historia
                          : "sin_historia";
                      if (!acc[historia]) acc[historia] = [];
                      acc[historia].push(option);
                      return acc;
                    }, {})
                ).map(([historia, options]) => (
                  <div key={historia} className="historia-group">
                    <div className="historia-title">Historia: {historia}</div>
                    <div className="options-grid">
                      {[...options]
                        .sort((a, b) =>
                          a === selectedOption
                            ? -1
                            : b === selectedOption
                            ? 1
                            : 0
                        )
                        .map((option, index) => (
                          <div
                            key={index}
                            className={`option-card ${
                              selectedOption === option ? "selected" : ""
                            }`}
                            onClick={() => handleOptionSelect(option)}
                            style={
                              selectedOption === option ? { order: -1 } : {}
                            }
                          >
                            {option.type === "image" && option.url && (
                              <img
                                src={option.url}
                                alt="Option"
                                className="option-image"
                              />
                            )}
                            {option.type === "audio" && option.url && (
                              <audio
                                controls
                                src={option.url}
                                style={{ width: "100%", margin: "10px 0" }}
                              >
                                Tu navegador no soporta audio.
                              </audio>
                            )}
                            <div className="option-content">
                              <p>{option.content}</p>
                              <div className="option-meta">
                                <span className="option-type">
                                  {option.type}
                                </span>
                                <span className="option-score">
                                  {Math.round(option.score * 100)}%
                                </span>
                                {option.metadata &&
                                  option.metadata.historia && (
                                    <span className="option-historia">
                                      {option.metadata.historia}
                                    </span>
                                  )}
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <button className="restart-btn" onClick={restartGame}>
          🔄 Crear Nueva Historia
        </button>

        <Link to="/" className="back-btn">
          ← Volver al calabozo
        </Link>
      </div>
    </div>
  );
};

export default TercerJuego;
