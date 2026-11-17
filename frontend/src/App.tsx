import { useEffect, useState } from "react";

type EstadoApi = "verificando" | "conectada" | "no-disponible";

const mensajes: Record<EstadoApi, string> = {
  verificando: "Verificando la API…",
  conectada: "API REST conectada",
  "no-disponible": "API REST no disponible",
};

export default function App() {
  const [estado, setEstado] = useState<EstadoApi>("verificando");

  useEffect(() => {
    let activo = true;

    fetch("/api/v1/health/")
      .then((respuesta) => {
        if (activo) setEstado(respuesta.ok ? "conectada" : "no-disponible");
      })
      .catch(() => {
        if (activo) setEstado("no-disponible");
      });

    return () => {
      activo = false;
    };
  }, []);

  return (
    <main>
      <h1>Arcakane Zone</h1>
      <p>Frontend ejecutándose en Docker.</p>
      <p>{mensajes[estado]}</p>
      <p>
        La API está disponible en <code>/api/v1/</code> y el sitio HTML en{" "}
        <code>/</code> del backend.
      </p>
    </main>
  );
}
