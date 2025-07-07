import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="home-container">
      <h1>
        📿 <i>Milvus</i>
      </h1>
      <p>¡Bienvenidos al otro lado!</p>

      <div className="games-grid">
        <Link to="/primer-juego" className="game-card">
          <div className="game-icon">🗪</div>
          <h3>Primer Ritual</h3>
          <p>
            Haz una pregunta y encuentra a la persona perfecta para la tarea
          </p>
          <div className="game-difficulty">Fácil</div>
        </Link>

        <Link to="/segundo-juego" className="game-card">
          <div className="game-icon">🕮</div>
          <h3>Segundo Ritual</h3>
          <p>Encontrá tu angel o demonio gemelo</p>
          <div className="game-difficulty">Medio</div>
        </Link>

        <Link to="/tercer-juego" className="game-card">
          <div className="game-icon">🕈</div>
          <h3>Tercer Ritual</h3>
          <p>Elige tu destino</p>
          <div className="game-difficulty">Difícil</div>
        </Link>
      </div>
    </div>
  );
}
