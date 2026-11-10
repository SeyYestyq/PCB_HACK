# Опись пакета PSB_Legal_Assistant (раскладка по ролям)

Собран 10 ноября 2026, около 07:23 мск (Europe/Moscow), на основе документации v1.6.
Дубли одного и того же исходного файла в разных папках имеют одинаковый SHA256.
Исходные документы не изменялись. Новые файлы: README ролей, этот манифест, официальный кейс в `01_common/official_case/`.

## Сводка

- Файлов в исходном архиве v1.6: 81
- Из них присутствуют в этом пакете (имя + SHA256): 81
- Пропущены: 0
- Расхождение SHA256 (файл есть, содержимое другое): 0
- Уникальных исходных файлов v1.6, попавших в пакет: 81
- Всего файлов в распакованном дереве (включая дубли, README, манифест и официальный кейс): 127

## Дерево папок

| Папка | Файлов (включая README и этот манифест) |
|---|---:|
| `00_START_HERE/` | 4 |
| `01_common/` | 29 |
| `02_frontend/` | 37 |
| `03_backend_rag/` | 27 |
| `04_kb_eval/` | 15 |
| `05_review_and_tests/` | 15 |

Проверка: все 81 файл архива v1.6 присутствуют, SHA256 совпадают.

## Файлы

| Путь в этом пакете | Роль | Назначение | Байты | SHA256 | Источник v1.6 |
|---|---|---|---:|---|---|
| `00_START_HERE/INDEX.md` | старт / все роли | Оглавление пакета v1.6, порядок чтения и сквозные идентификаторы | 16554 | `93a1c557df00b3ed47fb78ef007ede2994d56d1c206c8180be325c367090929d` | `docs/INDEX.md` |
| `00_START_HERE/README.md` | старт / все роли | Вход в пакет: структура, порядок работы, что агенты не сделают сами | 6973 | `435364370a6319868f010966bfc2557064739ac9a41a07e76767b20b6dab92b9` | новый файл пакета |
| `00_START_HERE/STATUS.md` | старт / все роли | Журнал проходов пакета, открытые вопросы и раздел «Что делать команде сейчас» | 48101 | `1c6b268544542d6b2940459dc0ed1ba5bca34cf1261dbc993d63a1122f8aa45d` | `STATUS.md` |
| `01_common/README.md` | общее | Краткий путеводитель по папке: порядок чтения, зона ответственности, передачи, критерии готовности | 2318 | `521754e7e9b87deb127cd4ae82b4a431127addfe3ea03197255028f27461a2b6` | новый файл пакета |
| `01_common/docs/01-product/01-problem-and-audience.md` | общее | Проблема из кейса, ЦА, JTBD J1-J10, анти-персоны | 17726 | `9ef84dad0937581668d61831aa1b54769783b9be692d3ed533184081eec48886` | `docs/01-product/01-problem-and-audience.md` |
| `01_common/docs/01-product/02-tz-complete.md` | общее | Сквозное ТЗ: контракт AnswerV2, F1-F17, редакции E1-E12, SEC, eval | 47464 | `cb4c535f80184a1f858c452d47bc1ce8b334ba78f59c8a458ad133fd00aaa6cd` | `docs/01-product/02-tz-complete.md` |
| `01_common/docs/01-product/03-tz-roles-3-people.md` | общее | Три роли, задачи с DoD, интерфейсы, ритм работы | 19233 | `c3b237b0432406f3987be850306832ef0f95776aac17b25db21f6ef58c8e9fc5` | `docs/01-product/03-tz-roles-3-people.md` |
| `01_common/docs/01-product/07-handoffs-and-interfaces.md` | общее | Передачи H-01..H-12, протокол контракта, RACI, эскалация | 7578 | `962f49fb66061018085a61668d809f9a619fb1c15ed668d0c282e366f3b34c5e` | `docs/01-product/07-handoffs-and-interfaces.md` |
| `01_common/docs/02-architecture/01-system-architecture.md` | общее | Архитектура системы, инварианты A1-A5, API, режимы отказа | 27759 | `ba3c9dce20a48745f578efc94f863ceccac90651383b74e5c8578c1d79c9d0b5` | `docs/02-architecture/01-system-architecture.md` |
| `01_common/docs/02-architecture/02-stack-and-decisions.md` | общее | ADR-01..12: стек, хранилище, поиск, реранкер, фреймворки | 20268 | `7f4b0fb3d22efd07f16af69a5622f11a560c1d909d6aaf4a09f3bbb2bda52c3e` | `docs/02-architecture/02-stack-and-decisions.md` |
| `01_common/docs/02-architecture/03-data-model-and-kb.md` | общее | Модель данных и база: 21 файл, аномалии KB-A1..A7, индекс | 22630 | `44679e483878cea9d5d867ad5fdb2448d6748d8d6723001ceaa82fdc6e643cd0` | `docs/02-architecture/03-data-model-and-kb.md` |
| `01_common/docs/02-architecture/04-security.md` | общее | Безопасность: угрозы T1-T12, инъекции, секреты, fail-closed | 17729 | `5e0374b31fc27c947886b5eddb933620a407187130933dedc39381f5b9beaf95` | `docs/02-architecture/04-security.md` |
| `01_common/docs/03-analogs/01-analogs-deep-dive.md` | общее | Разбор аналогов (банковские и legal AI) по 8 измерениям | 24364 | `841b17e7b79ce5fb07287583d143e6b2989c2aea9508ac238f1f18ceae6c71fc` | `docs/03-analogs/01-analogs-deep-dive.md` |
| `01_common/docs/03-analogs/02-what-we-take-and-reject.md` | общее | 22 паттерна: берём, адаптируем или отвергаем | 11002 | `9aaf40d6e18579c2fc8d7ba2ccc5f8af9bb0c0a96502f29b836a9f649ddee09b` | `docs/03-analogs/02-what-we-take-and-reject.md` |
| `01_common/docs/04-brand/07-decision-justifications.md` | общее | Обоснования решений BJ-01..09 с контраргументами | 20401 | `5d8e1e74226486e4f6f8ff1d7ba7d9937d7164fcdf67eb080d0889a21b96646f` | `docs/04-brand/07-decision-justifications.md` |
| `01_common/docs/05-rag/01-rag-deep-dive.md` | общее | Глубокий разбор RAG и список дефектов D1-D28 | 64483 | `8eeb0b0308780bb9241c6ec8475b6ac5f74e6ec720c9f13005a58c5373986a67` | `docs/05-rag/01-rag-deep-dive.md` |
| `01_common/docs/06-nodes/00-overview.md` | общее | Реестр узлов ND1-ND8, владельцы, потоки, сводка as-is | 19425 | `9d78e59cbc795f0bd973152df4c143f92cd25f26efce3d23a51938b6c31e4dcb` | `docs/06-nodes/00-overview.md` |
| `01_common/docs/06-nodes/07-api-contract-and-submission.md` | общее | ND7: контракт API, SSE, порты, solution.py, Docker, сабмит | 20318 | `82071a3531dcc9dd698781111ea061dd8d7cf0c604f96defbc7581c36127f284` | `docs/06-nodes/07-api-contract-and-submission.md` |
| `01_common/docs/99-sources.md` | общее | Реестр источников K-*, S-01..S-152, A-*, B1-B5 и неоткрывшихся ссылок | 51785 | `924fdc56c626ea40ecf6c08eabf728d1ac4edda2ed46576582dbf17aadb996e6` | `docs/99-sources.md` |
| `01_common/official_case/PSB_case.pdf` | общее | Официальный кейс хакатона (PDF), источник истины по условиям | 3049049 | `fc408872996fe3db396acbcdebd03628fd153153108c662f137a198184ed506f` | не входил в zip v1.6; файл `/workspace/pcb/PSB_case.pdf` |
| `01_common/official_case/PSB_case.txt` | общее | Текстовая выгрузка официального кейса | 46882 | `414e7ad78012de155240083a7e1309485b0ce37d3549c42e73eeef73cd88ee77` | не входил в zip v1.6; файл `/workspace/pcb/PSB_case.txt` |
| `01_common/references/analogs/cocounsel_legal_product.png` | общее | Снимок аналога CoCounsel | 156302 | `6d001b9b2f21f08ee30e8d2b3e22163acbf7c73f665e8586554f32f714bbc670` | `references/analogs/cocounsel_legal_product.png` |
| `01_common/references/analogs/garant_iskra_landing.jpg` | общее | Снимок лендинга ИСКРА (Гарант) | 333233 | `8227c3b180614fe1091f57afc9f18db0483c57926f1eefcff965fff98ff9b663` | `references/analogs/garant_iskra_landing.jpg` |
| `01_common/references/analogs/garant_iskra_lt.jpg` | общее | Снимок ИСКРА (Гарант), доп. кадр | 436797 | `57dc7c8c75fa02838042f6700f1fe74721a90add93eb51ab88e4ca1dd602520b` | `references/analogs/garant_iskra_lt.jpg` |
| `01_common/references/analogs/harvey_biglaw_sources_og.jpg` | общее | Снимок Harvey: источники | 93452 | `f1c72b2d91e256e09883a115f5f1960870cd56a41a2c85648c530928778587e1` | `references/analogs/harvey_biglaw_sources_og.jpg` |
| `01_common/references/analogs/harvey_home_og.jpg` | общее | Снимок главной Harvey | 17395 | `9f6aebe0daaa92625af11032da78665ed77e31eaedddea720ed941f4b763f7fc` | `references/analogs/harvey_home_og.jpg` |
| `01_common/references/analogs/harvey_knowledge_og.jpg` | общее | Снимок Harvey Knowledge | 24463 | `c47c98abc3369fe35a59ef48e133d73b56f3395f75cd9e8d4fa025656e83e3a7` | `references/analogs/harvey_knowledge_og.jpg` |
| `01_common/references/analogs/harvey_vault_og.jpg` | общее | Снимок Harvey Vault | 19721 | `7c10b6d9a8948d10eb9f547ecd217968e1ff59b1667e79449bfe524a7792b6a3` | `references/analogs/harvey_vault_og.jpg` |
| `01_common/references/analogs/legora_og.png` | общее | Снимок аналога Legora | 13913 | `85d02af5d0490941a7d417556ea328cd50ad03a41bf3ef45a63887c7eb549155` | `references/analogs/legora_og.png` |
| `01_common/references/analogs/luminance_og.jpg` | общее | Снимок аналога Luminance | 205450 | `091743b78877abee894bd86a92dcf07e2a12466e23acd188f7e586200c1fab54` | `references/analogs/luminance_og.jpg` |
| `01_common/references/analogs/neurolegal_og.jpg` | общее | Снимок аналога НейроЮрист | 398793 | `dcab772c596ffaa80061e8fdfb062343cdb5ba0d162f3c4814b1401e1f008d38` | `references/analogs/neurolegal_og.jpg` |
| `01_common/references/analogs/spellbook_og.png` | общее | Снимок аналога Spellbook | 312421 | `1a879887b6f69dec05e14fed4e75cef678037b31487efc95e6cf8700a2c39642` | `references/analogs/spellbook_og.png` |
| `02_frontend/README.md` | роль 2, фронтенд | Краткий путеводитель по папке: порядок чтения, зона ответственности, передачи, критерии готовности | 3935 | `4b82972fc3acc26610c622f75943e43ecbd0cc411762effffe221275cfb63103` | новый файл пакета |
| `02_frontend/docs/01-product/03-tz-roles-3-people.md` | роль 2, фронтенд | Три роли, задачи с DoD, интерфейсы, ритм работы | 19233 | `c3b237b0432406f3987be850306832ef0f95776aac17b25db21f6ef58c8e9fc5` | `docs/01-product/03-tz-roles-3-people.md` |
| `02_frontend/docs/01-product/05-role-2-frontend.md` | роль 2, фронтенд | Карточки роли 2 (интерфейс): R2.1-R2.11 | 15761 | `db5c59bfdd0864b0343245c9d7d74ea0ab3c9e5e3531add58e446381c0ce7ace` | `docs/01-product/05-role-2-frontend.md` |
| `02_frontend/docs/01-product/07-handoffs-and-interfaces.md` | роль 2, фронтенд | Передачи H-01..H-12, протокол контракта, RACI, эскалация | 7578 | `962f49fb66061018085a61668d809f9a619fb1c15ed668d0c282e366f3b34c5e` | `docs/01-product/07-handoffs-and-interfaces.md` |
| `02_frontend/docs/01-product/08-tz-frontend-complete.md` | роль 2, фронтенд | Полное ТЗ роли 2: экраны S0-S12, кнопки K1-K10, элементы FE-* | 75047 | `befe8dd4d8f2649946ce8d7ccfb06ce1d84b8ab1853c093cc8acc90837dbce99` | `docs/01-product/08-tz-frontend-complete.md` |
| `02_frontend/docs/02-architecture/01-system-architecture.md` | роль 2, фронтенд | Архитектура системы, инварианты A1-A5, API, режимы отказа | 27759 | `ba3c9dce20a48745f578efc94f863ceccac90651383b74e5c8578c1d79c9d0b5` | `docs/02-architecture/01-system-architecture.md` |
| `02_frontend/docs/04-brand/01-brand-book.md` | роль 2, фронтенд | Брендбук продукта: цвет, тип, знак, голос, do/don't | 48882 | `214479f490693ca27a9664b61056678602b5a9469d79240eba09e7fa9e084952` | `docs/04-brand/01-brand-book.md` |
| `02_frontend/docs/04-brand/02-design-system.md` | роль 2, фронтенд | Дизайн-система: токены, сетка, радиусы, состояния, a11y | 32241 | `3d448b017467b04ab9ec8ef5efa0fa48cc6500563d6ea8ed5edb4acde7b81e16` | `docs/04-brand/02-design-system.md` |
| `02_frontend/docs/04-brand/03-components-and-copy.md` | роль 2, фронтенд | Компоненты и тексты: кнопки, композер, статусы, баннеры | 79804 | `b6f9ac176d455b0b302e66df7ba43944f026befbfd0f8ab71dc6abadbfe6d4b7` | `docs/04-brand/03-components-and-copy.md` |
| `02_frontend/docs/04-brand/04-screens-and-flows.md` | роль 2, фронтенд | Экраны S0-S12 и сценарии, матрица статус → экран | 40921 | `47466bc2ce3d1070cfe05289459046d09232ecfe3a8cc3e133354fd4aafceddf` | `docs/04-brand/04-screens-and-flows.md` |
| `02_frontend/docs/04-brand/05-anti-slop-and-trends.md` | роль 2, фронтенд | Отвергнутые и принятые UI-паттерны, чек-лист качества | 15883 | `6336d7fb28e2712e498d61b82f4e8142f4b577987d9b597d6937a1dc3b6755bb` | `docs/04-brand/05-anti-slop-and-trends.md` |
| `02_frontend/docs/04-brand/06-detail-spacing-type-motion-skeletons.md` | роль 2, фронтенд | Детальная спецификация отступов, типографики, движения, скелетонов | 146992 | `f0b4f792772bfef22ea8d17501a520b2e1c9acf1daf40df37721d66f7c3f5538` | `docs/04-brand/06-detail-spacing-type-motion-skeletons.md` |
| `02_frontend/docs/04-brand/07-decision-justifications.md` | роль 2, фронтенд | Обоснования решений BJ-01..09 с контраргументами | 20401 | `5d8e1e74226486e4f6f8ff1d7ba7d9937d7164fcdf67eb080d0889a21b96646f` | `docs/04-brand/07-decision-justifications.md` |
| `02_frontend/docs/06-nodes/08-frontend.md` | роль 2, фронтенд | ND8: фронтенд чата, композер, статусы, источники, ошибки | 13482 | `4e727984b3a2bb011ded92317eed658e30faeaa59d04eb76db2ff71e6f3468a3` | `docs/06-nodes/08-frontend.md` |
| `02_frontend/docs/07-tests/00-strategy.md` | роль 2, фронтенд | Стратегия тестов: слои, LLM, флаки, ритм, определение регрессии | 16225 | `c9a1675b6e82d5faf6ccb5ab11a42d46b235a81eab64db8f4ff5537b0bfb76c8` | `docs/07-tests/00-strategy.md` |
| `02_frontend/docs/07-tests/02-regression.md` | роль 2, фронтенд | Регрессионный каталог: дефекты, статусы, API, сабмит, UI, a11y | 36580 | `1c1b3bc1c61fec4ca01db130f2b4bc3e4cfd98999c4b89257010b2311a2f90fc` | `docs/07-tests/02-regression.md` |
| `02_frontend/docs/07-tests/03-unit-and-contract.md` | роль 2, фронтенд | Unit по модулям и контрактные тесты API/UI | 23515 | `94164bde50b7fe50eda18fa3ec0dc413f7f69c1018d68feb6e180ff459c4c9e5` | `docs/07-tests/03-unit-and-contract.md` |
| `02_frontend/docs/08-review/02-frontend-design-review.md` | роль 2, фронтенд | Ревью фронтенда и дизайна | 10354 | `6afe7c6daeab5dd75d1319ff967f17c359fcaaed1d81f97ded1021d15428257d` | `docs/08-review/02-frontend-design-review.md` |
| `02_frontend/pdf/PSB_Legal_Assistant_Brandbook.pdf` | роль 2, фронтенд | PDF брендбука продукта (собранный) | 313512 | `5bdf0bae195877f6b54c97f1a1ff30f9bd19c6c2c84ee03b7946bf9dd1e14dfd` | `pdf/PSB_Legal_Assistant_Brandbook.pdf` |
| `02_frontend/pdf/src/assets/hig-sizes.png` | роль 2, фронтенд | Иллюстрация размеров зон нажатия для брендбука | 190587 | `0dffe93954527b6ed6d51206fa9669d2c709d220954c0b5fffca904ecfe74feb` | `pdf/src/assets/hig-sizes.png` |
| `02_frontend/pdf/src/assets/psb-p-05.png` | роль 2, фронтенд | Иллюстрация из гайда ПСБ для брендбука | 49132 | `656ef16749ec28fff28ad022d1e145bb14a6a71d7e2119ed88a3e8d034b22932` | `pdf/src/assets/psb-p-05.png` |
| `02_frontend/pdf/src/assets/psb_logo.png` | роль 2, фронтенд | Знак ПСБ для брендбука | 20296 | `9cd92a3f87ae64e4d80a569978c99226c0ec9dca2f4c7671030a0300f94a806d` | `pdf/src/assets/psb_logo.png` |
| `02_frontend/pdf/src/brandbook.html` | роль 2, фронтенд | HTML-исходник брендбука | 171483 | `44ca455bfee45fd32c285bbe4303e564d56b8f148d81d7c6433734e5025d4e88` | `pdf/src/brandbook.html` |
| `02_frontend/pdf/src/build.py` | роль 2, фронтенд | Скрипт сборки PDF брендбука | 98193 | `37a864155d527d49b623425835822dfc29621ef94f94c7e9e8bdfe37bcb59bbd` | `pdf/src/build.py` |
| `02_frontend/pdf/src/style.css` | роль 2, фронтенд | Стили брендбука | 7164 | `8469f2cdf9719a9fc9b4c84fa87394283ea693ca4e8461495fb30c06a154d948` | `pdf/src/style.css` |
| `02_frontend/pdf/src/svg.py` | роль 2, фронтенд | Генерация SVG для брендбука | 28958 | `e9eaf11babb2656d4dafb4facf8ee1524885a320757284dd5fc0d6b1cb6a703f` | `pdf/src/svg.py` |
| `02_frontend/references/brand/PSB_BRAND_NOTES.md` | роль 2, фронтенд | Рабочие заметки по официальному гайду ПСБ | 3199 | `28d04dec837e175166e6d255611bab074b12673e6d3baacc0d1fd1b043d4aaef` | `references/brand/PSB_BRAND_NOTES.md` |
| `02_frontend/references/brand/PSB_Brandbook.pdf` | роль 2, фронтенд | Официальный брендбук ПСБ (сторонний PDF, не править) | 12695967 | `3e5664b1d4193a6a4255691fecf8f13a622b3443ded93dff65983d83c75e17b9` | `references/brand/PSB_Brandbook.pdf` |
| `02_frontend/references/brand/PSB_Brandbook.txt` | роль 2, фронтенд | Текстовая выгрузка официального гайда ПСБ | 183507 | `d8766e1c1501a9d5536e2ce2c44547c70e58697d6e40a441365ef7c7bdeec877` | `references/brand/PSB_Brandbook.txt` |
| `02_frontend/references/psb/MANIFEST.md` | роль 2, фронтенд | Опись снимков и файлов официального стиля ПСБ | 1972 | `07f19f5e045d14e28d2789c48141bebe61b71b715127c796c2d333cd191cacc3` | `references/psb/MANIFEST.md` |
| `02_frontend/references/psb/PSB_brandbook_logo.pdf` | роль 2, фронтенд | Официальный PDF логотипа ПСБ с сайта банка (не править) | 7011498 | `f6447d09cd52d18b15905b948221eca784442099e60022582c71997bfec74d4e` | `references/psb/PSB_brandbook_logo.pdf` |
| `02_frontend/references/psb/bb-p07-colors-07.png` | роль 2, фронтенд | Страница цветов из гайда ПСБ | 35842 | `8adc930f1b5b16d2eef18bcdadeee710a8c4b063e526dea390161889c88fcdad` | `references/psb/bb-p07-colors-07.png` |
| `02_frontend/references/psb/bb-p11-dont-11.png` | роль 2, фронтенд | Страница «как нельзя» из гайда ПСБ | 279196 | `2558588930ee2f34e17ca20e275c6d38e79664287bd47d04168a4692640e5939` | `references/psb/bb-p11-dont-11.png` |
| `02_frontend/references/psb/harvey-design.png` | роль 2, фронтенд | Референс оформления legal AI (Harvey) | 133820 | `690dc9a399a0d4686490fc962977851dad353f83059847e9c52af65606965aba` | `references/psb/harvey-design.png` |
| `02_frontend/references/psb/psbank-home.png` | роль 2, фронтенд | Снимок главной psbank.ru | 674467 | `5ea556c1b193411f3efd0daf2ae1376b1503d04e9ba53fd48b2814eb06b9e347` | `references/psb/psbank-home.png` |
| `02_frontend/references/psb/psbank-style.png` | роль 2, фронтенд | Снимок стиля psbank.ru | 381165 | `ca343b67d55c20f5d685e42788fc82c7cfa46852a0c92a75c3b41ff07135bca8` | `references/psb/psbank-style.png` |
| `02_frontend/tools/contrast.py` | роль 2, фронтенд | Проверка цветовых пар по WCAG 2.2 | 1540 | `1634cdfae466575238458f9b55172c0367706a74e39a14b890327e058ce59768` | `tools/contrast.py` |
| `03_backend_rag/README.md` | роль 1, ядро и RAG | Краткий путеводитель по папке: порядок чтения, зона ответственности, передачи, критерии готовности | 4232 | `02a87db66d1d0bf3b306fa36febdb23db460f963ec1aa79945e8fded48d3ca46` | новый файл пакета |
| `03_backend_rag/docs/01-product/03-tz-roles-3-people.md` | роль 1, ядро и RAG | Три роли, задачи с DoD, интерфейсы, ритм работы | 19233 | `c3b237b0432406f3987be850306832ef0f95776aac17b25db21f6ef58c8e9fc5` | `docs/01-product/03-tz-roles-3-people.md` |
| `03_backend_rag/docs/01-product/04-role-1-backend-rag.md` | роль 1, ядро и RAG | Карточки роли 1 (ядро/RAG): R1.1-R1.16 | 32212 | `48d35baaa2dc2d00e8e1831b139a93b87f703e99808a3af73752dff3970e1b14` | `docs/01-product/04-role-1-backend-rag.md` |
| `03_backend_rag/docs/01-product/07-handoffs-and-interfaces.md` | роль 1, ядро и RAG | Передачи H-01..H-12, протокол контракта, RACI, эскалация | 7578 | `962f49fb66061018085a61668d809f9a619fb1c15ed668d0c282e366f3b34c5e` | `docs/01-product/07-handoffs-and-interfaces.md` |
| `03_backend_rag/docs/01-product/09-tz-backend-complete.md` | роль 1, ядро и RAG | Полное ТЗ роли 1: модули, узлы ND1-ND7, solution.py, Docker, BE-* | 51120 | `ee36e0e64ccadf8d502a6ac2c7bf2b86c864a5f1bbb6cba773202fe64fe1c74e` | `docs/01-product/09-tz-backend-complete.md` |
| `03_backend_rag/docs/02-architecture/01-system-architecture.md` | роль 1, ядро и RAG | Архитектура системы, инварианты A1-A5, API, режимы отказа | 27759 | `ba3c9dce20a48745f578efc94f863ceccac90651383b74e5c8578c1d79c9d0b5` | `docs/02-architecture/01-system-architecture.md` |
| `03_backend_rag/docs/02-architecture/02-stack-and-decisions.md` | роль 1, ядро и RAG | ADR-01..12: стек, хранилище, поиск, реранкер, фреймворки | 20268 | `7f4b0fb3d22efd07f16af69a5622f11a560c1d909d6aaf4a09f3bbb2bda52c3e` | `docs/02-architecture/02-stack-and-decisions.md` |
| `03_backend_rag/docs/02-architecture/03-data-model-and-kb.md` | роль 1, ядро и RAG | Модель данных и база: 21 файл, аномалии KB-A1..A7, индекс | 22630 | `44679e483878cea9d5d867ad5fdb2448d6748d8d6723001ceaa82fdc6e643cd0` | `docs/02-architecture/03-data-model-and-kb.md` |
| `03_backend_rag/docs/02-architecture/04-security.md` | роль 1, ядро и RAG | Безопасность: угрозы T1-T12, инъекции, секреты, fail-closed | 17729 | `5e0374b31fc27c947886b5eddb933620a407187130933dedc39381f5b9beaf95` | `docs/02-architecture/04-security.md` |
| `03_backend_rag/docs/05-rag/01-rag-deep-dive.md` | роль 1, ядро и RAG | Глубокий разбор RAG и список дефектов D1-D28 | 64483 | `8eeb0b0308780bb9241c6ec8475b6ac5f74e6ec720c9f13005a58c5373986a67` | `docs/05-rag/01-rag-deep-dive.md` |
| `03_backend_rag/docs/05-rag/02-best-approaches-and-our-pipeline.md` | роль 1, ядро и RAG | Пайплайн S0-S19, инварианты I1-I10, бюджет L0-L4, статусы | 43585 | `4d819ceb8f1db9c7485a770d6d7376ce9a58652385370b293d470b51d61b7798` | `docs/05-rag/02-best-approaches-and-our-pipeline.md` |
| `03_backend_rag/docs/06-nodes/00-overview.md` | роль 1, ядро и RAG | Реестр узлов ND1-ND8, владельцы, потоки, сводка as-is | 19425 | `9d78e59cbc795f0bd973152df4c143f92cd25f26efce3d23a51938b6c31e4dcb` | `docs/06-nodes/00-overview.md` |
| `03_backend_rag/docs/06-nodes/01-ingest-and-parse.md` | роль 1, ядро и RAG | ND1: ингест, парсер, санитайзер | 19317 | `0a199465d846840022582335ea278dec13a517575b4309393343d5aeabc9443e` | `docs/06-nodes/01-ingest-and-parse.md` |
| `03_backend_rag/docs/06-nodes/02-index-and-retrieval.md` | роль 1, ядро и RAG | ND2: токенизация, BM25, dense, RRF, гейт | 16079 | `53d549f518aae5e258c0ff01a479c48bfe4cfb745ca16536f983027db57ec704` | `docs/06-nodes/02-index-and-retrieval.md` |
| `03_backend_rag/docs/06-nodes/03-request-intake-and-guards.md` | роль 1, ядро и RAG | ND3: вход запроса, история, лимиты, гарды | 13386 | `11f06250e6103be263d78c01b13671ee9af1a98267098df05149da2b3924a230` | `docs/06-nodes/03-request-intake-and-guards.md` |
| `03_backend_rag/docs/06-nodes/04-clarify-and-counterparty-catalog.md` | роль 1, ядро и RAG | ND4: понимание вопроса, каталог контрагентов, clarify | 19900 | `517da1d146df5a7544d4ea3561227e0843a98cd58eaf2ab748ebe9551d9e49f1` | `docs/06-nodes/04-clarify-and-counterparty-catalog.md` |
| `03_backend_rag/docs/06-nodes/05-editions-and-filters.md` | роль 1, ядро и RAG | ND5: редакции, допсоглашения, граничные даты и пороги | 15328 | `876b46a7416964e89628721fa08611af0b58c92469138cc382506e8ff1fba08c` | `docs/06-nodes/05-editions-and-filters.md` |
| `03_backend_rag/docs/06-nodes/06-generate-verify-decide.md` | роль 1, ядро и RAG | ND6: генерация, проверка claims, матрица статусов | 17677 | `3345f16f03fe73514f5950480dd7acb57a8e474af7c174b495d5e50bd863dd8a` | `docs/06-nodes/06-generate-verify-decide.md` |
| `03_backend_rag/docs/06-nodes/07-api-contract-and-submission.md` | роль 1, ядро и RAG | ND7: контракт API, SSE, порты, solution.py, Docker, сабмит | 20318 | `82071a3531dcc9dd698781111ea061dd8d7cf0c604f96defbc7581c36127f284` | `docs/06-nodes/07-api-contract-and-submission.md` |
| `03_backend_rag/docs/07-tests/00-strategy.md` | роль 1, ядро и RAG | Стратегия тестов: слои, LLM, флаки, ритм, определение регрессии | 16225 | `c9a1675b6e82d5faf6ccb5ab11a42d46b235a81eab64db8f4ff5537b0bfb76c8` | `docs/07-tests/00-strategy.md` |
| `03_backend_rag/docs/07-tests/01-cascade.md` | роль 1, ядро и RAG | Каскадные тесты по 14 границам, таблица «симптом → узел» | 33554 | `4f9406dea90ceb9abdd16ed5977da962fca3b00cb76df32b3fb95ad5be5a6a20` | `docs/07-tests/01-cascade.md` |
| `03_backend_rag/docs/07-tests/02-regression.md` | роль 1, ядро и RAG | Регрессионный каталог: дефекты, статусы, API, сабмит, UI, a11y | 36580 | `1c1b3bc1c61fec4ca01db130f2b4bc3e4cfd98999c4b89257010b2311a2f90fc` | `docs/07-tests/02-regression.md` |
| `03_backend_rag/docs/07-tests/03-unit-and-contract.md` | роль 1, ядро и RAG | Unit по модулям и контрактные тесты API/UI | 23515 | `94164bde50b7fe50eda18fa3ec0dc413f7f69c1018d68feb6e180ff459c4c9e5` | `docs/07-tests/03-unit-and-contract.md` |
| `03_backend_rag/docs/07-tests/artifacts/asis-d1f068c-lexical-run.md` | роль 1, ядро и RAG | Артефакт лексического прогона as-is на коммите d1f068c | 14483 | `897fd74fff6edd12df1e670788b48782d658167106d212df80c29e5770ae248b` | `docs/07-tests/artifacts/asis-d1f068c-lexical-run.md` |
| `03_backend_rag/docs/08-review/01-code-review-core.md` | роль 1, ядро и RAG | Ревью кода ядра: RAG, проверка, solution.py, контракт | 16274 | `dc9679dd6edfcacb01686baafcc7138e4ea093c14e5c2c1cb6e8f8d0ff48d175` | `docs/08-review/01-code-review-core.md` |
| `03_backend_rag/docs/08-review/03-architecture-review.md` | роль 1, ядро и RAG | Архитектурное ревью: ADR, узлы, границы, fail-closed | 9310 | `92aa21327a11c6ba7098630c1819d755d83f9295c5a2b259958ec378c357a289` | `docs/08-review/03-architecture-review.md` |
| `03_backend_rag/docs/08-review/04-security-review.md` | роль 1, ядро и RAG | Ревью безопасности: инъекции, секреты, роль, API | 10003 | `c3c56fc9d509929e1051ec8678bf414d74cb59d6b42c2c136a7bb22acbe3c587` | `docs/08-review/04-security-review.md` |
| `04_kb_eval/README.md` | роль 3, база и eval | Краткий путеводитель по папке: порядок чтения, зона ответственности, передачи, критерии готовности | 4310 | `5c969d40e615eb0fb47ffe5d6be989db46d56cb285aaf02cac596e77b710532d` | новый файл пакета |
| `04_kb_eval/docs/01-product/03-tz-roles-3-people.md` | роль 3, база и eval | Три роли, задачи с DoD, интерфейсы, ритм работы | 19233 | `c3b237b0432406f3987be850306832ef0f95776aac17b25db21f6ef58c8e9fc5` | `docs/01-product/03-tz-roles-3-people.md` |
| `04_kb_eval/docs/01-product/06-role-3-kb-eval.md` | роль 3, база и eval | Карточки роли 3 (база, eval, документация): R3.1-R3.10 | 13693 | `19029c4467bfdb072f1380a83a15c391d3052f4dec654a722fc8a6b4a47ed83d` | `docs/01-product/06-role-3-kb-eval.md` |
| `04_kb_eval/docs/01-product/07-handoffs-and-interfaces.md` | роль 3, база и eval | Передачи H-01..H-12, протокол контракта, RACI, эскалация | 7578 | `962f49fb66061018085a61668d809f9a619fb1c15ed668d0c282e366f3b34c5e` | `docs/01-product/07-handoffs-and-interfaces.md` |
| `04_kb_eval/docs/01-product/10-tz-kb-eval-complete.md` | роль 3, база и eval | Полное ТЗ роли 3: эталон базы, golden, судья, отчёты, KE-* | 24405 | `551465656abaf11c07391ebc94b5cff01e299bd31eeb96b356a7ff92160cbbca` | `docs/01-product/10-tz-kb-eval-complete.md` |
| `04_kb_eval/docs/02-architecture/03-data-model-and-kb.md` | роль 3, база и eval | Модель данных и база: 21 файл, аномалии KB-A1..A7, индекс | 22630 | `44679e483878cea9d5d867ad5fdb2448d6748d8d6723001ceaa82fdc6e643cd0` | `docs/02-architecture/03-data-model-and-kb.md` |
| `04_kb_eval/docs/05-rag/01-rag-deep-dive.md` | роль 3, база и eval | Глубокий разбор RAG и список дефектов D1-D28 | 64483 | `8eeb0b0308780bb9241c6ec8475b6ac5f74e6ec720c9f13005a58c5373986a67` | `docs/05-rag/01-rag-deep-dive.md` |
| `04_kb_eval/docs/07-tests/00-strategy.md` | роль 3, база и eval | Стратегия тестов: слои, LLM, флаки, ритм, определение регрессии | 16225 | `c9a1675b6e82d5faf6ccb5ab11a42d46b235a81eab64db8f4ff5537b0bfb76c8` | `docs/07-tests/00-strategy.md` |
| `04_kb_eval/docs/07-tests/01-cascade.md` | роль 3, база и eval | Каскадные тесты по 14 границам, таблица «симптом → узел» | 33554 | `4f9406dea90ceb9abdd16ed5977da962fca3b00cb76df32b3fb95ad5be5a6a20` | `docs/07-tests/01-cascade.md` |
| `04_kb_eval/docs/07-tests/02-regression.md` | роль 3, база и eval | Регрессионный каталог: дефекты, статусы, API, сабмит, UI, a11y | 36580 | `1c1b3bc1c61fec4ca01db130f2b4bc3e4cfd98999c4b89257010b2311a2f90fc` | `docs/07-tests/02-regression.md` |
| `04_kb_eval/docs/07-tests/04-eval-golden.md` | роль 3, база и eval | Golden-набор: формат кейсов, метрики, суррогатный судья | 17295 | `aa2eba88e98e6b60a2a9408c172eb3d8e39f86d59886fa01afb6d9a19e915619` | `docs/07-tests/04-eval-golden.md` |
| `04_kb_eval/docs/07-tests/05-traceability.md` | роль 3, база и eval | Трассировка: требование → узел → тест → дефект → критерий | 9459 | `17f78147f0219e44524a8705e0881226214a12ddf87a6b7ab9726d049fad2536` | `docs/07-tests/05-traceability.md` |
| `04_kb_eval/docs/07-tests/artifacts/asis-d1f068c-lexical-run.md` | роль 3, база и eval | Артефакт лексического прогона as-is на коммите d1f068c | 14483 | `897fd74fff6edd12df1e670788b48782d658167106d212df80c29e5770ae248b` | `docs/07-tests/artifacts/asis-d1f068c-lexical-run.md` |
| `04_kb_eval/docs/08-review/05-tests-and-eval-review.md` | роль 3, база и eval | Ревью тестов и eval: оракулы, покрытие, golden | 10623 | `047920b7598663f4895eeb653e20f3b48fe317487fbf69f1c183dd63d6324660` | `docs/08-review/05-tests-and-eval-review.md` |
| `04_kb_eval/docs/08-review/06-docs-review.md` | роль 3, база и eval | Ревью документации на соответствие коду и кейсу | 8025 | `bd13ed869719a84f5e729d1be128d41f04956fef48efcb7f5f266c436217dfb9` | `docs/08-review/06-docs-review.md` |
| `05_review_and_tests/README.md` | ревью и тесты (полный набор) | Краткий путеводитель по папке: порядок чтения, зона ответственности, передачи, критерии готовности | 2693 | `56939b0dbfabdfae098ca620ce8bb3265739b8b031852842d8054e0671b56bee` | новый файл пакета |
| `05_review_and_tests/docs/07-tests/00-strategy.md` | ревью и тесты (полный набор) | Стратегия тестов: слои, LLM, флаки, ритм, определение регрессии | 16225 | `c9a1675b6e82d5faf6ccb5ab11a42d46b235a81eab64db8f4ff5537b0bfb76c8` | `docs/07-tests/00-strategy.md` |
| `05_review_and_tests/docs/07-tests/01-cascade.md` | ревью и тесты (полный набор) | Каскадные тесты по 14 границам, таблица «симптом → узел» | 33554 | `4f9406dea90ceb9abdd16ed5977da962fca3b00cb76df32b3fb95ad5be5a6a20` | `docs/07-tests/01-cascade.md` |
| `05_review_and_tests/docs/07-tests/02-regression.md` | ревью и тесты (полный набор) | Регрессионный каталог: дефекты, статусы, API, сабмит, UI, a11y | 36580 | `1c1b3bc1c61fec4ca01db130f2b4bc3e4cfd98999c4b89257010b2311a2f90fc` | `docs/07-tests/02-regression.md` |
| `05_review_and_tests/docs/07-tests/03-unit-and-contract.md` | ревью и тесты (полный набор) | Unit по модулям и контрактные тесты API/UI | 23515 | `94164bde50b7fe50eda18fa3ec0dc413f7f69c1018d68feb6e180ff459c4c9e5` | `docs/07-tests/03-unit-and-contract.md` |
| `05_review_and_tests/docs/07-tests/04-eval-golden.md` | ревью и тесты (полный набор) | Golden-набор: формат кейсов, метрики, суррогатный судья | 17295 | `aa2eba88e98e6b60a2a9408c172eb3d8e39f86d59886fa01afb6d9a19e915619` | `docs/07-tests/04-eval-golden.md` |
| `05_review_and_tests/docs/07-tests/05-traceability.md` | ревью и тесты (полный набор) | Трассировка: требование → узел → тест → дефект → критерий | 9459 | `17f78147f0219e44524a8705e0881226214a12ddf87a6b7ab9726d049fad2536` | `docs/07-tests/05-traceability.md` |
| `05_review_and_tests/docs/07-tests/artifacts/asis-d1f068c-lexical-run.md` | ревью и тесты (полный набор) | Артефакт лексического прогона as-is на коммите d1f068c | 14483 | `897fd74fff6edd12df1e670788b48782d658167106d212df80c29e5770ae248b` | `docs/07-tests/artifacts/asis-d1f068c-lexical-run.md` |
| `05_review_and_tests/docs/08-review/00-overview.md` | ревью и тесты (полный набор) | Правила ревью: виды, метки, фиксация находок, ошибки ревьюера | 12608 | `a6b400aa6db8832c41355955cd2d350dc6908d4370c1d697d3cf659ae4a65995` | `docs/08-review/00-overview.md` |
| `05_review_and_tests/docs/08-review/01-code-review-core.md` | ревью и тесты (полный набор) | Ревью кода ядра: RAG, проверка, solution.py, контракт | 16274 | `dc9679dd6edfcacb01686baafcc7138e4ea093c14e5c2c1cb6e8f8d0ff48d175` | `docs/08-review/01-code-review-core.md` |
| `05_review_and_tests/docs/08-review/02-frontend-design-review.md` | ревью и тесты (полный набор) | Ревью фронтенда и дизайна | 10354 | `6afe7c6daeab5dd75d1319ff967f17c359fcaaed1d81f97ded1021d15428257d` | `docs/08-review/02-frontend-design-review.md` |
| `05_review_and_tests/docs/08-review/03-architecture-review.md` | ревью и тесты (полный набор) | Архитектурное ревью: ADR, узлы, границы, fail-closed | 9310 | `92aa21327a11c6ba7098630c1819d755d83f9295c5a2b259958ec378c357a289` | `docs/08-review/03-architecture-review.md` |
| `05_review_and_tests/docs/08-review/04-security-review.md` | ревью и тесты (полный набор) | Ревью безопасности: инъекции, секреты, роль, API | 10003 | `c3c56fc9d509929e1051ec8678bf414d74cb59d6b42c2c136a7bb22acbe3c587` | `docs/08-review/04-security-review.md` |
| `05_review_and_tests/docs/08-review/05-tests-and-eval-review.md` | ревью и тесты (полный набор) | Ревью тестов и eval: оракулы, покрытие, golden | 10623 | `047920b7598663f4895eeb653e20f3b48fe317487fbf69f1c183dd63d6324660` | `docs/08-review/05-tests-and-eval-review.md` |
| `05_review_and_tests/docs/08-review/06-docs-review.md` | ревью и тесты (полный набор) | Ревью документации на соответствие коду и кейсу | 8025 | `bd13ed869719a84f5e729d1be128d41f04956fef48efcb7f5f266c436217dfb9` | `docs/08-review/06-docs-review.md` |

## Этот файл

Строка ниже добавляется после записи манифеста, чтобы SHA256 описывал окончательное содержимое.

## Этот файл

Хеш и размер `00_START_HERE/MANIFEST.md` в таблицу не входят: они зависят от собственного текста.
После распаковки его можно проверить командой `sha256sum 00_START_HERE/MANIFEST.md`.
