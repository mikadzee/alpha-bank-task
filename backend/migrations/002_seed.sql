INSERT INTO loan_products
    (code, name, purpose, description, min_amount, max_amount,
     min_term_months, max_term_months, annual_rate, is_active)
VALUES
    ('turnover', 'Кредит на пополнение оборотных средств', 'working_capital',
     'Финансирование закупок, оплаты поставщикам и текущих расходов бизнеса.',
     500000, 3000000, 6, 36, 16, TRUE),
    ('equipment', 'Кредит на покупку оборудования', 'equipment',
     'Финансирование покупки или обновления оборудования.',
     1000000, 10000000, 12, 60, 18, TRUE),
    ('growth', 'Кредит на развитие бизнеса', 'business_expansion',
     'Финансирование запуска направления или расширения бизнеса.',
     300000, 5000000, 6, 48, 20, TRUE),
    ('universal', 'Кредит на любые бизнес-цели', 'other',
     'Демонстрационный продукт для иных целей финансирования.',
     300000, 5000000, 6, 48, 21, TRUE)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    purpose = EXCLUDED.purpose,
    description = EXCLUDED.description,
    min_amount = EXCLUDED.min_amount,
    max_amount = EXCLUDED.max_amount,
    min_term_months = EXCLUDED.min_term_months,
    max_term_months = EXCLUDED.max_term_months,
    annual_rate = EXCLUDED.annual_rate,
    is_active = TRUE;

INSERT INTO mock_companies (inn, company_name, ogrn, address, okved)
VALUES
    ('7701234567', 'ООО ТехноПлюс', '1237700123456', 'г. Москва, ул. Примерная, д. 10', '28.99'),
    ('7812345678', 'ООО Северный проект', '1187847000123', 'г. Санкт-Петербург, Невский проспект, д. 20', '46.90'),
    ('7723456789', 'ООО Альфа Трейд', '1167746000456', 'г. Москва, ул. Деловая, д. 5', '46.90'),
    ('5401234567', 'ООО Сибирь Сервис', '1205400000789', 'г. Новосибирск, ул. Центральная, д. 8', '82.99'),
    ('6601234567', 'ООО УралМаш', '1196658000123', 'г. Екатеринбург, ул. Заводская, д. 14', '28.99'),
    ('5001234567', 'ООО Подмосковье Логистика', '1175029000345', 'Московская обл., г. Химки, ул. Транспортная, д. 3', '49.41'),
    ('2301234567', 'ООО Кубань Агро', '1212300000678', 'г. Краснодар, ул. Солнечная, д. 11', '01.11'),
    ('123456789012', 'ИП Иванов Алексей Сергеевич', '321774600098765', 'г. Москва, ул. Новая, д. 7', '47.91')
ON CONFLICT (inn) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    ogrn = EXCLUDED.ogrn,
    address = EXCLUDED.address,
    okved = EXCLUDED.okved;
