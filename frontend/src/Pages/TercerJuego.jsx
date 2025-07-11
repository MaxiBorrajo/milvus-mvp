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
  const [draggedIndex, setDraggedIndex] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOverIndex, setDragOverIndex] = useState(null);
  const [showReorderInfo, setShowReorderInfo] = useState(false);
  const [selectedStoryEntries, setSelectedStoryEntries] = useState([]);
  // const [uploading, setUploading] = useState(false);
  // const [uploadResult, setUploadResult] = useState(null);

  const { loading, error, searchByText, getSearchResults, reset } =
    useMultimodalSearch();

  // Historia base inicial
  const baseStory = (
    <>
      Tras ser absorbidos por la grieta, quedamos condenados a un espacio de
      consultas infinitas: el **Limbo Vectorial**. Aquí nada se resuelve, todo
      se enreda. Cada pregunta desata nuevos fragmentos dispersos de nuestro
      propio relato roto.
    </>
  );

  // Mostrar información de reordenamiento cuando hay más de una historia
  useEffect(() => {
    if (storyHistory.length > 1 && !showReorderInfo) {
      setShowReorderInfo(true);
      // Ocultar después de 5 segundos
      setTimeout(() => setShowReorderInfo(false), 5000);
    }
  }, [storyHistory.length, showReorderInfo]);

  const handleQuery = async () => {
    if (!userQuery.trim()) return;

    try {
      await searchByText(userQuery, 3);
      setSelectedOption(null);
    } catch (err) {
      console.error("Error en la búsqueda:", err);
    }
  };

  const handleOptionSelect = async (option) => {
    setSelectedOption(option);
    // Eliminar en backend si tiene id o filename
    console.log(option);
    if (option.id) {
      try {
        await deleteFragmentById(
          option.id,
          option.type === "image" ? "image" : "text"
        );
      } catch (err) {
        alert("No se pudo eliminar el fragmento en el backend por id");
      }
    }

    setRemovedOptions((prev) => [...prev, option]);
    // Agregar la opción seleccionada a la historia
    const newStoryEntry = {
      text: option.content,
      type: option.type,
      url: option.url,
      score: option.score,
      isSelected: true, // Marcar como seleccionado
      originalOption: option, // Guardar referencia a la opción original
    };
    setStoryHistory((prev) => [...prev, newStoryEntry]);
    setSelectedStoryEntries((prev) => [...prev, newStoryEntry]);
    setCurrentStory((prev) => prev + " " + option.content);
    reset();
    setUserQuery("");
  };

  const handleRemoveOption = (option) => {
    setRemovedOptions((prev) => [...prev, option]);
    // Si el fragmento marcado es el seleccionado, deseleccionarlo
    if (selectedOption === option) setSelectedOption(null);
  };

  // Funciones para reordenamiento
  const handleDragStart = (e, index) => {
    setDraggedIndex(index);
    setIsDragging(true);
    setDragOverIndex(null);
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/html", e.target.outerHTML);

    // Agregar clase al body para estilos globales
    document.body.classList.add("dragging-active");
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    setDragOverIndex(index);
  };

  const handleDragLeave = () => {
    setDragOverIndex(null);
  };

  const handleDrop = (e, dropIndex) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDraggedIndex(null);
      setIsDragging(false);
      setDragOverIndex(null);
      document.body.classList.remove("dragging-active");
      return;
    }

    setStoryHistory((prev) => {
      const newHistory = [...prev];
      const draggedItem = newHistory[draggedIndex];
      newHistory.splice(draggedIndex, 1);
      newHistory.splice(dropIndex, 0, draggedItem);
      return newHistory;
    });

    setDraggedIndex(null);
    setIsDragging(false);
    setDragOverIndex(null);
    document.body.classList.remove("dragging-active");
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
    setIsDragging(false);
    setDragOverIndex(null);
    document.body.classList.remove("dragging-active");
  };

  const restartGame = () => {
    setCurrentStory("");
    setStoryHistory([]);
    setUserQuery("");
    setSelectedOption(null);
    setRemovedOptions([]);
    setSelectedStoryEntries([]);
    reset();
  };

  // Función para resetear el orden de las historias
  const resetStoryOrder = () => {
    if (storyHistory.length <= 1) return; // Solo la historia base

    // Mantener la historia base y reordenar el resto cronológicamente
    const baseEntry = storyHistory[0];
    const otherEntries = storyHistory.slice(1);

    // Ordenar por score (relevancia) de mayor a menor
    const sortedEntries = otherEntries.sort((a, b) => {
      const scoreA = a.score || 0;
      const scoreB = b.score || 0;
      return scoreB - scoreA;
    });

    setStoryHistory([baseEntry, ...sortedEntries]);
  };

  const searchResults = getSearchResults();

  return (
    <div className="game-container">
      <Header title="Tercer Ritual" />

      <div className="game-content metal-mania">
        <h1>⛤ Historia Interactiva ⛤</h1>
        <p>En el limbo sin fin tan solo resta hacer preguntas</p>
        {baseStory}
        {/* Botón para cargar items.json a la BDD */}
        <div style={{ margin: "16px 0", textAlign: "right" }}>
          <div className="story-section great-primer-sc">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "10px",
              }}
            >
              <h3>
                ☠ Historia Actual:{" "}
                <small style={{ fontSize: "0.8em", color: "#ffd700" }}>
                  (Arrastra los seleccionados)
                </small>
              </h3>
              {selectedStoryEntries.length > 1 && (
                <button
                  onClick={resetStoryOrder}
                  style={{
                    background: "rgba(255, 215, 0, 0.1)",
                    border: "1px solid #ffd700",
                    color: "#ffd700",
                    padding: "4px 8px",
                    borderRadius: "4px",
                    fontSize: "0.8em",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = "rgba(255, 215, 0, 0.2)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = "rgba(255, 215, 0, 0.1)";
                  }}
                >
                  🔄 Resetear orden
                </button>
              )}
            </div>

            {/* Información de reordenamiento */}

            <div className={`story-text ${isDragging ? "drag-active" : ""}`}>
              {storyHistory.length === 0 ? (
                <p style={{ color: "#bbb", fontStyle: "italic" }}>
                  Aquí aparecerán fragmentos de la historia a medida que
                  avances...
                </p>
              ) : (
                storyHistory.map((entry, index) => (
                  <div
                    key={index}
                    className={`story-entry ${
                      isDragging && draggedIndex === index ? "dragging" : ""
                    } ${dragOverIndex === index ? "drag-over" : ""}`}
                    draggable={entry.isSelected} // Solo permitir arrastrar los seleccionados
                    onDragStart={(e) => handleDragStart(e, index)}
                    onDragOver={(e) => handleDragOver(e, index)}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, index)}
                    onDragEnd={handleDragEnd}
                    style={{
                      cursor: entry.isSelected ? "grab" : "default",
                      opacity: isDragging && draggedIndex === index ? 0.5 : 1,
                      transform:
                        isDragging && draggedIndex === index
                          ? "rotate(5deg)"
                          : "none",
                      transition: "all 0.2s ease",
                      border: entry.isSelected
                        ? "2px dashed transparent"
                        : "none",
                      borderRadius: "8px",
                      padding: "8px",
                      margin: "8px 0",
                      backgroundColor: entry.isSelected
                        ? "rgba(255, 215, 0, 0.05)"
                        : "transparent",
                      position: "relative",
                    }}
                    onMouseEnter={(e) => {
                      if (entry.isSelected && !isDragging) {
                        e.target.style.border = "2px dashed #ffd700";
                        e.target.style.backgroundColor =
                          "rgba(255, 215, 0, 0.1)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (entry.isSelected && !isDragging) {
                        e.target.style.border = "2px dashed transparent";
                        e.target.style.backgroundColor =
                          "rgba(255, 215, 0, 0.05)";
                      }
                    }}
                  >
                    {entry.isSelected && (
                      <div
                        style={{
                          position: "absolute",
                          top: "5px",
                          right: "10px",
                          fontSize: "12px",
                          color: "#ffd700",
                          opacity: 0.7,
                          pointerEvents: "none",
                        }}
                      >
                        ⋮⋮
                      </div>
                    )}
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
                    {entry.isSelected && (
                      <small
                        style={{
                          position: "absolute",
                          top: "5px",
                          left: "10px",
                          fontSize: "10px",
                          color: "#ffd700",
                          opacity: 0.6,
                          background: "rgba(0,0,0,0.5)",
                          padding: "2px 4px",
                          borderRadius: "3px",
                        }}
                      >
                        #{index}
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

          {/* <button className="restart-btn" onClick={restartGame}>
          🔄 Crear Nueva Historia
        </button> */}

          <Link to="/" className="back-btn">
            ← Volver al calabozo
          </Link>
        </div>
      </div>
    </div>
  );
};
export default TercerJuego;
