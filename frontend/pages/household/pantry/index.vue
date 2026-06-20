<template>
  <v-container>
    <!-- Header -->
    <v-row class="mb-4" align="center">
      <v-col>
        <h1 class="text-h4 font-weight-bold">
          <v-icon start color="primary">{{ $globals.icons.pantry }}</v-icon>
          Pantry
        </h1>
        <p class="text-body-2 text-medium-emphasis mt-1">
          Track what you have on hand
        </p>
      </v-col>
    </v-row>

    <!-- Location Tabs -->
    <v-tabs v-model="activeTab" color="primary" class="mb-4">
      <v-tab value="all">All</v-tab>
      <v-tab v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</v-tab>
      <v-tab v-if="hasUnlocated" value="__no_location__">No Location</v-tab>
    </v-tabs>

    <!-- Loading -->
    <v-row v-if="loading">
      <v-col v-for="n in 6" :key="n" cols="12" sm="6" md="4">
        <v-skeleton-loader type="card" />
      </v-col>
    </v-row>

    <!-- Empty state -->
    <div v-else-if="filteredItems.length === 0" class="d-flex flex-column align-center justify-center py-16">
      <v-icon size="64" color="grey-lighten-1">{{ $globals.icons.pantry }}</v-icon>
      <p class="text-h6 text-medium-emphasis mt-4">Your pantry is empty</p>
      <p class="text-body-2 text-medium-emphasis mb-4">Add items to keep track of what you have</p>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog()">Add First Item</v-btn>
    </div>

    <!-- Item Grid -->
    <v-row v-else>
      <v-col v-for="item in filteredItems" :key="item.id" cols="12" sm="6" md="4" lg="3">
        <v-card
          class="pantry-item-card"
          :class="{ 'border-error': item.isOut, 'border-warning': item.isLow && !item.isOut }"
          @click="openEditDialog(item)"
        >
          <v-card-title class="text-body-1 font-weight-semibold pb-0">
            {{ item.name }}
          </v-card-title>
          <v-card-subtitle class="pt-0">
            <span v-if="item.location">{{ item.location }}</span>
            <span v-if="item.location && item.category" class="mx-1">·</span>
            <span v-if="item.category">{{ item.category }}</span>
          </v-card-subtitle>
          <v-card-text class="pb-1">
            <div v-if="item.quantity" class="text-body-2">
              {{ item.quantity }} {{ item.unit || "" }}
            </div>
            <div v-if="item.notes" class="text-caption text-medium-emphasis">{{ item.notes }}</div>
            <div class="mt-2 d-flex flex-wrap gap-1">
              <v-chip v-if="item.isOut" color="error" size="small" variant="tonal">Out</v-chip>
              <v-chip v-else-if="item.isLow" color="warning" size="small" variant="tonal">Low</v-chip>
              <v-chip v-else color="success" size="small" variant="tonal">In Stock</v-chip>
              <v-chip
                v-if="expiryChip(item)"
                :color="expiryChip(item)!.color"
                size="small"
                variant="tonal"
              >{{ expiryChip(item)!.label }}</v-chip>
            </div>
          </v-card-text>
          <v-card-actions class="pt-0" @click.stop>
            <v-btn-toggle
              :model-value="itemStatus(item)"
              density="compact"
              variant="outlined"
              color="primary"
              mandatory
              @update:model-value="setStatus(item, $event)"
            >
              <v-btn value="ok" size="small">OK</v-btn>
              <v-btn value="low" size="small" color="warning">Low</v-btn>
              <v-btn value="out" size="small" color="error">Out</v-btn>
            </v-btn-toggle>
            <v-spacer />
            <v-btn icon size="small" variant="text" color="grey" @click.stop="confirmDelete(item)">
              <v-icon size="small">{{ $globals.icons.delete }}</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- FAB -->
    <v-fab
      color="primary"
      icon
      location="bottom end"
      size="large"
      style="position: fixed; bottom: 24px; right: 24px;"
      @click="openAddDialog()"
    >
      <v-icon>{{ $globals.icons.create }}</v-icon>
    </v-fab>

    <!-- Add / Edit Dialog -->
    <v-dialog v-model="showItemDialog" max-width="480">
      <v-card>
        <v-card-title>{{ editingItem ? 'Edit Pantry Item' : 'Add Pantry Item' }}</v-card-title>
        <v-card-text>

          <!-- Food picker — same autocomplete used in ingredient editor -->
          <v-autocomplete
            v-model="selectedFood"
            v-model:search="foodSearch"
            :items="filteredFoods"
            item-title="name"
            return-object
            :custom-filter="() => true"
            label="Food"
            placeholder="Search foods…"
            clearable
            density="compact"
            variant="outlined"
            class="mb-3"
            @update:model-value="onFoodSelected"
          >
            <template #no-data>
              <div class="text-caption text-center py-2">No match — name will be used as-is</div>
            </template>
          </v-autocomplete>

          <!-- Free-form name (auto-filled from food, editable) -->
          <v-text-field
            v-model="form.name"
            label="Name"
            :hint="selectedFood ? 'Linked to food record' : 'No food record linked — won\'t update pantry from recipes'"
            persistent-hint
            required
            density="compact"
            variant="outlined"
            class="mb-3"
          />

          <v-row dense>
            <v-col cols="6">
              <v-combobox
                v-model="form.location"
                :items="locations"
                label="Location"
                placeholder="Fridge, Freezer, Top Shelf…"
                density="compact"
                variant="outlined"
                clearable
                hide-details
              />
            </v-col>
            <v-col cols="6">
              <v-combobox
                v-model="form.category"
                :items="categories"
                label="Category"
                placeholder="Dairy, Produce, Spices…"
                density="compact"
                variant="outlined"
                clearable
                hide-details
              />
            </v-col>
          </v-row>

          <v-row dense class="mb-1">
            <v-col cols="6">
              <v-text-field
                v-model.number="form.quantity"
                label="Quantity"
                type="number"
                min="0"
                density="compact"
                variant="outlined"
              />
            </v-col>
            <v-col cols="6">
              <v-combobox
                v-model="form.unit"
                :items="units"
                label="Unit"
                placeholder="cups, lbs, items…"
                density="compact"
                variant="outlined"
                clearable
                hide-details
              />
            </v-col>
          </v-row>

          <v-text-field
            v-model="form.notes"
            label="Notes"
            density="compact"
            variant="outlined"
            class="mb-3"
          />

          <v-menu v-model="expiryDateMenu" :close-on-content-click="false" location="bottom">
            <template #activator="{ props: menuProps }">
              <v-text-field
                :model-value="formatExpiryDisplay(form.expirationDate)"
                v-bind="menuProps"
                label="Expiration Date"
                density="compact"
                variant="outlined"
                readonly
                clearable
                class="mb-4"
                @click:clear="form.expirationDate = null"
              />
            </template>
            <v-date-picker
              :model-value="strToDate(form.expirationDate)"
              hide-header
              @update:model-value="(d) => { form.expirationDate = dateToStr(d); expiryDateMenu = false; }"
            />
          </v-menu>

          <!-- Stock status -->
          <div class="text-body-2 text-medium-emphasis mb-2">Stock status</div>
          <v-btn-toggle
            v-model="form.status"
            density="compact"
            variant="outlined"
            color="primary"
            mandatory
          >
            <v-btn value="ok">In Stock</v-btn>
            <v-btn value="low" color="warning">Low</v-btn>
            <v-btn value="out" color="error">Out</v-btn>
          </v-btn-toggle>

        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeItemDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            :disabled="!form.name"
            :loading="saving"
            @click="saveItem"
          >
            {{ editingItem ? 'Save' : 'Add' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { usePantryApi, type PantryItem, type PantryItemCreate, type PantryItemUpdate } from "~/composables/api/use-pantry-api";
import { useFoodStore } from "~/composables/store";
import { useSearch } from "~/composables/use-search";

const pantryApi = usePantryApi();

// ── Date helpers ─────────────────────────────────────────────────────────────
const expiryDateMenu = ref(false);

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

function formatExpiryDisplay(s: string | null): string {
  if (!s) return "";
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString();
}

// Food store — same source used by recipe ingredient editor
const foodStore = useFoodStore();
const { search: foodSearch, filtered: filteredFoods } = useSearch(foodStore.store);
const selectedFood = ref<{ id: string; name: string } | null>(null);

function onFoodSelected(food: { id: string; name: string } | null) {
  if (food) {
    form.value.name = food.name;
    form.value.foodId = food.id;
  }
  else {
    form.value.foodId = null;
  }
}

// Pantry items
const items = ref<PantryItem[]>([]);
const loading = ref(true);
const saving = ref(false);
const showItemDialog = ref(false);
const editingItem = ref<PantryItem | null>(null);
const activeTab = ref<string>("all");

type StatusValue = "ok" | "low" | "out";

interface ItemForm {
  name: string;
  foodId: string | null;
  location: string;
  category: string;
  quantity: number | undefined;
  unit: string;
  notes: string;
  status: StatusValue;
  expirationDate: string | null;
}

const defaultForm = (): ItemForm => ({
  name: "",
  foodId: null,
  location: "",
  category: "",
  quantity: undefined,
  unit: "",
  notes: "",
  status: "ok",
  expirationDate: null,
});

const form = ref<ItemForm>(defaultForm());

function itemStatus(item: PantryItem): StatusValue {
  if (item.isOut) return "out";
  if (item.isLow) return "low";
  return "ok";
}

function expiryChip(item: PantryItem): { color: string; label: string } | null {
  if (!item.expirationDate) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const expiry = new Date(item.expirationDate);
  expiry.setHours(0, 0, 0, 0);
  const diffMs = expiry.getTime() - today.getTime();
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return { color: "error", label: "Expired" };
  if (diffDays === 0) return { color: "error", label: "Exp: today" };
  if (diffDays <= 3) return { color: "error", label: `Exp: ${diffDays}d` };
  if (diffDays <= 7) return { color: "warning", label: `Exp: ${diffDays}d` };
  return null;
}

const locations = computed(() => {
  const locs = new Set(items.value.map(i => i.location).filter((l): l is string => !!l));
  return Array.from(locs).sort();
});

const hasUnlocated = computed(() => items.value.some(i => !i.location));

const categories = computed(() => {
  const cats = new Set(items.value.map(i => i.category).filter((c): c is string => !!c));
  return Array.from(cats).sort();
});

const units = computed(() => {
  const us = new Set(items.value.map(i => i.unit).filter((u): u is string => !!u));
  return Array.from(us).sort();
});

const filteredItems = computed(() => {
  if (activeTab.value === "all") return items.value;
  if (activeTab.value === "__no_location__") return items.value.filter(i => !i.location);
  return items.value.filter(i => i.location === activeTab.value);
});

function openAddDialog() {
  editingItem.value = null;
  selectedFood.value = null;
  foodSearch.value = "";
  form.value = defaultForm();
  showItemDialog.value = true;
}

function openEditDialog(item: PantryItem) {
  editingItem.value = item;
  // Restore food selection if linked
  if (item.foodId) {
    const food = filteredFoods.value.find((f: any) => f.id === item.foodId) || null;
    selectedFood.value = food as { id: string; name: string } | null;
  }
  else {
    selectedFood.value = null;
  }
  foodSearch.value = "";
  form.value = {
    name: item.name,
    foodId: item.foodId ?? null,
    location: item.location ?? "",
    category: item.category ?? "",
    quantity: item.quantity ?? undefined,
    unit: item.unit ?? "",
    notes: item.notes ?? "",
    status: itemStatus(item),
    expirationDate: item.expirationDate ?? null,
  };
  showItemDialog.value = true;
}

function closeItemDialog() {
  showItemDialog.value = false;
  editingItem.value = null;
  selectedFood.value = null;
  form.value = defaultForm();
}

async function saveItem() {
  if (!form.value.name) return;
  saving.value = true;

  const isLow = form.value.status === "low" || form.value.status === "out";
  const isOut = form.value.status === "out";

  if (editingItem.value) {
    const update: PantryItemUpdate = {
      name: form.value.name,
      foodId: form.value.foodId,
      location: form.value.location || null,
      category: form.value.category || null,
      quantity: form.value.quantity ?? null,
      unit: form.value.unit || null,
      notes: form.value.notes || null,
      isLow,
      isOut,
      expirationDate: form.value.expirationDate || null,
    };
    const { data } = await pantryApi.updatePantryItem(editingItem.value.id, update);
    if (data) {
      const idx = items.value.findIndex(i => i.id === editingItem.value!.id);
      if (idx >= 0) items.value[idx] = data;
    }
  }
  else {
    const create: PantryItemCreate = {
      name: form.value.name,
      foodId: form.value.foodId,
      location: form.value.location || null,
      category: form.value.category || null,
      quantity: form.value.quantity ?? null,
      unit: form.value.unit || null,
      notes: form.value.notes || null,
      isLow,
      isOut,
      expirationDate: form.value.expirationDate || null,
    };
    const { data } = await pantryApi.createPantryItem(create);
    if (data) items.value.push(data);
  }

  saving.value = false;
  closeItemDialog();
}

async function setStatus(item: PantryItem, status: StatusValue) {
  const update: PantryItemUpdate = {
    isLow: status === "low" || status === "out",
    isOut: status === "out",
  };
  const { data } = await pantryApi.updatePantryItem(item.id, update);
  if (data) {
    const idx = items.value.findIndex(i => i.id === item.id);
    if (idx >= 0) items.value[idx] = data;
  }
}

async function confirmDelete(item: PantryItem) {
  if (!confirm(`Remove "${item.name}" from pantry?`)) return;
  await pantryApi.deletePantryItem(item.id);
  items.value = items.value.filter(i => i.id !== item.id);
}

async function loadItems() {
  loading.value = true;
  const { data } = await pantryApi.getPantryItems();
  items.value = data || [];
  loading.value = false;
}

onMounted(() => {
  loadItems();
});
</script>

<style scoped>
.pantry-item-card {
  height: 100%;
  cursor: pointer;
}
.border-error {
  border-left: 4px solid rgb(var(--v-theme-error)) !important;
}
.border-warning {
  border-left: 4px solid rgb(var(--v-theme-warning)) !important;
}
</style>
