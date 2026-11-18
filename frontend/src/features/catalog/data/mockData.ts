import chronoForge from "../../../assets/covers/chrono-forge.svg";
import deepSignal from "../../../assets/covers/deep-signal.svg";
import guardiansOfAurora from "../../../assets/covers/guardians-of-aurora.svg";
import neonDrift from "../../../assets/covers/neon-drift.svg";
import pixelRealms from "../../../assets/covers/pixel-realms.svg";
import screenshotOne from "../../../assets/covers/screenshot-abstract-1.svg";
import screenshotTwo from "../../../assets/covers/screenshot-abstract-2.svg";
import shadowBloom from "../../../assets/covers/shadow-bloom.svg";
import skybound from "../../../assets/covers/skybound.svg";
import terminalVelocity from "../../../assets/covers/terminal-velocity.svg";
import type { CatalogCategory, CatalogGenre, Product } from "../types";

export const categories: readonly CatalogCategory[] = [
  {
    id: "1",
    name: "Acción",
    description: "Títulos intensos, combate directo y adrenalina sin pausa.",
  },
  {
    id: "2",
    name: "Aventura",
    description: "Historias por descubrir, mundos por recorrer y decisiones que importan.",
  },
  {
    id: "3",
    name: "Rol",
    description: "Sistemas de progresión, personajes memorables y largas campañas.",
  },
  {
    id: "4",
    name: "Estrategia",
    description: "Planificación, gestión de recursos y batallas tácticas.",
  },
  {
    id: "5",
    name: "Indie",
    description: "Propuestas originales de estudios independientes.",
  },
  {
    id: "6",
    name: "Terror",
    description: "Suspenso, oscuridad y experiencias para los más valientes.",
  },
];

export const genres: readonly CatalogGenre[] = [
  { id: "1", name: "Acción" },
  { id: "2", name: "Aventura" },
  { id: "3", name: "Rol" },
  { id: "4", name: "Estrategia" },
  { id: "5", name: "Indie" },
  { id: "6", name: "Terror" },
];

export const platforms: readonly string[] = [
  "PC",
  "PlayStation 5",
  "Xbox Series X|S",
  "Nintendo Switch",
];

const gallery = [screenshotOne, screenshotTwo] as const;

export const products: readonly Product[] = [
  {
    id: "1",
    title: "Neon Drift",
    description: "Carreras nocturnas en una ciudad que nunca apaga sus luces.",
    longDescription:
      "Corre por las autopistas elevadas de una metrópolis neon, ajusta tu motor, esquiva la policía y escribe tu nombre en la escena clandestina de las carreras callejeras.",
    cover: neonDrift,
    gallery,
    releaseDate: "2026-02-14",
    category: categories[0]!,
    genre: genres[0]!,
    developer: "Midnight Circuit",
    featured: true,
    tags: ["Carreras", "Multijugador", "Arcade"],
    features: [
      { label: "Idiomas", value: "Español, Inglés, Portugués" },
      { label: "Modo", value: "Un jugador y multijugador en línea" },
      { label: "Clasificación", value: "PEGI 12" },
      { label: "Requisitos", value: "16 GB RAM · GPU de 6 GB" },
    ],
    offers: [
      {
        id: "o-1-pc",
        platform: "PC",
        sku: "AZ-ND-PC",
        price: 89000,
        stock: 24,
        status: "publicado",
      },
      {
        id: "o-1-ps5",
        platform: "PlayStation 5",
        sku: "AZ-ND-PS5",
        price: 109000,
        stock: 8,
        status: "publicado",
      },
    ],
  },
  {
    id: "2",
    title: "Guardians of Aurora",
    description: "Une las piezas de un antiguo pacto para devolver la luz al reino.",
    longDescription:
      "Explora islas flotantes, resuelve enigmas de la aurora y forma un equipo con guardianes elementales en una aventura cooperativa llena de secretos.",
    cover: guardiansOfAurora,
    gallery,
    releaseDate: "2025-11-07",
    category: categories[1]!,
    genre: genres[1]!,
    developer: "Lumen Forge",
    featured: true,
    tags: ["Cooperativo", "Puzzle", "Fantasía"],
    features: [
      { label: "Idiomas", value: "Español, Inglés, Francés" },
      { label: "Modo", value: "Hasta 4 jugadores en línea" },
      { label: "Clasificación", value: "PEGI 7" },
      { label: "Requisitos", value: "12 GB RAM · GPU de 4 GB" },
    ],
    offers: [
      {
        id: "o-2-ps5",
        platform: "PlayStation 5",
        sku: "AZ-GA-PS5",
        price: 119000,
        stock: 15,
        status: "publicado",
      },
      {
        id: "o-2-switch",
        platform: "Nintendo Switch",
        sku: "AZ-GA-SW",
        price: 99000,
        stock: 11,
        status: "publicado",
      },
    ],
  },
  {
    id: "3",
    title: "Chrono Forge",
    description: "Construye, investiga y domina el tiempo en una colonia mecanizada.",
    longDescription:
      "Gestiona una forja que atraviesa eras, investiga tecnologías perdidas y envía expediciones a través de líneas temporales inestables para asegurar el futuro de tu colonia.",
    cover: chronoForge,
    gallery,
    releaseDate: "2026-01-21",
    category: categories[3]!,
    genre: genres[3]!,
    developer: "Iron Meridian",
    featured: false,
    tags: ["Construcción", "Gestión", "Ciencia ficción"],
    features: [
      { label: "Idiomas", value: "Español, Inglés" },
      { label: "Modo", value: "Un jugador" },
      { label: "Clasificación", value: "PEGI 12" },
      { label: "Requisitos", value: "8 GB RAM · GPU integrada" },
    ],
    offers: [
      {
        id: "o-3-pc",
        platform: "PC",
        sku: "AZ-CF-PC",
        price: 99000,
        stock: 32,
        status: "publicado",
      },
      {
        id: "o-3-xbox",
        platform: "Xbox Series X|S",
        sku: "AZ-CF-XBX",
        price: 105000,
        stock: 6,
        status: "publicado",
      },
    ],
  },
  {
    id: "4",
    title: "Shadow Bloom",
    description: "Un RPG oscuro donde cada elección deja una marca permanente.",
    longDescription:
      "Adéntrate en un bosque vivo que responde a tus decisiones. Descubre linajes olvidados, forja alianzas peligrosas y cultiva un jardín que florece solo en la oscuridad.",
    cover: shadowBloom,
    gallery,
    releaseDate: "2025-09-30",
    category: categories[2]!,
    genre: genres[2]!,
    developer: "Nocturne Studio",
    featured: true,
    tags: ["RPG", "Narrativa", "Elecciones"],
    features: [
      { label: "Idiomas", value: "Español, Inglés, Alemán" },
      { label: "Modo", value: "Un jugador" },
      { label: "Clasificación", value: "PEGI 16" },
      { label: "Requisitos", value: "16 GB RAM · GPU de 6 GB" },
    ],
    offers: [
      {
        id: "o-4-pc",
        platform: "PC",
        sku: "AZ-SB-PC",
        price: 139000,
        stock: 19,
        status: "publicado",
      },
      {
        id: "o-4-ps5",
        platform: "PlayStation 5",
        sku: "AZ-SB-PS5",
        price: 149000,
        stock: 4,
        status: "publicado",
      },
    ],
  },
  {
    id: "5",
    title: "Skybound Odyssey",
    description: "Navega sobre las nubes y descubre islas que nadie ha tocado.",
    longDescription:
      "Prepara tu dirigible, recluta una tripulación excéntrica y cartografía un archipiélago suspendido sobre una niebla eterna en esta aventura familiar.",
    cover: skybound,
    gallery,
    releaseDate: "2025-06-18",
    category: categories[1]!,
    genre: genres[1]!,
    developer: "Paper Kite Games",
    featured: false,
    tags: ["Exploración", "Familiar", "Dirigibles"],
    features: [
      { label: "Idiomas", value: "Español, Inglés, Italiano" },
      { label: "Modo", value: "Un jugador y cooperativo local" },
      { label: "Clasificación", value: "PEGI 3" },
      { label: "Requisitos", value: "8 GB RAM · GPU de 2 GB" },
    ],
    offers: [
      {
        id: "o-5-switch",
        platform: "Nintendo Switch",
        sku: "AZ-SO-SW",
        price: 79000,
        stock: 21,
        status: "publicado",
      },
      {
        id: "o-5-ps5",
        platform: "PlayStation 5",
        sku: "AZ-SO-PS5",
        price: 89000,
        stock: 0,
        status: "publicado",
      },
    ],
  },
  {
    id: "6",
    title: "Terminal Velocity",
    description: "Supera una estación orbital en caída libre a máxima velocidad.",
    longDescription:
      "Corre, salta y deslízate por los pasillos de una estación que se desintegra. Cada segundo cuenta y cada atajo tiene un precio en esta carrera contrarreloj.",
    cover: terminalVelocity,
    gallery,
    releaseDate: "2026-03-05",
    category: categories[0]!,
    genre: genres[0]!,
    developer: "Redline Collective",
    featured: true,
    tags: ["Parkour", "Contrarreloj", "Acción"],
    features: [
      { label: "Idiomas", value: "Español, Inglés, Japonés" },
      { label: "Modo", value: "Un jugador y tableros de récords" },
      { label: "Clasificación", value: "PEGI 12" },
      { label: "Requisitos", value: "12 GB RAM · GPU de 4 GB" },
    ],
    offers: [
      {
        id: "o-6-pc",
        platform: "PC",
        sku: "AZ-TV-PC",
        price: 109000,
        stock: 27,
        status: "publicado",
      },
      {
        id: "o-6-xbox",
        platform: "Xbox Series X|S",
        sku: "AZ-TV-XBX",
        price: 115000,
        stock: 9,
        status: "publicado",
      },
    ],
  },
  {
    id: "7",
    title: "Pixel Realms",
    description: "Una aventura retro compuesta por pequeños mundos que se conectan.",
    longDescription:
      "Recorre reinos de ocho bits, rescata a sus habitantes y desbloquea atajos secretos en un homenaje moderno a las aventuras clásicas de exploración.",
    cover: pixelRealms,
    gallery,
    releaseDate: "2025-04-12",
    category: categories[4]!,
    genre: genres[4]!,
    developer: "Tiny Lantern",
    featured: false,
    tags: ["Pixel art", "Metroidvania", "Indie"],
    features: [
      { label: "Idiomas", value: "Español, Inglés" },
      { label: "Modo", value: "Un jugador" },
      { label: "Clasificación", value: "PEGI 7" },
      { label: "Requisitos", value: "4 GB RAM · GPU integrada" },
    ],
    offers: [
      {
        id: "o-7-pc",
        platform: "PC",
        sku: "AZ-PR-PC",
        price: 59000,
        stock: 45,
        status: "publicado",
      },
      {
        id: "o-7-switch",
        platform: "Nintendo Switch",
        sku: "AZ-PR-SW",
        price: 65000,
        stock: 18,
        status: "publicado",
      },
    ],
  },
  {
    id: "8",
    title: "Deep Signal",
    description: "Investiga una señal imposible en las profundidades del océano.",
    longDescription:
      "Dirige una expedición submarina, interpreta lecturas de sonar y decide cuándo subir a la superficie. Una experiencia de terror psicológico donde la presión es real.",
    cover: deepSignal,
    gallery,
    releaseDate: "2026-05-29",
    category: categories[5]!,
    genre: genres[5]!,
    developer: "Abyss Works",
    featured: false,
    tags: ["Terror", "Sonar", "Supervivencia"],
    features: [
      { label: "Idiomas", value: "Español, Inglés" },
      { label: "Modo", value: "Un jugador" },
      { label: "Clasificación", value: "PEGI 16" },
      { label: "Requisitos", value: "16 GB RAM · GPU de 6 GB" },
    ],
    offers: [
      {
        id: "o-8-pc",
        platform: "PC",
        sku: "AZ-DS-PC",
        price: 95000,
        stock: 13,
        status: "publicado",
      },
      {
        id: "o-8-ps5",
        platform: "PlayStation 5",
        sku: "AZ-DS-PS5",
        price: 99000,
        stock: 0,
        status: "publicado",
      },
    ],
  },
];
