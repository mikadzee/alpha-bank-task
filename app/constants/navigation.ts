
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

// кб сотрудника банка
export const adminPages: Page[] = [
  {
    id: 1,
    name: 'Обзор',
    icon: 'icon-dashboard',
    path: '/admin',
  },
  {
    id: 2,
    name: 'Заявки клиентов',
    icon: 'icon-clipboard',
    path: '/admin/applications',
  },
  {
    id: 3,
    name: 'Компании',
    icon: 'icon-building',
    path: '/admin/companies',
  },
  {
    id: 4,
    name: 'Кредитные продукты',
    icon: 'icon-credit-card',
    path: '/admin/products',
  },
  {
    id: 5,
    name: 'Аналитика',
    icon: 'icon-chart',
    path: '/admin/analytics',
  },
];
