import en from '../content/i18n/en.json';
import zh from '../content/i18n/zh.json';

const dicts = { en, zh } as const;

export type Locale = keyof typeof dicts;

export function t(key: string, lang: Locale = 'zh'): string {
  const parts = key.split('.');
  let val: any = dicts[lang] || dicts.zh;
  for (const p of parts) {
    val = val?.[p];
  }
  return typeof val === 'string' ? val : key;
}
