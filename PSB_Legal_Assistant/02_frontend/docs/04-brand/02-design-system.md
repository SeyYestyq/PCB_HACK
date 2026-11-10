# 02. Дизайн-система: токены, шкалы, сетка, состояния

Этот файл реализуется напрямую в `apps/web/src/app/globals.css` и `tailwind.config.ts`. Все значения в px для веба (1 CSS px соответствует 1 pt HIG на стандартной плотности). Обоснование выбора цветов и шрифтов в `01-brand-book.md`; компоненты в `03`.

Условные обозначения источников (коды из `01-brand-book.md` §4.1): **[B1]** гайд ПСБ 02.10-02.12, **[B4]** CSS psbank.ru, **[B5]** Коммерсантъ о ребрендинге, **[Calc]** производное значение, рассчитано из канона, контраст проверен по WCAG 2.2, **[HIG]** Apple Human Interface Guidelines, **[WCAG]** WCAG 2.2.

---

## 1. Светлая или тёмная тема: решение

**По умолчанию светлая. Тёмная поддерживается через `prefers-color-scheme: dark`, без отдельного переключателя в приложении.**

Почему светлая основная:
1. Позитивная полярность (тёмный текст на светлом) даёт лучшую точность вычитки и чтения у молодых и пожилых пользователей: Piepenbrock, Mayr, Mund, Buchner (2013), «Positive display polarity is advantageous for both younger and older adults», Ergonomics 56(7), [doi:10.1080/00140139.2013.790485](https://doi.org/10.1080/00140139.2013.790485). Юрист вычитывает формулировки пунктов, это задача точности.
2. Документы-первоисточники (договоры, кодексы) существуют как чёрный текст на белом листе. Совпадение с привычной формой снижает когнитивную нагрузку при сверке.
3. Бренд ПСБ светлый: фон сайта `#F8F8FC`, текст `#3E3E59` [B4]; Коммерсантъ о ребрендинге: «Предпочтение в офисах ПСБ отдано светлым, спокойным тонам» [B5].
4. Рабочее место юриста в банке: офисное освещение, длинные сессии, печать.

Почему тёмная только системная: HIG Dark Mode: «Avoid offering an app-specific appearance setting» и «Ensure that your app looks good in both appearance modes» ([dark-mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode)). Тёмная тема в нашем продукте не «премиум-стиль» и не декор (референсы `refs/10`, `refs/12` с тёмным оформлением используются только для структуры).

---

## 2. Цвет: токены

### 2.1. Светлая тема (`:root`)

```css
:root {
  /* Бренд ПСБ */
  --psb-blue-072:      #2B2C84; /* [B1] Pantone Blue 072C, RGB 43/44/132 */
  --psb-orange-172:    #EA5614; /* [B1] Pantone 172C,  RGB 234/86/20 */
  --psb-grey-431:      #646872; /* [B1] Pantone 431,   RGB 100/104/114 */
  --psb-khaki-5753:    #4E621C; /* [B1] Pantone 5753C, RGB 78/98/28 */

  /* Поверхности */
  --color-canvas:      #F8F8FC; /* [B4] body фон сайта */
  --color-surface:     #FFFFFF; /* [B1] белый */
  --color-surface-2:   #F0F0F7; /* [B4] плашки, hover строк */
  --color-surface-3:   #E6E6EF; /* [B4] pressed строк, disabled фон */

  /* Линии */
  --color-line:        #E6E6EF; /* [B4] волосяные разделители, 1.27:1, декоративные */
  --color-line-strong: #C7C7D9; /* [B4] границы карточек */
  --color-control-border: #8D8DA6; /* [B4] граница полей ввода, 3.23:1 с белым: SC 1.4.11 */

  /* Текст */
  --color-ink:         #3E3E59; /* [B4] основной, 10.30:1 на белом, 9.73:1 на canvas */
  --color-ink-2:       #5C5C73; /* [B4] вторичный, 6.49:1 на белом, 5.73:1 на surface-2 */
  --color-ink-3:       #646872; /* [B1] серый 431, метаданные, 5.58:1 */
  --color-ink-disabled:#8D8DA6; /* [B4] только неактивное: SC 1.4.3 исключение для inactive */
  --color-on-accent:   #FFFFFF;

  /* Действие */
  --color-accent:          var(--psb-blue-072); /* 11.69:1 с белым */
  --color-accent-hover:    #22236B; /* [Calc] -20% L, 13.81:1 */
  --color-accent-pressed:  #1A1B55; /* [Calc] -35% L, 15.77:1 */
  --color-accent-tint:     #EDEDF7; /* [Calc] фон выбранного; синий на нём 10.05:1 */
  --color-evidence-bg:     #E4E4F3; /* [Calc] подсветка фрагмента; ink на нём 8.19:1 */
  --color-focus:           var(--psb-blue-072);

  /* Статусы */
  --color-grounded:        var(--psb-khaki-5753); /* 6.80:1 */
  --color-grounded-bg:     #EEF2E4; /* [Calc]; хаки на нём 5.98:1 */
  --color-attention:       var(--psb-orange-172); /* не-текст: полосы, точки; 3.60:1 */
  --color-attention-text:  #9A3A0E; /* [Calc] 7.03:1 на белом, 6.30:1 на bg */
  --color-attention-bg:    #FDF0E9; /* [Calc] */
  --color-neutral-status:  var(--psb-grey-431); /* 5.58:1 */
  --color-neutral-bg:      #F0F0F7; /* [B4] */
  --color-info:            var(--psb-blue-072);
  --color-info-bg:         #EDEDF7;
  --color-danger:          #BB3E45; /* [B4] ошибки форм сайта, 5.40:1 */
  --color-danger-bg:       #FBECEC; /* [Calc]; danger на нём 4.71:1 */
  --color-danger-hover:    #A1343A; /* [Calc] белый на нём 6.85:1 */
  --color-danger-pressed:  #8A2C31; /* [Calc] белый на нём 8.45:1 */

  /* Оверлеи */
  --color-scrim:           rgba(29, 30, 74, 0.32); /* [Calc] от #2B2C84 */
}
```

### 2.2. Тёмная тема (`@media (prefers-color-scheme: dark)`)

Принцип HIG: «The color palette in Dark Mode includes dimmer background colors and brighter foreground colors» и «Soften the color of white backgrounds». Тёмные поверхности строятся от синего 072C, а не от чистого чёрного, чтобы сохранить бренд и избежать «неонового» контраста.

| Токен | Значение | Контраст | Источник |
|---|---|---|---|
| `--color-canvas` | `#0E0F22` | | [Calc] от 072C |
| `--color-surface` | `#12132B` | | [Calc] |
| `--color-surface-2` | `#1B1C3A` | | [Calc] |
| `--color-surface-3` | `#25264A` | | [Calc] |
| `--color-line` | `#2C2D52` | | [Calc] |
| `--color-control-border` | `#6E6F8F` | 3.76:1 к surface (SC 1.4.11) | [Calc] |
| `--color-ink` | `#E8E8F2` | 14.96:1 | [Calc] |
| `--color-ink-2` | `#B4B4CC` | 8.96:1 | [Calc] |
| `--color-accent` | `#A9AAF0` | 8.40:1 к surface; текст на нём `#12132B` 8.40:1 | [Calc] осветлённый 072C. Не `#8D87FF` из логотипа: тот фиолетовее и уводит в «AI purple» |
| `--color-evidence-bg` | `#25264A` + линия accent | | [Calc] |
| `--color-grounded` | `#A8C46A` | 9.33:1 | [Calc] осветлённый 5753C |
| `--color-attention-text` | `#FF8A4C` | 7.79:1 | [Calc] осветлённый 172C |
| `--color-danger` | `#F08A90` | 7.58:1 | [Calc] |

Проверка обеих тем обязательна: HIG Accessibility «make sure to check the minimum contrast in both light and dark appearances».

### 2.3. Повышенный контраст

`@media (prefers-contrast: more)`: `--color-ink-2` заменяется на `--color-ink`, `--color-line` на `--color-control-border`, все бейджи получают границу 1px цветом текста. HIG Accessibility: «If your app doesn't provide this minimum contrast by default, ensure it at least provides a higher contrast color scheme when the system setting Increase Contrast is turned on».

### 2.4. Правила контраста

- Текст меньше 24px обычного начертания или меньше 18.66px жирного (700): не ниже 4.5:1. Начертание 600 мы не считаем жирным в смысле WCAG и проверяем по порогу 4.5:1 ([SC 1.4.3](https://www.w3.org/TR/WCAG22/#contrast-minimum), HIG Accessibility 4.5:1). Цель для основного текста 7:1 и выше: HIG Dark Mode «strive for a contrast ratio of 7:1, especially in small text». Основной текст `#3E3E59` даёт 10.30:1.
- Границы полей, фокус, иконки-носители смысла: не ниже 3:1 ([SC 1.4.11](https://www.w3.org/TR/WCAG22/#non-text-contrast)). Поэтому граница поля `#8D8DA6`, а не `#C7C7D9` (1.67:1).
- Оранжевый 172C никогда не цвет текста меньше 24px.

---

## 3. Типографика: токены и шкала

### 3.1. Семейства

```css
:root {
  --font-ui: "Golos Text", Verdana, system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-source: "PT Serif", Georgia, "Times New Roman", serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
```

Подключение: `next/font/google` с `subsets: ["cyrillic", "latin"]`, `display: "swap"`, веса Golos Text 400/500/600, PT Serif 400/400 italic/700. Verdana во втором слоте прямо разрешена гайдом ПСБ [B1 02.12].

### 3.2. Шкала (desktop; mobile в 3.3)

Базовый кегль 16px. HIG Typography даёт для macOS default 13pt, minimum 10pt, для iOS default 17pt, minimum 11pt. Мы работаем в браузере на десктопе с длинным чтением, поэтому основной текст ближе к iOS-значению (16), а мелкий не ниже 12 (выше минимума macOS с запасом под кириллицу).

| Токен | Гарнитура | Размер / интерлиньяж | Вес | Трекинг | Где |
|---|---|---|---|---|---|
| `type-title-1` | UI | 24 / 32 | 600 | 0 | Заголовок пустого экрана, заголовок документа в просмотрщике |
| `type-title-2` | UI | 20 / 28 | 600 | 0 | Заголовок панели «Источники», заголовок модального окна |
| `type-headline` | UI | 17 / 24 | 600 | 0 | Первое предложение ответа (вывод), заголовки баннеров |
| `type-body` | UI | 16 / 26 | 400 | 0 | Текст ответа, сообщение пользователя |
| `type-body-strong` | UI | 16 / 26 | 600 | 0 | Выделение в ответе |
| `type-source` | Source | 17 / 28 | 400 | 0 | Цитата в карточке источника, текст документа в просмотрщике |
| `type-source-sm` | Source | 15 / 24 | 400 | 0 | Цитата в свёрнутой карточке |
| `type-control` | UI | 15 / 20 | 500 | 0.005em | Подписи кнопок, поле ввода, пункты меню |
| `type-callout` | UI | 14 / 20 | 400 | 0 | Тексты баннеров, «Чего не хватает» |
| `type-label` | UI | 14 / 20 | 500 | 0 | Бейджи статуса, заголовки групп |
| `type-meta` | UI | 13 / 18 | 400 | 0.01em | Редакция, дата, номер пункта, время, подсказка клавиш |
| `type-chip` | UI | 13 / 16 | 500 | 0 | Чип ссылки «[1]» внутри текста, `tabular-nums` |
| `type-micro` | UI | 12 / 16 | 500 | 0.01em | Только счётчики (например «4» у вкладки). Не для предложений |

Ниже 12px текст запрещён. Каждая ступень отличается от соседней минимум на 1 шаг веса или 2px размера; HIG: «Adjust font weight, size, and color as needed to emphasize important information».

### 3.3. Адаптация

- < 768px: `type-title-1` 22/28, `type-body` 16/24, `type-source` 16/26. Основной кегль не уменьшается: HIG «Use font sizes that most people can read easily».
- Масштаб браузера до 200% без потери контента и без горизонтальной прокрутки при 320 CSS px ([SC 1.4.4](https://www.w3.org/TR/WCAG22/#resize-text), [SC 1.4.10 Reflow](https://www.w3.org/TR/WCAG22/#reflow)). Все размеры в `rem`.
- [SC 1.4.12 Text Spacing](https://www.w3.org/TR/WCAG22/#text-spacing): верстка выдерживает межстрочный 1.5, межбуквенный 0.12em, межсловный 0.16em без обрезки. Значит, никаких фиксированных высот у текстовых контейнеров.
- HIG «Keep text truncation to a minimum»: названия документов переносятся до 2 строк, затем многоточие плюс полный текст в `title` и в просмотрщике.

---

## 4. Пространство: 4/8-шкала

Шаг 4px, ритм 8px. Совпадает с практикой IBM Carbon (2x grid, шаги 2/4/8/12/16/24/32/40/48) ([carbondesignsystem.com](https://carbondesignsystem.com/elements/spacing/overview/)) и Material 3 (4dp baseline). Произвольные значения запрещены (unslop: «Arbitrary values, like mt-[13px] → steps on the 4px scale»).

| Токен | px | Типичное применение |
|---|---|---|
| `space-1` | 4 | Иконка ↔ текст в бейдже, зазор фокус-кольца (2) + толщина (2) |
| `space-2` | 8 | Иконка ↔ подпись в кнопке, между чипами, внутри строки метаданных |
| `space-3` | 12 | Вертикальный padding кнопки 44px (12 + 20 + 12), padding бейджа по горизонтали 8-12 |
| `space-4` | 16 | Горизонтальный padding кнопок и полей, padding карточки источника |
| `space-5` | 20 | Padding баннеров |
| `space-6` | 24 | Между абзацами ответа и списком оснований, padding панелей |
| `space-8` | 32 | Между репликами в ленте |
| `space-10` | 40 | Отступ ленты от композера |
| `space-12` | 48 | Верхний отступ пустого экрана |
| `space-16` | 64 | Крупные разрывы на пустом экране |

Правило близости (гештальт): внутри группы отступ меньше, чем между группами, минимум в 1.5 раза. HIG Layout: «Group related items to clearly express related information or functions».

Расстояние между соседними интерактивными элементами не меньше 8px. HIG Accessibility: «Consider spacing between controls as important as size... it works well to add about 12 points of padding around elements that include a bezel. For elements without a bezel, about 24 points» (скриншот `refs/01-apple-hig-accessibility-control-sizes.png`). В плотном интерфейсе: 8px между кнопками с рамкой внутри одной группы, 12px между группами, 24px вокруг безрамочных иконок-кнопок, если их визуальный размер меньше 44.

---

## 5. Размеры контролов и зоны нажатия

Опорные нормы:
- HIG Buttons: «a button needs a hit region of at least 44x44 pt... to ensure that people can select it easily, whether they use a fingertip, a pointer...» (`refs/03-apple-hig-buttons-hit-region-44pt.png`).
- HIG Accessibility, таблица Mobility: iOS/iPadOS default 44x44, minimum 28x28; macOS default 28x28, minimum 20x20 (`refs/01-...`).
- WCAG 2.2 [SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) AA: 24x24 CSS px или достаточный отступ; исключение «Inline» для целей внутри предложения. [SC 2.5.5](https://www.w3.org/TR/WCAG22/#target-size-enhanced) AAA: 44x44.
- Закон Фиттса: время наведения растёт с расстоянием и падает с размером цели ([NN/g, Fitts's Law](https://www.nngroup.com/articles/fitts-law/)).

Решение: три класса контролов.

| Класс | Визуальная высота | Зона нажатия | Где | Обоснование |
|---|---|---|---|---|
| L (основной) | 44 | 44x44 минимум | Отправка «Спросить», primary/secondary кнопки, поле ввода (мин. 44), строки списка источников (56), пункты истории (44), кнопки баннеров | HIG 44pt; AAA 2.5.5; самые частые и ответственные действия |
| M (плотный) | 32 | 44 по высоте за счёт прозрачного `::before` с `inset: -6px 0`, если сосед не ближе 8px; иначе 32 | Иконки-кнопки в шапке ответа («Копировать», «Повторить»), вкладки, переключатели в просмотрщике | HIG macOS default 28 ≤ 32; WCAG 2.5.8 AA выполнен с запасом |
| S (в строке текста) | 24 | 24x24 минимум (`min-width: 24px; min-height: 24px`) | Чип ссылки «[1]» внутри абзаца ответа | WCAG 2.5.8 AA, исключение «Inline». Каждая такая ссылка дублируется строкой 56px в списке оснований и в панели источников, то есть у пользователя всегда есть цель класса L |

Курсор: `cursor: pointer` у всех кликабельных элементов, включая кнопки. Конвенция настольных ОС (`default` у кнопок) уступает привычке веба и сайта банка; решение принято один раз и не меняется по компонентам.

---

## 6. Сетка и раскладка

### 6.1. Каркас рабочего места (desktop ≥ 1280px)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Шапка 56px: логотип ПСБ | Юридический ассистент · База: 21 документ    [?]  │
├────────────┬───────────────────────────────────────┬─────────────────────────┤
│ История    │ Лента диалога                          │ Панель «Источники»      │
│ 264px      │ fluid, колонка текста max 680px        │ 400px (min 360)         │
│ сворачива- │ по центру, поля 32px                   │ → 640px в режиме        │
│ ется в     │                                        │   «Документ»            │
│ 0 (drawer) │ Композер прилип к низу, max 680px      │                         │
└────────────┴───────────────────────────────────────┴─────────────────────────┘
```

| Зона | Ширина | Почему |
|---|---|---|
| История | 264px; скрывается кнопкой; < 1280 скрыта по умолчанию | HIG Sidebars: «Consider letting people hide the sidebar»; «show no more than two levels of hierarchy». История вторична по отношению к доказательствам |
| Лента | Остаток; текстовая колонка max 680px | 60-75 знаков в строке при 16px Golos Text (Baymard; Butterick 45-90) |
| Источники | 400px, ресайз мышью 360-640 | Цитата 17px PT Serif даёт около 45 знаков в строке при 400px, что достаточно для фрагмента; при открытии документа панель расширяется до 640 (около 70 знаков) |

Референсы структуры: `refs/14-pinterest-documentation-page.png` (левое дерево, читаемая колонка, правый контекст), `refs/15-pinterest-document-editor.png` (документ + боковая панель), `refs/16-pinterest-transcript-page-playbook.png` (лента реплик + панель деталей). Берём только структуру и плотность; фиолетовые акценты и скругления этих концептов не берём.

### 6.2. Брейкпоинты

| Диапазон | История | Лента | Источники | Документ |
|---|---|---|---|---|
| ≥ 1440 | Открыта | Fluid | 400 (или 640 с документом) | В панели справа |
| 1280-1439 | Открыта | Fluid | 400 | Панель 640, лента сжимается (min 560) |
| 1024-1279 | Drawer по кнопке | Fluid | 360 | Документ поверх ленты как правый лист 640 с затемнением |
| 768-1023 | Drawer | 100% | Drawer справа по кнопке «Источники (N)» | Полноэкранный лист |
| < 768 | Drawer | 100% | Нижний лист (bottom sheet) 85% высоты | Полноэкранный лист |

Минимальная ширина окна, при которой показываются три колонки: 1280. HIG Windows: «Choose a minimum and maximum size for each window» и HIG Layout «Design a layout that adapts gracefully and consistently».

### 6.3. Вертикальный ритм

Базовая линия 4px. Высоты строк кратны 4 (16, 20, 24, 28, 32), кроме двух осознанных исключений: 18 (`type-meta`) и 26 (`type-body`), выбранных ради читаемости длинного текста. Отступы вокруг них кратны 4.

---

## 7. Форма: радиусы, линии, возвышение

### 7.1. Радиусы

| Токен | px | Где | Почему |
|---|---|---|---|
| `radius-xs` | 2 | Подсветка фрагмента в документе | Выглядит как маркер, не как карточка |
| `radius-sm` | 4 | Кнопки, поля, бейджи, чипы | Совпадает с `.btn{border-radius:4px}` ПСБ [B4] |
| `radius-md` | 8 | Карточки источников, баннеры, композер, меню | Плотный рабочий инструмент |
| `radius-lg` | 12 | Модальные окна, нижний лист (верхние углы) | Только крупные плавающие поверхности |

Запрещены радиусы 16+ у карточек и `999px` у кнопок (unslop «candy radii»).

### 7.2. Линии

1px `--color-line` между зонами каркаса и между репликами-ответами; 1px `--color-line-strong` у карточек; 1px `--color-control-border` у полей. Цитата: левая линия 2px `--color-accent`. Баннер-предупреждение: левая полоса 4px статусного цвета.

### 7.3. Возвышение

Глубина в основном тоном поверхности и линией, тени только у плавающих слоёв (unslop: «depth from surface steps and hairlines»).

| Уровень | Тень | Где |
|---|---|---|
| 0 | нет | Лента, панели, карточки |
| 1 | `0 1px 2px rgba(29,30,74,.08)` | Композер, прилипшая шапка ответа при скролле |
| 2 | `0 4px 16px rgba(29,30,74,.12)` | Меню, поповер ссылки, тултип |
| 3 | `0 12px 32px rgba(29,30,74,.18)` + scrim | Модальное окно, лист документа на узких экранах |

Цвет тени от синего 072C, не чёрный и не цветной; свечения запрещены.

### 7.4. Z-index

`base 0`, `sticky 10` (шапка, композер), `drawer 30`, `popover 40`, `modal 50`, `toast 60`.

---

## 8. Состояния взаимодействия

HIG Buttons: «Always include a press state for a custom button. Without a press state, a button can feel unresponsive». HIG Focus and Selection: «Indicate focus using visual appearances that are consistent with the platform». WCAG [2.4.7 Focus Visible](https://www.w3.org/TR/WCAG22/#focus-visible), [2.4.11 Focus Not Obscured (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html), [2.4.13 Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html) (AAA, используем как цель).

### 8.1. Универсальная модель

| Состояние | Визуальное правило | Токены |
|---|---|---|
| Default | Как в спецификации компонента | |
| Hover (только `@media (hover: hover)`) | Заливка на одну ступень темнее, либо фон `surface-2` у безрамочных | `accent-hover`, `surface-2` |
| Pressed (`:active`) | Ещё на ступень темнее, без сдвига и без масштабирования | `accent-pressed`, `surface-3` |
| Focus-visible | Кольцо 2px `--color-focus` + зазор 2px цвета фона (`outline: 2px solid; outline-offset: 2px`). Площадь кольца по периметру не меньше 2 CSS px, контраст кольца к фону 11.69:1 | `focus` |
| Selected / current | Фон `accent-tint`, текст `accent`, `aria-current` / `aria-selected` | `accent-tint` |
| Disabled | Фон `surface-3`, текст `ink-disabled`, без тени, `cursor: not-allowed`, `aria-disabled="true"` если элемент должен оставаться фокусируемым для объяснения | `surface-3`, `ink-disabled` |
| Loading | Подпись сохраняется, слева спиннер 16px, ширина кнопки фиксируется (не прыгает), `aria-busy="true"`, повторное нажатие игнорируется | |
| Error | Граница 1px `danger` + текст ошибки под элементом с иконкой, связка `aria-describedby` | `danger` |

Почему не прозрачные «state layers» Material 3 (hover 8%, focus 10%, pressed 10%, [m3.material.io](https://m3.material.io/foundations/interaction/states/state-layers)): на тинтах статусов полупрозрачный слой даёт непредсказуемый контраст. Используем явные ступени с проверенным контрастом; идея «одна ступень на состояние» взята из M3.

### 8.2. Движение

| Токен | Значение | Где |
|---|---|---|
| `motion-fast` | 120ms `cubic-bezier(.2,0,0,1)` | Hover, pressed, фокус |
| `motion-base` | 200ms | Раскрытие карточки, появление бейджа |
| `motion-panel` | 240ms | Выезд панели и листа документа |
| `motion-scroll` | `scroll-behavior: smooth` 300ms | Прокрутка документа к фрагменту |

`@media (prefers-reduced-motion: reduce)`: все переходы 0ms, прокрутка мгновенная, спиннер заменяется статичным текстом стадии. HIG Accessibility: «Be cautious with fast-moving and blinking animations»; «Replacing transitions in x-, y-, and z-axes with fades to avoid motion».

Запрещено: «печатание» ответа по буквам с курсором-миганием, пульсирующие орбы, shimmer-градиенты дольше 1 секунды на месте контента, который уже пришёл.

---

## 9. Доступность: обязательный минимум

| Требование | Реализация |
|---|---|
| [SC 4.1.3 Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | Лента `role="log" aria-live="polite"`; стадии загрузки в отдельном `role="status"`; системная ошибка `role="alert"` |
| Клавиатура (HIG Accessibility: «Let people use the keyboard alone») | Tab-порядок: шапка → история → лента → композер → источники. `Enter` отправка, `Shift+Enter` перенос, `Esc` закрывает документ/лист и возвращает фокус на вызвавший чип, стрелки ↑/↓ переводят фокус между карточками в панели источников (roving tabindex), `/` фокус в композер, если фокус не в поле ввода. `Alt+1..9` не используем: в Chrome и Firefox на Linux это переключение вкладок |
| Фокус не перекрыт (2.4.11) | `scroll-padding-bottom` ленты равен высоте композера + 16px |
| Не только цвет (1.4.1, HIG Color) | Каждый статус: иконка + текст; подсветка фрагмента: фон + линия + `<mark>` |
| Скринридер | Чип ссылки: `aria-label="Источник 1: Регламент согласования договоров ред. 2025, пункт 2.2"`; бейдж статуса начинает каждую реплику ассистента в DOM |
| Язык | `<html lang="ru">` |

---

## 10. Токены в Tailwind (замена наследия)

```ts
// tailwind.config.ts (фрагмент): заменить brand/platinum/mint/lavender/peach/rose/cyanSoft
colors: {
  accent: { DEFAULT: "var(--color-accent)", hover: "var(--color-accent-hover)", pressed: "var(--color-accent-pressed)", tint: "var(--color-accent-tint)" },
  canvas: "var(--color-canvas)", surface: { DEFAULT: "var(--color-surface)", 2: "var(--color-surface-2)", 3: "var(--color-surface-3)" },
  ink: { DEFAULT: "var(--color-ink)", 2: "var(--color-ink-2)", 3: "var(--color-ink-3)", disabled: "var(--color-ink-disabled)" },
  line: { DEFAULT: "var(--color-line)", strong: "var(--color-line-strong)", control: "var(--color-control-border)" },
  grounded: { DEFAULT: "var(--color-grounded)", bg: "var(--color-grounded-bg)" },
  attention: { DEFAULT: "var(--color-attention)", text: "var(--color-attention-text)", bg: "var(--color-attention-bg)" },
  neutralStatus: { DEFAULT: "var(--color-neutral-status)", bg: "var(--color-neutral-bg)" },
  danger: { DEFAULT: "var(--color-danger)", bg: "var(--color-danger-bg)" },
  evidence: "var(--color-evidence-bg)",
},
borderRadius: { xs: "2px", sm: "4px", md: "8px", lg: "12px" },
fontFamily: { ui: ["var(--font-ui)"], source: ["var(--font-source)"], mono: ["var(--font-mono)"] },
```

Удалить из проекта: `borderRadius.card: 28px`, `pill: 999px`, `boxShadow.soft`, `fontFamily.sans: Manrope`, каталог `public/icons/3d/`.
