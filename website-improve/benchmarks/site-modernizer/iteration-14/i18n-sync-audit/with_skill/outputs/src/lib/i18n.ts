import en from '../content/i18n/en.json';
import zh from '../content/i18n/zh.json';

const dicts = { en, zh };

export function t(key: string, lang: string = 'zh'): string {
  const parts = key.split('.');
  let val: any = dicts[lang as keyof typeof dicts] || dicts.zh;
  for (const p of parts) val = val?.[p];
  return val || key;
}
