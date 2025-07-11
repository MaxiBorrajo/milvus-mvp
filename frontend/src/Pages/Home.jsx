import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="home-container">
      <h1 className="metal-mania">
        𐕣 <span>MILVUS</span> 𐕣
      </h1>
      <p className="great-primer-sc">¡Bienvenidos al otro lado!</p>

      <div className="games-grid">
        <Link to="/primer-juego" className="game-card">
          <div className="game-icon">🗪</div>
          <h3 className="great-primer-sc">Primer Ritual</h3>
          <p className="libertinus-font">
            Haz una pregunta y encuentra a la persona perfecta para la tarea
          </p>
          <div className="game-difficulty libertinus-font">Fácil</div>
        </Link>

        <Link to="/segundo-juego" className="game-card">
          <div className="game-icon">🕮</div>
          <h3 className="great-primer-sc">Segundo Ritual</h3>
          <p className="libertinus-font">Arma tu legión</p>
          <div className="game-difficulty libertinus-font">Medio</div>
        </Link>

        <Link to="/tercer-juego" className="game-card">
          <div className="game-icon">🕈</div>
          <h3 className="great-primer-sc">Tercer Ritual</h3>
          <p className="libertinus-font">Elige tu destino</p>
          <div className="game-difficulty libertinus-font">Difícil</div>
        </Link>
      </div>
    </div>
  );
}
