<template>
  <v-dialog
    :model-value="modelValue"
    max-width="580"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="d-flex align-center gap-2">
        <v-icon color="primary">
          {{ $globals.icons.pantry }}
        </v-icon>
        Check Your Pantry
      </v-card-title>
      <v-card-subtitle class="pb-2">
        Update remaining quantities for ingredients you used.
      </v-card-subtitle>

      <v-card-text>
        <div
          v-if="ingredients.length === 0"
          class="text-medium-emphasis py-4 text-center"
        >
          No food ingredients found for this recipe.
        </div>

        <template v-else>
          <!-- ── Existing pantry items ── -->
          <template v-if="existingIngredients.length > 0">
            <div class="text-overline text-medium-emphasis mb-1">
              In Your Pantry
            </div>
            <v-list density="compact">
              <v-list-item
                v-for="ingredient in existingIngredients"
                :key="ingredient.referenceId || ingredient.foodId"
                class="px-0"
              >
                <template #default>
                  <div class="py-2">
                    <div class="d-flex align-center mb-1">
                      <span class="text-body-2 font-weight-medium">{{ ingredient.foodName }}</span>
                      <span
                        v-if="ingredient.quantity || ingredient.unit"
                        class="text-caption text-medium-emphasis ml-2"
                      >
                        (recipe: {{ ingredient.quantity ?? "" }} {{ ingredient.unit ?? "" }})
                      </span>
                    </div>
                    <div class="d-flex align-center gap-2 flex-wrap">
                      <v-text-field
                        v-model.number="depletions[ingredient.foodId!].quantity"
                        type="number"
                        min="0"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Remaining"
                        style="max-width: 110px;"
                      />
                      <v-combobox
                        v-model="depletions[ingredient.foodId!].pantryUnit"
                        :items="availableUnits"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Unit"
                        style="max-width: 110px;"
                      />
                      <!-- Date picker for expiry -->
                      <v-menu
                        v-model="openDatePickers[ingredient.foodId!]"
                        :close-on-content-click="false"
                        location="bottom"
                      >
                        <template #activator="{ props: menuProps }">
                          <v-text-field
                            :model-value="formatDate(depletions[ingredient.foodId!].expirationDate)"
                            v-bind="menuProps"
                            density="compact"
                            variant="outlined"
                            hide-details
                            label="Expiry date"
                            readonly
                            clearable
                            style="max-width: 160px;"
                            @click:clear="depletions[ingredient.foodId!].expirationDate = null"
                          />
                        </template>
                        <v-date-picker
                          :model-value="strToDate(depletions[ingredient.foodId!].expirationDate)"
                          hide-header
                          @update:model-value="(d) => pickDate(ingredient.foodId!, d)"
                        />
                      </v-menu>
                      <v-btn-toggle
                        v-model="depletions[ingredient.foodId!].status"
                        density="compact"
                        variant="outlined"
                        color="primary"
                        mandatory
                        class="ml-auto"
                      >
                        <v-btn value="ok" size="small">OK</v-btn>
                        <v-btn value="low" size="small" color="warning">Low</v-btn>
                        <v-btn value="out" size="small" color="error">Out</v-btn>
                      </v-btn-toggle>
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </template>

          <!-- ── New items (not yet in pantry) ── -->
          <template v-if="newIngredients.length > 0">
            <v-divider v-if="existingIngredients.length > 0" class="my-3" />
            <div class="d-flex align-center gap-1 text-overline text-medium-emphasis mb-1">
              <v-icon size="small" color="primary">{{ $globals.icons.plus }}</v-icon>
              New to Pantry
            </div>
            <v-list density="compact">
              <v-list-item
                v-for="ingredient in newIngredients"
                :key="ingredient.referenceId || ingredient.foodId"
                class="px-0"
              >
                <template #default>
                  <div class="py-2">
                    <div class="d-flex align-center mb-2">
                      <span class="text-body-2 font-weight-medium">{{ ingredient.foodName }}</span>
                      <span
                        v-if="ingredient.quantity || ingredient.unit"
                        class="text-caption text-medium-emphasis ml-2"
                      >
                        (recipe: {{ ingredient.quantity ?? "" }} {{ ingredient.unit ?? "" }})
                      </span>
                    </div>
                    <!-- Row 1: qty + unit + expiry + status -->
                    <div class="d-flex align-center gap-2 flex-wrap mb-2">
                      <v-text-field
                        v-model.number="depletions[ingredient.foodId!].quantity"
                        type="number"
                        min="0"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Remaining"
                        style="max-width: 110px;"
                      />
                      <v-combobox
                        v-model="depletions[ingredient.foodId!].pantryUnit"
                        :items="availableUnits"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Unit"
                        style="max-width: 110px;"
                      />
                      <v-menu
                        v-model="openDatePickers[ingredient.foodId!]"
                        :close-on-content-click="false"
                        location="bottom"
                      >
                        <template #activator="{ props: menuProps }">
                          <v-text-field
                            :model-value="formatDate(depletions[ingredient.foodId!].expirationDate)"
                            v-bind="menuProps"
                            density="compact"
                            variant="outlined"
                            hide-details
                            label="Expiry date"
                            readonly
                            clearable
                            style="max-width: 160px;"
                            @click:clear="depletions[ingredient.foodId!].expirationDate = null"
                          />
                        </template>
                        <v-date-picker
                          :model-value="strToDate(depletions[ingredient.foodId!].expirationDate)"
                          hide-header
                          @update:model-value="(d) => pickDate(ingredient.foodId!, d)"
                        />
                      </v-menu>
                      <v-btn-toggle
                        v-model="depletions[ingredient.foodId!].status"
                        density="compact"
                        variant="outlined"
                        color="primary"
                        mandatory
                        class="ml-auto"
                      >
                        <v-btn value="ok" size="small">OK</v-btn>
                        <v-btn value="low" size="small" color="warning">Low</v-btn>
                        <v-btn value="out" size="small" color="error">Out</v-btn>
                      </v-btn-toggle>
                    </div>
                    <!-- Row 2: location + category -->
                    <div class="d-flex gap-2">
                      <v-combobox
                        v-model="depletions[ingredient.foodId!].location"
                        :items="availableLocations"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Location"
                        class="flex-grow-1"
                      />
                      <v-combobox
                        v-model="depletions[ingredient.foodId!].category"
                        :items="availableCategories"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Category"
                        class="flex-grow-1"
                      />
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </template>
        </template>
      </v-card-text>

      <v-card-actions>
        <v-btn
          variant="text"
          @click="cancel"
        >
          Skip
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          :loading="saving"
          @click="confirm"
        >
          Update Pantry
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { usePantryApi } from "~/composables/api/use-pantry-api";
import { alert } from "~/composables/use-toast";

interface RecipeIngredientRef {
  referenceId: string;
  foodId?: string | null;
  foodName: string;
  quantity?: number | null;
  unit?: string | null;
}

interface DepletionEntry {
  status: "ok" | "low" | "out";
  quantity: number | null;
  expirationDate: string | null;
  location: string | null;
  category: string | null;
  pantryUnit: string | null;
}

const props = defineProps<{
  modelValue: boolean;
  recipeSlug: string;
  ingredients: RecipeIngredientRef[];
}>();

const emit = defineEmits<{
  "update:modelValue": [val: boolean];
  done: [];
}>();

const pantryApi = usePantryApi();
const saving = ref(false);

const depletions = ref<Record<string, DepletionEntry>>({});
const newItemFoodIds = ref<Set<string>>(new Set());
const openDatePickers = ref<Record<string, boolean>>({});

const availableLocations = ref<string[]>([]);
const availableUnits = ref<string[]>([]);
const availableCategories = ref<string[]>([]);

// ── Date helpers ────────────────────────────────────────────────────────────
function strToDate(s: string | null): Date | undefined {
  if (!s) return undefined;
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function dateToStr(d: Date | null | undefined): string | null {
  if (!d) return null;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function formatDate(s: string | null): string {
  if (!s) return "";
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString();
}

function pickDate(key: string, d: Date | null) {
  depletions.value[key].expirationDate = dateToStr(d);
  openDatePickers.value[key] = false;
}

// ── Computed ingredient lists ───────────────────────────────────────────────
const existingIngredients = computed(() =>
  props.ingredients.filter(ing => {
    const key = ing.foodId || ing.referenceId;
    return key && !newItemFoodIds.value.has(key);
  }),
);

const newIngredients = computed(() =>
  props.ingredients.filter(ing => {
    const key = ing.foodId || ing.referenceId;
    return key && newItemFoodIds.value.has(key);
  }),
);

// ── Initialise on open ──────────────────────────────────────────────────────
async function initDepletions() {
  // Build map synchronously first so the template has valid entries immediately
  const map: Record<string, DepletionEntry> = {};
  const pickers: Record<string, boolean> = {};
  for (const ing of props.ingredients) {
    const key = ing.foodId || ing.referenceId;
    if (key) {
      map[key] = { status: "ok", quantity: null, expirationDate: null, location: null, category: null, pantryUnit: ing.unit ?? null };
      pickers[key] = false;
    }
  }
  depletions.value = map;
  openDatePickers.value = pickers;
  newItemFoodIds.value = new Set();

  if (!props.recipeSlug) return;

  // Fetch pantry data in parallel
  const [crossRef, allItems] = await Promise.all([
    pantryApi.getRecipePantryIngredients(props.recipeSlug),
    pantryApi.getPantryItems(),
  ]);

  // Populate available locations & units from all pantry items
  if (allItems.data) {
    availableLocations.value = [...new Set(allItems.data.map(i => i.location).filter((l): l is string => !!l))].sort();
    availableUnits.value = [...new Set(allItems.data.map(i => i.unit).filter((u): u is string => !!u))].sort();
    availableCategories.value = [...new Set(allItems.data.map(i => i.category).filter((c): c is string => !!c))].sort();
  }

  // Apply cross-ref data
  const newIds = new Set<string>();
  if (crossRef.data) {
    for (const row of crossRef.data) {
      const key = row.food_id || row.reference_id;
      if (key && depletions.value[key] !== undefined) {
        if (row.pantry_items?.length > 0) {
          depletions.value[key].quantity = row.pantry_items[0].quantity ?? null;
          depletions.value[key].expirationDate = row.pantry_items[0].expiration_date ?? null;
          depletions.value[key].pantryUnit = row.pantry_items[0].unit ?? depletions.value[key].pantryUnit;
        }
        else {
          newIds.add(key);
        }
      }
    }
  }

  newItemFoodIds.value = newIds;
}

watchEffect(() => {
  if (props.modelValue) {
    initDepletions();
  }
});

// ── Submit ──────────────────────────────────────────────────────────────────
async function confirm() {
  saving.value = true;
  const deplList = props.ingredients
    .filter(ing => ing.foodId)
    .map(ing => ({
      foodId: ing.foodId!,
      status: depletions.value[ing.foodId!]?.status ?? "ok",
      quantity: depletions.value[ing.foodId!]?.quantity ?? null,
      unit: depletions.value[ing.foodId!]?.pantryUnit ?? ing.unit ?? null,
      expirationDate: depletions.value[ing.foodId!]?.expirationDate ?? null,
      location: depletions.value[ing.foodId!]?.location ?? null,
      category: depletions.value[ing.foodId!]?.category ?? null,
    }));

  if (deplList.length > 0) {
    const { error } = await pantryApi.cookingCheck({
      recipeSlug: props.recipeSlug,
      depletions: deplList,
    });

    if (!error) {
      alert.success("Pantry updated!");
    }
    else {
      alert.error("Failed to update pantry");
    }
  }

  saving.value = false;
  emit("update:modelValue", false);
  emit("done");
}

function cancel() {
  emit("update:modelValue", false);
}
</script>
