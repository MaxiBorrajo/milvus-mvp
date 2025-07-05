import React, { useState } from "react";
import Header from "../Components/Header";

const SegundoJuego = () => {
  const [cards, setCards] = useState([]);
  const [flipped, setFlipped] = useState([]);
  const [matched, setMatched] = useState([]);
  const [moves, setMoves] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const emojis = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"];

  const initializeGame = () => {
    const gameCards = [...emojis, ...emojis]
      .sort(() => Math.random() - 0.5)
      .map((emoji, index) => ({
        id: index,
        emoji,
        isFlipped: false,
        isMatched: false,
      }));

    setCards(gameCards);
    setFlipped([]);
    setMatched([]);
    setMoves(0);
    setIsPlaying(true);
  };

  const handleCardClick = (cardId) => {
    if (
      !isPlaying ||
      flipped.length >= 2 ||
      flipped.includes(cardId) ||
      matched.includes(cardId)
    ) {
      return;
    }

    const newFlipped = [...flipped, cardId];
    setFlipped(newFlipped);

    if (newFlipped.length === 2) {
      setMoves((prev) => prev + 1);

      const [firstId, secondId] = newFlipped;
      const firstCard = cards.find((card) => card.id === firstId);
      const secondCard = cards.find((card) => card.id === secondId);

      if (firstCard.emoji === secondCard.emoji) {
        setMatched((prev) => [...prev, firstId, secondId]);
        setFlipped([]);

        // Check if game is won
        if (matched.length + 2 === cards.length) {
          setTimeout(() => {
            alert(
              `¡Felicidades! Completaste el juego en ${moves + 1} movimientos.`
            );
            setIsPlaying(false);
          }, 500);
        }
      } else {
        setTimeout(() => {
          setFlipped([]);
        }, 1000);
      }
    }
  };

  const isCardVisible = (cardId) => {
    return flipped.includes(cardId) || matched.includes(cardId);
  };

  return (
    <div className="game-container">
      <Header title="Segundo Juego" />

      <div className="game-content">
        <h1>🧠 Segundo Juego</h1>
        <p>¡Encuentra las parejas de emojis!</p>

        <div className="game-stats">
          <div className="stat">
            <span className="stat-label">Movimientos:</span>
            <span className="stat-value">{moves}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Parejas encontradas:</span>
            <span className="stat-value">{matched.length / 2}</span>
          </div>
        </div>

        {!isPlaying && cards.length === 0 && (
          <button className="game-start-btn" onClick={initializeGame}>
            Comenzar Juego
          </button>
        )}

        {cards.length > 0 && (
          <div className="memory-game">
            <div className="cards-grid">
              {cards.map((card) => (
                <div
                  key={card.id}
                  className={`memory-card ${
                    isCardVisible(card.id) ? "flipped" : ""
                  }`}
                  onClick={() => handleCardClick(card.id)}
                >
                  <div className="card-inner">
                    <div className="card-front">❓</div>
                    <div className="card-back">{card.emoji}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {cards.length > 0 && (
          <button className="game-start-btn" onClick={initializeGame}>
            Reiniciar Juego
          </button>
        )}

        <div className="game-instructions">
          <h3>Instrucciones:</h3>
          <ul>
            <li>Haz clic en las cartas para voltearlas</li>
            <li>Encuentra las parejas de emojis iguales</li>
            <li>Completa todas las parejas para ganar</li>
            <li>¡Intenta hacerlo con la menor cantidad de movimientos!</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SegundoJuego;
