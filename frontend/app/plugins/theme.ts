export interface ThemeConfig {
  lightPrimary: string;
  lightAccent: string;
  lightSecondary: string;
  lightSuccess: string;
  lightInfo: string;
  lightWarning: string;
  lightError: string;
  darkPrimary: string;
  darkAccent: string;
  darkSecondary: string;
  darkSuccess: string;
  darkInfo: string;
  darkWarning: string;
  darkError: string;
}

let __cachedTheme: ThemeConfig | undefined;

async function fetchTheme(): Promise<ThemeConfig | undefined> {
  const route = "/api/app/about/theme";

  try {
    const response = await fetch(route);
    const data = await response.json();
    return data as ThemeConfig;
  }
  catch {
    return undefined;
  }
}

export default defineNuxtPlugin(async (nuxtApp) => {
  nuxtApp.hook("vuetify:before-create", async ({ vuetifyOptions }) => {
    let theme = __cachedTheme;
    if (!theme) {
      theme = await fetchTheme();
      __cachedTheme = theme;
    }
    vuetifyOptions.theme = {
      defaultTheme: nuxtApp.$config.public.useDark ? "dark" : "light",
      variations: {
        colors: ["primary", "accent", "secondary", "success", "info", "warning", "error", "background"],
        lighten: 3,
        darken: 3,
      },
      themes: {
        light: {
          dark: false,
          colors: {
            primary: theme?.lightPrimary ?? "#558B2F",
            accent: theme?.lightAccent ?? "#8BC34A",
            secondary: theme?.lightSecondary ?? "#4A7C59",
            success: theme?.lightSuccess ?? "#43A047",
            info: theme?.lightInfo ?? "#1976D2",
            warning: theme?.lightWarning ?? "#F57F17",
            error: theme?.lightError ?? "#EF5350",
          },
        },
        dark: {
          dark: true,
          colors: {
            primary: theme?.darkPrimary ?? "#7CB342",
            accent: theme?.darkAccent ?? "#AED581",
            secondary: theme?.darkSecondary ?? "#66BB6A",
            success: theme?.darkSuccess ?? "#43A047",
            info: theme?.darkInfo ?? "#1976D2",
            warning: theme?.darkWarning ?? "#F57F17",
            error: theme?.darkError ?? "#EF5350",
            background: "#1E1E1E",
            surface: "#1E1E1E",
          },
        },
      },
    };
  });
});
