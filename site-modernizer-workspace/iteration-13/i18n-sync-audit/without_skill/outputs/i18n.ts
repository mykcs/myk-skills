import zh from '../content/i18n/zh.json';
import en from '../content/i18n/en.json';

const translations: Record<string, typeof zh> = { zh, en };

export function getTranslations(lang: string) {
  return translations[lang] || translations['zh'];
}
