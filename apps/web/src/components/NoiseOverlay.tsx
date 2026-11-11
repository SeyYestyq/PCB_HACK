/**
 * Зерно поверх подложки: SVG feTurbulence, без картинок и сетевых запросов.
 * Слой лежит под UI (z-index: 0), нажимаемость не перехватывает.
 */
export function NoiseOverlay() {
  return <div className="noise-overlay" aria-hidden />;
}
