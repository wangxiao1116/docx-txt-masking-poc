import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatBytes(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

export function maskIdCards(text: string) {
  return text.replace(
    /(?<![0-9A-Za-z])(\d{6})(?:\d{8}|\d{5})(\d{3}[\dXx]|\d{4})(?![0-9A-Za-z])/g,
    (_match, start, end) => `${start}********${end}`,
  );
}
