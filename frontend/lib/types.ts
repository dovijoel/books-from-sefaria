// Book configuration types (matches backend Pydantic schemas)
export interface TextEntry {
  link: string;
  commentary: string[];
  translation?: string;
  range?: string;
  dafrange?: string;
  format?: Partial<BookFormatSettings>;
}

export interface BookFormatSettings {
  paperheight: string;
  paperwidth: string;
  hebfont: string;
  hebboldfont: string;
  engfont: string;
  commentfont: string;
  top: string;
  bottom: string;
  inner: string;
  outer: string;
  fontsize: number;
  spacing: string;
  engfontsize: string;
  parskip: string;
  layout: "" | "twocol";
  twocolfootnotes: boolean;
  newpage: 0 | 1;
  pagenumloc: string;
  pagenumheb: boolean;
  headpos: string;
  evenhead: string;
  oddhead: string;
  chapfontsize: string;
  covercolor: string;
  covertextcolor: string;
  covertype: "hardcover" | "softcover";
  backtext: string;
  titleheb: string;
}

export interface BookConfig {
  id?: string;
  name: string;
  texts: TextEntry[];
  format: BookFormatSettings;
  createdAt?: string;
  updatedAt?: string;
}

export interface Job {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  config: BookConfig;
  createdAt: string;
  completedAt?: string;
  error?: string;
  pdfUrl?: string;
}

export interface SefariaTextSearchResult {
  ref: string;
  title: string;
  heTitle: string;
  titleVariants?: string[];
  type: string;
}

export const DEFAULT_FORMAT: BookFormatSettings = {
  paperheight: "11in",
  paperwidth: "8.5in",
  hebfont: "Frank Ruehl CLM",
  hebboldfont: "Frank Ruehl CLM",
  engfont: "Linux Libertine O",
  commentfont: "Linux Libertine O",
  top: "0.75in",
  bottom: "0.75in",
  inner: "1in",
  outer: "0.75in",
  fontsize: 12,
  spacing: "1.5",
  engfontsize: "11pt",
  parskip: "6pt",
  layout: "",
  twocolfootnotes: false,
  newpage: 0,
  pagenumloc: "bottom",
  pagenumheb: false,
  headpos: "center",
  evenhead: "",
  oddhead: "",
  chapfontsize: "14pt",
  covercolor: "#004E78",
  covertextcolor: "#C4A35A",
  covertype: "softcover",
  backtext: "",
  titleheb: "",
};

export const COMMENTARY_OPTIONS = [
  { value: "Rashi", label: "Rashi (רש״י)" },
  { value: "Tosafot", label: "Tosafot (תוספות)" },
  { value: "Rambam", label: "Rambam (רמב״ם)" },
  { value: "Ramban", label: "Ramban (רמב״ן)" },
  { value: "Ibn Ezra", label: "Ibn Ezra (אבן עזרא)" },
  { value: "Sforno", label: "Sforno (ספורנו)" },
  { value: "Kli Yakar", label: "Kli Yakar (כלי יקר)" },
  { value: "Or HaChaim", label: "Or HaChaim (אור החיים)" },
];

export const HEBREW_FONTS = [
  "Frank Ruehl CLM",
  "Ezra SIL",
  "SBL Hebrew",
  "David CLM",
  "Miriam CLM",
];

export const ENGLISH_FONTS = [
  "Linux Libertine O",
  "TeX Gyre Termes",
  "Palatino",
  "Times New Roman",
  "Georgia",
];

export const TEXT_CATEGORIES = [
  {
    name: "Torah",
    icon: "📜",
    texts: ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"],
  },
  {
    name: "Prophets",
    icon: "🕊️",
    texts: ["Joshua", "Judges", "Isaiah", "Jeremiah", "Ezekiel", "Amos"],
  },
  {
    name: "Writings",
    icon: "✍️",
    texts: ["Psalms", "Proverbs", "Job", "Song of Songs", "Ruth", "Esther"],
  },
  {
    name: "Talmud",
    icon: "📚",
    texts: ["Berakhot", "Shabbat", "Pesachim", "Yoma", "Sukkah", "Bava Metzia"],
  },
  {
    name: "Mishnah",
    icon: "🔖",
    texts: ["Pirkei Avot", "Mishnah Berakhot", "Mishnah Shabbat"],
  },
  {
    name: "Halakha",
    icon: "⚖️",
    texts: ["Shulchan Arukh", "Mishneh Torah", "Tur"],
  },
];
