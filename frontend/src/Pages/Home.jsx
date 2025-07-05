import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="home-container">
      <h1>🎮 Arcade de Juegos</h1>
      <p>¡Bienvenido a nuestra colección de juegos interactivos!</p>

      <div className="games-grid">
        <Link to="/primer-juego" className="game-card">
          <div className="game-icon">🎯</div>
          <h3>Primer Juego</h3>
          <p>¡Haz clic lo más rápido que puedas!</p>
          <div className="game-difficulty">Fácil</div>
        </Link>

        <Link to="/segundo-juego" className="game-card">
          <div className="game-icon">🧠</div>
          <h3>Segundo Juego</h3>
          <p>¡Encuentra las parejas de emojis!</p>
          <div className="game-difficulty">Medio</div>
        </Link>

        <Link to="/tercer-juego" className="game-card">
          <div className="game-icon">🎨</div>
          <h3>Tercer Juego</h3>
          <p>¡Repite la secuencia de colores!</p>
          <div className="game-difficulty">Difícil</div>
        </Link>
      </div>

      <div className="features">
        <h2>Características de los Juegos:</h2>
        <ul>
          <li>🎮 Juegos interactivos y divertidos</li>
          <li>📊 Sistema de puntuación</li>
          <li>🏆 Diferentes niveles de dificultad</li>
          <li>🔄 Reinicio automático</li>
          <li>📱 Diseño responsive</li>
          <li>⚡ Animaciones fluidas</li>
        </ul>
      </div>
    </div>
  );
}
