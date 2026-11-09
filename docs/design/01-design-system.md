# Design System

## Принцип двойного слоя

| Слой | Где | Характер |
|------|-----|----------|
| **Bank Trust** | Чат, суммы, платежи, налоги | Фирменный красный акцент, воздух, минимум декора |
| **Championship Delight** | Landing, первый onboarding splash | Энергия кейса (purple/lime), не переносить в money UI |

## Цвета (PRD + палитра)

Фирменный красный `#EF3124` и платиновый `#D1D5D8`. Полный визуальный контекст: [06-visual-language.md](06-visual-language.md).

| Token | Hex | Use |
|-------|-----|-----|
| `--color-primary` | `#EF3124` | CTA, акценты, нотификации (фирменный красный) |
| `--color-platinum` | `#D1D5D8` | Вторичные плашки, dividers, inactive chrome |
| `--color-ink` | `#0B1117` | Заголовки, dark bg |
| `--color-surface` | `#FFFFFF` | Карточки, light bg |
| `--color-muted` | `#F2F3F5` | Фон чата / canvas, disabled |
| `--color-success` | `#00C853` | Успех, green compliance |

### Delight (только маркетинг)

| Token | Approx | Use |
|-------|--------|-----|
| `--color-spark` | `#6C3CF0` | Hero background |
| `--color-volt` | `#C8F560` | Hero accents |
| `--color-smile` | `#FFB020` | Мелкие delight-детали |

**Запрет:** purple-on-white тема во всём приложении; glow-everywhere; «AI purple SaaS» клише в продуктовых экранах.

## Типографика

В продуктах используется современный гротеск (Manrope, system-ui).

| Role | Font | Notes |
|------|------|-------|
| UI / chat / dashboard | Manrope, system-ui | 16px body, line-height 150%; лёгкий и открытый ритм |
| Display / marketing | Manrope Bold | Только landing / промо |
| Figures | Tabular nums | Суммы налогов и платежей — крупнейший акцент иерархии |

Не строить UI только на Inter. Не использовать slab в money UI.

**Demo:** CSS-токены + шрифт Manrope; визуальный паритет и аккуратность.

## Spacing & radius

По референсам UI ([08-marketing-ui-patterns.md](08-marketing-ui-patterns.md)):

- База 4px; внутренний padding карточек 16–24.  
- **Витрина / landing / Home rows:** radius карточек **24–32px**; pills `999px`.  
- **GenUI money cards в чате:** radius 20–24px; только интерактивные поверхности.  
- Canvas страницы: `#F5F5F5` / `#F2F3F5`, карточки белые или pastel.  
- Макс. ширина колонки чата 720px desktop; mobile full-bleed.

## Elevation

- Мягкая рассеянная тень **или** разделение тоном (canvas vs surface).  
- Без тяжёлого multi-layer glow.

## Icons & 3D

| Зона | Стиль |
|------|--------|
| Landing / promo | Glossy 3D / clay (карта, монета, %) — реф. `references/web-2026/` |
| Home service rows | Компактный 3D справа (как «Сервисы») |
| Chat / compliance | Линейные 24px или простой светофор; без emoji как UI |

## Dark mode

- Marketing dark bento (чёрный canvas + цветные карточки) — **landing only**.  
- Prod SuperApp: deep black `#0B1117` опционально.  
- Demo workspace (налоги/чат): light-first.

## Components (atomic)

`ButtonPrimary`, `ButtonGhost`, `ChatBubble`, `Composer`, `DisclaimerBar`, `CjmStepper`, `HeroMetric`, `InsightRow`, плюс GenUI registry.

Дашборд Home: [07-dashboard-patterns.md](07-dashboard-patterns.md) (Role–Metric–Density–Action).  
UI-паттерны: [08-marketing-ui-patterns.md](08-marketing-ui-patterns.md) + скрины в `references/web-2026/`.

Доп. компоненты: `SegmentedPill`, `ServiceRow`, `PastelPromoCard`, `InvertCtaCard` (чёрная row как «Оформить самозанятость»).

## Motion tokens

См. [05-motion-voice-tone.md](05-motion-voice-tone.md). Длительности: 150 / 250 / 400ms; easing standard.
