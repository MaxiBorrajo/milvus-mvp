import { useCallback } from "react";
import useApi from "./useApi";

const useTestData = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const createTestData = useCallback(
    async (testData) => {
      try {
        const result = await makeRequest(
          "http://localhost:8000/insert-person",
          {
            method: "POST",
            body: JSON.stringify(testData),
          }
        );

        return result;
      } catch (err) {
        // El error ya está manejado en useApi
        throw err;
      }
    },
    [makeRequest]
  );

  const getDefaultTestData = () => {
    return {
      items: generateMockPersons(),
    };
  };

  const generateMockPersons = () => {
    const persons = [
      {
        name: "Joel Cabral",
        description:
          "Desarrollador full-stack con experiencia en React y Node.js. Especialista en aplicaciones web modernas y optimización de rendimiento.",
      },
      {
        name: "Lucas Josué Coronel",
        description:
          "Analista de datos y experto en machine learning. Capacidad para extraer insights valiosos de grandes volúmenes de información.",
      },
      {
        name: "Matías Francisco Deo",
        description:
          "Diseñador UX/UI con enfoque en experiencia de usuario. Creador de interfaces intuitivas y atractivas.",
      },
      {
        name: "Damián Peñalver",
        description:
          "Project Manager con amplia experiencia en gestión de equipos ágiles. Especialista en metodologías Scrum y Kanban.",
      },
      {
        name: "Enzo Ploza",
        description:
          "Ingeniero de sistemas con expertise en arquitectura de software. Diseñador de soluciones escalables y robustas.",
      },
      {
        name: "Lourdes De La Cuerda",
        description:
          "Especialista en marketing digital y redes sociales. Estratega de contenido y crecimiento de audiencias.",
      },
      {
        name: "Axel García",
        description:
          "Desarrollador backend especializado en APIs RESTful y bases de datos. Experto en seguridad y optimización.",
      },
      {
        name: "Damián Manchali",
        description:
          "DevOps engineer con experiencia en CI/CD y cloud computing. Especialista en AWS y Docker.",
      },
      {
        name: "Hernán Moreyra",
        description:
          "Analista de negocio con fuerte background en finanzas. Experto en análisis de rentabilidad y estrategias corporativas.",
      },
      {
        name: "Francisco Raffin",
        description:
          "Desarrollador móvil con experiencia en React Native e iOS. Creador de aplicaciones nativas multiplataforma.",
      },
      {
        name: "Walter Altamirano",
        description:
          "Especialista en ciberseguridad y auditoría de sistemas. Experto en protección de datos y compliance.",
      },
      {
        name: "Ian Bravo",
        description:
          "Diseñador gráfico y artista digital. Creador de identidades visuales y contenido multimedia impactante.",
      },
      {
        name: "Matías Javier Maza Vega",
        description:
          "Ingeniero de datos con expertise en Big Data y procesamiento distribuido. Especialista en Hadoop y Spark.",
      },
      {
        name: "Luciana Merlino",
        description:
          "Product Manager con experiencia en desarrollo de productos digitales. Especialista en investigación de usuarios y validación.",
      },
      {
        name: "Abril Rodríguez",
        description:
          "Especialista en recursos humanos y desarrollo organizacional. Experta en reclutamiento y gestión de talento.",
      },
      {
        name: "Maximiliano Borrajo",
        description:
          "Desarrollador frontend con expertise en JavaScript moderno y frameworks. Especialista en performance y accesibilidad.",
      },
      {
        name: "Tomás Fuentes",
        description:
          "Analista de calidad y testing automatizado. Experto en metodologías de testing y herramientas de automatización.",
      },
      {
        name: "Cristian Nasr",
        description:
          "Arquitecto de software con experiencia en microservicios y sistemas distribuidos. Especialista en patrones de diseño.",
      },
      {
        name: "Franco Orizonte",
        description:
          "Especialista en inteligencia artificial y procesamiento de lenguaje natural. Experto en chatbots y NLP.",
      },
      {
        name: "Nicolás Torboli",
        description:
          "Desarrollador de videojuegos con experiencia en Unity y Unreal Engine. Creador de experiencias inmersivas.",
      },
      {
        name: "Ornella Bottiggi",
        description:
          "Especialista en comunicación corporativa y relaciones públicas. Experta en gestión de crisis y branding.",
      },
      {
        name: "Melisa Confalonieri",
        description:
          "Diseñadora de experiencia de usuario con enfoque en investigación. Especialista en usabilidad y testing de usuarios.",
      },
      {
        name: "Chiara Forti Dono",
        description:
          "Analista de marketing con expertise en análisis de competencia y posicionamiento. Especialista en estrategias de mercado.",
      },
      {
        name: "Candela Marzaroli",
        description:
          "Desarrolladora de aplicaciones web con experiencia en e-commerce. Especialista en optimización de conversión.",
      },
      {
        name: "Josefina Volosin",
        description:
          "Especialista en gestión de proyectos de innovación. Experta en metodologías ágiles y transformación digital.",
      },
      {
        name: "Carolina Ciampini",
        description:
          "Analista de datos con expertise en visualización y storytelling. Especialista en Tableau y Power BI.",
      },
      {
        name: "Lucrecia Colón",
        description:
          "Especialista en customer success y experiencia del cliente. Experta en retención y satisfacción de usuarios.",
      },
      {
        name: "Maria Emilia Díaz",
        description:
          "Desarrolladora full-stack con experiencia en aplicaciones empresariales. Especialista en integración de sistemas.",
      },
      {
        name: "Nehuen Gallitelli",
        description:
          "Especialista en automatización de procesos y RPA. Experto en optimización de flujos de trabajo.",
      },
      {
        name: "Abril Orlando",
        description:
          "Diseñadora de productos digitales con enfoque en innovación. Especialista en design thinking y prototipado.",
      },
      {
        name: "Sebastián Correa",
        description:
          "Ingeniero de infraestructura con experiencia en redes y telecomunicaciones. Especialista en arquitectura de red.",
      },
      {
        name: "Lautaro Galvez Monge",
        description:
          "Desarrollador de aplicaciones móviles nativas. Especialista en Android y Kotlin con enfoque en performance.",
      },
      {
        name: "Lautaro Lovato Herrera",
        description:
          "Especialista en machine learning y deep learning. Experto en redes neuronales y algoritmos de IA.",
      },
      {
        name: "Lucas Sanguinetti",
        description:
          "Analista de sistemas con experiencia en integración de APIs. Especialista en middleware y conectividad.",
      },
      {
        name: "Lucía Viazzo",
        description:
          "Especialista en gestión de contenido digital y SEO. Experta en estrategias de posicionamiento web.",
      },
    ];

    return persons;
  };

  return {
    loading,
    error,
    data,
    createTestData,
    getDefaultTestData,
    reset,
  };
};

export default useTestData;
