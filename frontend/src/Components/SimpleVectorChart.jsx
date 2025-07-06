import React, { useEffect, useRef } from "react";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const SimpleVectorChart = ({ data, currentResults = [] }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!data || !data.data || data.data.length === 0) {
      return;
    }

    const ctx = chartRef.current.getContext("2d");

    // Destruir chart anterior si existe
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Preparar datos
    const chartData = data.data
      .filter((item) => item.type === "person")
      .map((item) => ({
        x: item.vector[0],
        y: item.vector[1],
        name: item.name,
        description: item.description,
        isCurrentResult: currentResults.includes(item.name),
      }));

    // Separar por tipo (resultados actuales vs otros)
    const currentResultPoints = chartData.filter(
      (point) => point.isCurrentResult
    );
    const otherPoints = chartData.filter((point) => !point.isCurrentResult);

    chartInstance.current = new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Resultados actuales",
            data: currentResultPoints,
            backgroundColor: "#10B981",
            borderColor: "#059669",
            borderWidth: 2,
            pointRadius: 8,
            pointHoverRadius: 10,
          },
          {
            label: "Otros",
            data: otherPoints,
            backgroundColor: "#6B7280",
            borderColor: "#4B5563",
            borderWidth: 1,
            pointRadius: 6,
            pointHoverRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: `Visualización de ${chartData.length} personas`,
            color: "#333",
            font: {
              size: 16,
              weight: "bold",
            },
          },
          legend: {
            display: true,
            position: "top",
            labels: {
              usePointStyle: true,
              padding: 20,
              color: "#333",
            },
          },
          tooltip: {
            callbacks: {
              title: (context) => {
                const point = context[0];
                return point.raw.name || "Persona";
              },
              label: (context) => {
                const point = context.raw;
                return point.description || "Sin descripción";
              },
            },
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            titleColor: "#fff",
            bodyColor: "#fff",
            borderColor: "#fff",
            borderWidth: 1,
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Componente 1",
              color: "#333",
            },
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
          y: {
            title: {
              display: true,
              text: "Componente 2",
              color: "#333",
            },
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, currentResults]);

  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="no-data">
        <h3>📊 No hay personas para visualizar</h3>
        <p>Primero crea algunos datos de prueba para ver la visualización.</p>
      </div>
    );
  }

  return (
    <div className="simple-chart-container">
      <canvas ref={chartRef} />
    </div>
  );
};

export default SimpleVectorChart;
