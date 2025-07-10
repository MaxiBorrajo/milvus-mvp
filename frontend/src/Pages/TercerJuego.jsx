import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Header from "../Components/Header";
import useMultimodalSearch from "../hooks/useMultimodalSearch";

const TercerJuego = () => {
  const [currentStory, setCurrentStory] = useState("");
  const [storyHistory, setStoryHistory] = useState([]);
  const [currentStage, setCurrentStage] = useState(0);
  const [userQuery, setUserQuery] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);
  const [gameCompleted, setGameCompleted] = useState(false);

  const { loading, error, searchByText, getSearchResults, reset } =
    useMultimodalSearch();

  // Historia base inicial
  const baseStory =
    "En una noche sin luna, un grupo de amigos descubrió un portal misterioso en el sótano de una antigua biblioteca. El portal emitía una luz tenue y pulsante, como si estuviera vivo. Nadie sabía qué había del otro lado, pero todos sentían una extraña atracción hacia él.";

  useEffect(() => {
    if (!currentStory) {
      setCurrentStory(baseStory);
      setStoryHistory([{ text: baseStory, stage: 0 }]);
    }
  }, []);

  const handleQuery = async () => {
    if (!userQuery.trim()) return;

    try {
      await searchByText(userQuery, 3);
      setSelectedOption(null);
    } catch (err) {
      console.error("Error en la búsqueda:", err);
    }
  };

  const handleOptionSelect = (option) => {
    setSelectedOption(option);

    // Agregar la opción seleccionada a la historia
    const newStoryEntry = {
      text: option.content,
      stage: currentStage + 1,
      type: option.type,
      url: option.url,
      score: option.score,
    };

    setStoryHistory((prev) => [...prev, newStoryEntry]);
    setCurrentStory((prev) => prev + " " + option.content);
    setCurrentStage((prev) => prev + 1);

    // Limpiar la búsqueda actual
    reset();
    setUserQuery("");

    // Verificar si el juego está completo (4 etapas)
    if (currentStage >= 3) {
      setGameCompleted(true);
    }
  };

  const restartGame = () => {
    setCurrentStory("");
    setStoryHistory([]);
    setCurrentStage(0);
    setUserQuery("");
    setSelectedOption(null);
    setGameCompleted(false);
    reset();
  };

  const searchResults = getSearchResults();

  return (
    <div className="game-container">
      <Header title="Tercer Ritual" />

      <div className="game-content">
        <h1>📖 Historia Interactiva</h1>
        <p>Continúa la historia con tus propias preguntas</p>

        <div className="story-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${((currentStage + 1) / 4) * 100}%` }}
            ></div>
          </div>
          <p>Etapa {currentStage + 1} de 4</p>
        </div>

        <div className="story-section">
          <h3>📚 Historia Actual:</h3>
          <div className="story-text">
            {storyHistory.map((entry, index) => (
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
            ))}
          </div>
        </div>

        {!gameCompleted && (
          <div className="query-section">
            <h3>🤔 ¿Qué quieres saber?</h3>
            <div className="input-group">
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
                <div className="options-grid">
                  {searchResults.map((option, index) => (
                    <div
                      key={index}
                      className={`option-card ${
                        selectedOption === option ? "selected" : ""
                      }`}
                      onClick={() => handleOptionSelect(option)}
                    >
                      {option.type === "image" && option.url && (
                        <img
                          src={option.url}
                          alt="Option"
                          className="option-image"
                        />
                      )}
                      <div className="option-content">
                        <p>{option.content}</p>
                        <div className="option-meta">
                          <span className="option-type">{option.type}</span>
                          <span className="option-score">
                            {Math.round(option.score * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {gameCompleted && (
          <div className="game-completed">
            <h2>🎉 ¡Historia Completada!</h2>
            <p>Has completado las 4 etapas de la historia interactiva.</p>
            <button className="restart-btn" onClick={restartGame}>
              🔄 Crear Nueva Historia
            </button>
          </div>
        )}

        <Link to="/" className="back-btn">
          ← Volver al calabozo
        </Link>
      </div>
    </div>
  );
};

export default TercerJuego;
