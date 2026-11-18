export interface CatalogCategory {
  id: string;
  name: string;
  description: string;
}

export interface CatalogGenre {
  id: string;
  name: string;
}

export type OfferStatus = "publicado" | "borrador" | "retirado";

export interface ProductOffer {
  id: string;
  platform: string;
  sku: string;
  price: number;
  stock: number;
  status: OfferStatus;
}

export interface ProductFeature {
  label: string;
  value: string;
}

export interface Product {
  id: string;
  title: string;
  description: string;
  longDescription: string;
  cover: string;
  gallery: readonly string[];
  releaseDate: string;
  category: CatalogCategory;
  genre: CatalogGenre;
  developer: string;
  featured: boolean;
  tags: readonly string[];
  features: readonly ProductFeature[];
  offers: readonly ProductOffer[];
}

export interface ProductFilters {
  query?: string;
  categoryId?: string;
  platform?: string;
}
