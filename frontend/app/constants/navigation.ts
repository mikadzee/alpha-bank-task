
export interface Page {
  id: number;
  name: string;
  icon: string;
  path: string;
}

// кб предпринимателя
export const pages: Page[] = [
  {
    id: 1,
    name: 'Главная',
    icon: 'icon-home',
    path: '/',
  },
  {
    id: 2,
    name: 'Мои заявки',
    icon: 'icon-file-text',
    path: '/applications',
  },
  {
    id: 3,
    name: 'Кредиты',
    icon: 'icon-credit-card',
    path: '/loans',
  },
  {
    id: 4,
    name: 'Моя компания',
    icon: 'icon-building',
    path: '/company',
  },
  {
    id: 5,
    name: 'Документы',
    icon: 'icon-folder',
    path: '/documents',
  },
];

export const employeePages: Page[] = [
  { id: 1, name: 'Входящие заявки', icon: 'icon-clipboard', path: '/staff' },
];
