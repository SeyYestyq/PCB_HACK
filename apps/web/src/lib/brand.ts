/** Продуктовые строки интерфейса. Юридические утверждения здесь не формулируются. */

export const PRODUCT_NAME = "Юридический ассистент";
export const PRODUCT_OWNER = "ПСБ · юридическая служба";
export const PRODUCT_BUILD = "пилот · сборка 0.3";

export const HERO_LABEL = "База знаний банка";
export const HERO_TITLE = "Ответ по документам — с пунктом-основанием";
export const HERO_TEXT =
  "Ассистент ищет только в выданной базе знаний и показывает фрагменты, на которых построен ответ. Если положения нет, он откажет, а не достроит норму.";

export const COMPOSER_PLACEHOLDER = "Вопрос по документам базы знаний";

export const TRUST_SHORT =
  "Ответ ограничен базой знаний. Выводы сверяйте с пунктами в источниках.";

export const HERO_CHIPS = [
  "Только база знаний",
  "Каждый вывод — с пунктом",
  "Отказ вместо догадки",
];

export type Example = {
  label: string;
  question: string;
  icon: "contract" | "labor" | "absence";
};

export const EXAMPLES: Example[] = [
  {
    label: "Договор аренды",
    question:
      "Какая арендная плата по договору с ООО «Северный Склад» и до какого числа её нужно вносить?",
    icon: "contract",
  },
  {
    label: "Трудовой кодекс",
    question:
      "Какой максимальный срок испытания можно установить главному бухгалтеру?",
    icon: "labor",
  },
  {
    label: "Нормы нет в базе",
    question: "Какой размер пособия по беременности и родам?",
    icon: "absence",
  },
];
