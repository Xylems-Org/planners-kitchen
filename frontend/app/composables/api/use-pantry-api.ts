import { useRequests } from "./api-client";

export interface PantryItem {
  id: string;
  householdId: string;
  groupId: string;
  name: string;
  foodId?: string | null;
  location?: string | null;
  category?: string | null;
  quantity?: number | null;
  unit?: string | null;
  notes?: string | null;
  isLow: boolean;
  isOut: boolean;
  lastUpdated?: string | null;
  expirationDate?: string | null;
}

export interface PantryItemCreate {
  name: string;
  foodId?: string | null;
  location?: string | null;
  category?: string | null;
  quantity?: number | null;
  unit?: string | null;
  notes?: string | null;
  isLow?: boolean;
  isOut?: boolean;
  expirationDate?: string | null;
}

export interface PantryItemUpdate {
  name?: string;
  foodId?: string | null;
  location?: string | null;
  category?: string | null;
  quantity?: number | null;
  unit?: string | null;
  notes?: string | null;
  isLow?: boolean;
  isOut?: boolean;
  expirationDate?: string | null;
}

export interface CookingCheckDepletion {
  foodId: string;
  status: "out" | "low" | "ok";
  quantity?: number | null;
  unit?: string | null;
  location?: string | null;
  category?: string | null;
  expirationDate?: string | null;
}

export interface CookingCheckRequest {
  recipeSlug: string;
  depletions: CookingCheckDepletion[];
}

export interface IngredientSuggestion {
  id: string;
  name: string;
  frequency: number;
}

export function usePantryApi() {
  const requests = useRequests();
  const BASE = "/api/households/pantry";

  async function getPantryItems(filters?: { location?: string; category?: string }) {
    const params: Record<string, string> = {};
    if (filters?.location) params.location = filters.location;
    if (filters?.category) params.category = filters.category;
    return await requests.get<PantryItem[]>(BASE, params);
  }

  async function createPantryItem(data: PantryItemCreate) {
    return await requests.post<PantryItem, PantryItemCreate>(BASE, data);
  }

  async function updatePantryItem(id: string, data: PantryItemUpdate) {
    return await requests.put<PantryItem, PantryItemUpdate>(`${BASE}/${id}`, data);
  }

  async function deletePantryItem(id: string) {
    return await requests.delete<void>(`${BASE}/${id}`);
  }

  async function cookingCheck(data: CookingCheckRequest) {
    return await requests.post<{ message: string }, CookingCheckRequest>(`${BASE}/cooking-check`, data);
  }

  async function getRecipePantryIngredients(slug: string) {
    return await requests.get<any[]>(`${BASE}/recipe/${slug}/ingredients`);
  }

  async function getIngredientSuggestions(limit = 10) {
    return await requests.get<IngredientSuggestion[]>(`${BASE}/suggestions/ingredients`, { limit });
  }

  return {
    getPantryItems,
    createPantryItem,
    updatePantryItem,
    deletePantryItem,
    cookingCheck,
    getRecipePantryIngredients,
    getIngredientSuggestions,
  };
}
