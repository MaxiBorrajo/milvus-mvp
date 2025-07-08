import React, { useState } from "react";
import { Link } from "react-router-dom";
import Header from "../Components/Header";

const TercerJuego = () => {
  const [sequence, setSequence] = useState([]);
  const [playerSequence, setPlayerSequence] = useState([]);
  const [level, setLevel] = useState(1);
  const [score, setScore] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isShowingSequence, setIsShowingSequence] = useState(false);
  const [gameOver, setGameOver] = useState(false);

  const colors = [
    { id: 1, name: "red", color: "#ef4444" },
    { id: 2, name: "blue", color: "#3b82f6" },
    { id: 3, name: "green", color: "#10b981" },
    { id: 4, name: "yellow", color: "#f59e0b" },
  ];

  const startGame = () => {
    setSequence([]);
    setPlayerSequence([]);
    setLevel(1);
    setScore(0);
    setGameOver(false);
    setIsPlaying(true);
    generateSequence();
  };

  const generateSequence = () => {
    const newSequence = [];
    for (let i = 0; i < level; i++) {
      newSequence.push(Math.floor(Math.random() * 4) + 1);
    }
    setSequence(newSequence);
    showSequence(newSequence);
  };

  const showSequence = (seq) => {
    setIsShowingSequence(true);
    let index = 0;

    const interval = setInterval(() => {
      if (index >= seq.length) {
        clearInterval(interval);
        setIsShowingSequence(false);
        setPlayerSequence([]);
        return;
      }

      // Highlight the color briefly
      const colorElement = document.getElementById(`color-${seq[index]}`);
      if (colorElement) {
        colorElement.style.transform = "scale(0.9)";
        colorElement.style.filter = "brightness(1.3)";

        setTimeout(() => {
          colorElement.style.transform = "scale(1)";
          colorElement.style.filter = "brightness(1)";
        }, 500);
      }

      index++;
    }, 800);
  };

  const handleColorClick = (colorId) => {
    if (isShowingSequence || !isPlaying) return;

    const newPlayerSequence = [...playerSequence, colorId];
    setPlayerSequence(newPlayerSequence);

    // Check if the sequence is correct
    const isCorrect = newPlayerSequence.every(
      (id, index) => id === sequence[index]
    );

    if (!isCorrect) {
      // Game over
      setGameOver(true);
      setIsPlaying(false);
      return;
    }

    if (newPlayerSequence.length === sequence.length) {
      // Level completed
      setScore((prev) => prev + level * 10);
      setLevel((prev) => prev + 1);
      setPlayerSequence([]);

      setTimeout(() => {
        generateSequence();
      }, 1000);
    }
  };

  // Función helper para obtener color por ID (no utilizada actualmente)
  // const getColorById = (id) => {
  //   return colors.find((color) => color.id === id);
  // };

  return (
    <div className="game-container">
      <Header title="Tercer Ritual" />

      <div className="game-content">
        <h1>🕈 Tercer Ritual</h1>
        <p>Elige tu destino</p>

        <div className="game-stats">
          <div className="stat">
            <span className="stat-label">Nivel:</span>
            <span className="stat-value">{level}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Puntuación:</span>
            <span className="stat-value">{score}</span>
          </div>
        </div>

        {!isPlaying && !gameOver && (
          <button className="game-start-btn" onClick={startGame}>
            Comenzar Juego
          </button>
        )}

        {gameOver && (
          <div className="game-over">
            <h2>¡Juego Terminado!</h2>
            <p>Puntuación final: {score}</p>
            <p>Nivel alcanzado: {level}</p>
            <button className="game-start-btn" onClick={startGame}>
              Jugar de nuevo
            </button>
          </div>
        )}

        {isPlaying && (
          <div className="color-game">
            <div className="colors-grid">
              {colors.map((color) => (
                <div
                  key={color.id}
                  id={`color-${color.id}`}
                  className="color-button"
                  style={{ backgroundColor: color.color }}
                  onClick={() => handleColorClick(color.id)}
                >
                  <span className="color-name">{color.name}</span>
                </div>
              ))}
            </div>

            <div className="game-status">
              {isShowingSequence && (
                <p className="status-message">Memoriza la secuencia...</p>
              )}
              {!isShowingSequence && isPlaying && (
                <p className="status-message">Repite la secuencia</p>
              )}
            </div>
          </div>
        )}

        <div className="game-instructions">
          <h3>Instrucciones:</h3>
          <ul>
            <li>Observa la secuencia de colores que se ilumina</li>
            <li>Repite la secuencia haciendo clic en los colores</li>
            <li>La secuencia se hace más larga en cada nivel</li>
            <li>¡No te equivoques o perderás!</li>
          </ul>
        </div>

        <Link to="/" className="back-btn">
          ← Volver al Menú Principal
        </Link>
      </div>
    </div>
  );
};

export default TercerJuego;
