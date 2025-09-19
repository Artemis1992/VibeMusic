# SQL-запросы для базы данных vibemusic

## Описание
Эта таблица содержит 100 SQL-запросов, от простых до сложных, для работы с базой данных музыкальной платформы `vibemusic`. Запросы охватывают выборку данных, вставку, обновление, удаление, объединения таблиц, агрегатные функции, подзапросы и индексы. Каждый запрос адаптирован к таблицам `Users`, `Artists`, `Genres`, `Tracks`, `Posts`, `Comments`, `Reactions`.

| №  | Уровень сложности | Запрос | Описание | Примечания |
|----|-------------------|--------|----------|------------|
| 1  | Базовый | `SELECT * FROM Users;` | Получить все записи из таблицы `Users`. | Простейший запрос для вывода всех пользователей. |
| 2  | Базовый | `SELECT username, email FROM Users;` | Выбрать только столбцы `username` и `email` из `Users`. | Ограничение выборки конкретными столбцами. |
| 3  | Базовый | `SELECT title FROM Tracks;` | Выбрать названия всех треков. | Простая выборка одного столбца. |
| 4  | Базовый | `SELECT * FROM Tracks WHERE duration > 180;` | Получить треки длительностью более 3 минут. | Условие `WHERE` для фильтрации по числовому полю. |
| 5  | Базовый | `SELECT username FROM Users WHERE join_date >= '2025-01-01';` | Показать пользователей, зарегистрированных после 1 января 2025. | Фильтрация по дате. |
| 6  | Базовый | `SELECT title, artist_id FROM Tracks WHERE artist_id = 1;` | Найти треки конкретного артиста (ID=1). | Условие на внешний ключ. |
| 7  | Базовый | `SELECT * FROM Comments ORDER BY created_at DESC;` | Вывести комментарии, отсортированные по дате (от новых к старым). | Сортировка с `ORDER BY`. |
| 8  | Базовый | `SELECT DISTINCT name FROM Artists;` | Получить уникальных артистов. | Устранение дубликатов с `DISTINCT`. |
| 9  | Базовый | `SELECT * FROM Tracks LIMIT 10;` | Вывести первые 10 треков. | Ограничение количества строк (MySQL/PostgreSQL). |
| 10 | Базовый | `SELECT title FROM Tracks WHERE title LIKE '%love%';` | Найти треки с "love" в названии. | Поиск подстроки с `LIKE`. |
| 11 | Базовый | `SELECT * FROM Genres WHERE slug = 'rock';` | Найти жанр по slug. | Фильтрация по текстовому полю. |
| 12 | Базовый | `SELECT content FROM Comments WHERE post_id = 5;` | Получить комментарии к посту с ID=5. | Условие на внешний ключ. |
| 13 | Базовый | `SELECT * FROM Posts WHERE created_at > '2025-01-01';` | Найти посты, созданные после 1 января 2025. | Фильтрация по дате. |
| 14 | Базовый | `SELECT name FROM Genres ORDER BY name ASC;` | Вывести жанры, отсортированные по алфавиту. | Сортировка по возрастанию. |
| 15 | Базовый | `SELECT * FROM Reactions WHERE user_id = 10;` | Найти все реакции пользователя с ID=10. | Фильтрация реакций по пользователю. |
| 16 | Базовый | `INSERT INTO Users (username, email, join_date, is_active) VALUES ('user1', 'user1@example.com', '2025-08-01', TRUE);` | Добавить нового пользователя. | Простая вставка данных. |
| 17 | Базовый | `INSERT INTO Tracks (title, artist_id, genre_id, duration) VALUES ('New Song', 1, 2, 200);` | Добавить новый трек. | Вставка с указанием внешних ключей. |
| 18 | Базовый | `UPDATE Users SET is_active = FALSE WHERE id = 1;` | Деактивировать пользователя с ID=1. | Обновление одного поля. |
| 19 | Базовый | `DELETE FROM Comments WHERE id = 10;` | Удалить комментарий с ID=10. | Простое удаление записи. |
| 20 | Базовый | `SELECT COUNT(*) FROM Tracks;` | Подсчитать общее количество треков. | Простая агрегатная функция `COUNT`. |
| 21 | Средний | `SELECT * FROM Tracks WHERE duration BETWEEN 180 AND 300;` | Найти треки с длительностью от 3 до 5 минут. | Использование `BETWEEN` для диапазона. |
| 22 | Средний | `SELECT title, release_date FROM Tracks WHERE release_date IS NOT NULL;` | Получить треки с известной датой релиза. | Проверка на `NOT NULL`. |
| 23 | Средний | `SELECT username FROM Users WHERE email LIKE '%@gmail.com';` | Найти пользователей с Gmail-адресами. | Поиск по шаблону в email. |
| 24 | Средний | `SELECT * FROM Posts WHERE title LIKE '%review%' LIMIT 5;` | Найти 5 постов с "review" в заголовке. | Комбинация `LIKE` и `LIMIT`. |
| 25 | Средний | `SELECT * FROM Comments WHERE created_at >= NOW() - INTERVAL '1 day';` | Получить комментарии за последние 24 часа. | Работа с временными интервалами (PostgreSQL). |
| 26 | Средний | `SELECT name FROM Genres WHERE background_image IS NULL;` | Найти жанры без фонового изображения. | Проверка на `NULL`. |
| 27 | Средний | `SELECT title, duration FROM Tracks ORDER BY duration DESC LIMIT 10;` | Вывести 10 самых длинных треков. | Сортировка и ограничение. |
| 28 | Средний | `INSERT INTO Comments (user_id, post_id, content, created_at) VALUES (1, 5, 'Great post!', NOW());` | Добавить комментарий с текущей датой. | Использование функции `NOW()`. |
| 29 | Средний | `UPDATE Tracks SET duration = duration + 10 WHERE id = 3;` | Увеличить длительность трека на 10 секунд. | Обновление с арифметической операцией. |
| 30 | Средний | `DELETE FROM Reactions WHERE created_at < '2025-01-01';` | Удалить старые реакции (до 2025 года). | Удаление с условием по дате. |
| 31 | Средний | `SELECT AVG(duration) FROM Tracks;` | Вычислить среднюю длительность треков. | Агрегатная функция `AVG`. |
| 32 | Средний | `SELECT MAX(created_at) FROM Comments;` | Найти дату последнего комментария. | Агрегатная функция `MAX`. |
| 33 | Средний | `SELECT MIN(duration) FROM Tracks WHERE genre_id = 2;` | Найти самый короткий трек в жанре (ID=2). | `MIN` с фильтрацией. |
| 34 | Средний | `SELECT COUNT(*) FROM Users WHERE is_active = TRUE;` | Подсчитать активных пользователей. | `COUNT` с условием. |
| 35 | Средний | `SELECT title FROM Tracks WHERE artist_id IN (1, 2, 3);` | Найти треки нескольких артистов. | Использование `IN`. |
| 36 | Средний | `SELECT * FROM Posts WHERE genre_id IS NULL;` | Найти посты без указанного жанра. | Проверка на `NULL`. |
| 37 | Средний | `SELECT username FROM Users WHERE id NOT IN (SELECT user_id FROM Comments);` | Найти пользователей, не оставивших комментариев. | Подзапрос с `NOT IN`. |
| 38 | Средний | `SELECT title FROM Tracks WHERE release_date > CURRENT_DATE - INTERVAL '1 year';` | Найти треки, выпущенные за последний год. | Работа с датами (PostgreSQL). |
| 39 | Средний | `SELECT * FROM Reactions WHERE track_id IS NOT NULL;` | Найти реакции, связанные с треками. | Фильтрация по `NOT NULL`. |
| 40 | Средний | `SELECT name FROM Genres WHERE name LIKE 'r%';` | Найти жанры, начинающиеся на "r". | Поиск по началу строки. |
| 41 | Средний | `INSERT INTO Artists (name, bio) VALUES ('New Artist', 'Bio text') RETURNING id;` | Добавить артиста и вернуть его ID. | `RETURNING` для получения ID (PostgreSQL). |
| 42 | Средний | `UPDATE Posts SET content = 'Updated' WHERE author_id = 1;` | Обновить содержимое постов автора. | Обновление с фильтрацией по внешнему ключу. |
| 43 | Средний | `DELETE FROM Tracks WHERE duration < 60;` | Удалить треки короче 1 минуты. | Удаление с числовым условием. |
| 44 | Средний | `SELECT COUNT(*) FROM Comments GROUP BY post_id;` | Подсчитать комментарии для каждого поста. | Группировка с `GROUP BY`. |
| 45 | Средний | `SELECT genre_id, COUNT(*) FROM Tracks GROUP BY genre_id;` | Подсчитать треки по жанрам. | Агрегатная функция с группировкой. |
| 46 | Продвинутый | `SELECT t.title, a.name FROM Tracks t JOIN Artists a ON t.artist_id = a.id;` | Получить треки с именами артистов. | Простое объединение с `JOIN`. |
| 47 | Продвинутый | `SELECT p.title, g.name FROM Posts p LEFT JOIN Genres g ON p.genre_id = g.id;` | Получить посты с жанрами (включая посты без жанра). | `LEFT JOIN` для сохранения всех постов. |
| 48 | Продвинутый | `SELECT u.username, c.content FROM Users u JOIN Comments c ON u.id = c.user_id WHERE c.post_id = 5;` | Получить комментарии к посту с именами пользователей. | Объединение с фильтрацией. |
| 49 | Продвинутый | `SELECT t.title, g.name FROM Tracks t JOIN Genres g ON t.genre_id = g.id WHERE g.slug = 'rock';` | Найти треки жанра "rock" с названием жанра. | `JOIN` с условием. |
| 50 | Продвинутый | `SELECT a.name, COUNT(t.id) FROM Artists a LEFT JOIN Tracks t ON a.id = t.artist_id GROUP BY a.id;` | Подсчитать треки для каждого артиста. | `LEFT JOIN` с группировкой. |
| 51 | Продвинутый | `SELECT p.title, COUNT(c.id) FROM Posts p LEFT JOIN Comments c ON p.id = c.post_id GROUP BY p.id;` | Подсчитать комментарии для каждого поста. | Группировка с `LEFT JOIN`. |
| 52 | Продвинутый | `SELECT u.username FROM Users u WHERE EXISTS (SELECT 1 FROM Comments c WHERE c.user_id = u.id);` | Найти пользователей, оставивших комментарии. | Подзапрос с `EXISTS`. |
| 53 | Продвинутый | `SELECT t.title FROM Tracks t WHERE t.id IN (SELECT track_id FROM Reactions);` | Найти треки с лайками. | Подзапрос с `IN`. |
| 54 | Продвинутый | `SELECT title FROM Posts WHERE id = (SELECT post_id FROM Comments WHERE content LIKE '%awesome%');` | Найти посты с комментариями, содержащими "awesome". | Подзапрос в условии. |
| 55 | Продвинутый | `SELECT a.name FROM Artists a WHERE NOT EXISTS (SELECT 1 FROM Tracks t WHERE t.artist_id = a.id);` | Найти артистов без треков. | Подзапрос с `NOT EXISTS`. |
| 56 | Продвинутый | `SELECT t.title, (SELECT COUNT(*) FROM Reactions r WHERE r.track_id = t.id) AS like_count FROM Tracks t;` | Получить треки с количеством лайков. | Подзапрос в `SELECT`. |
| 57 | Продвинутый | `SELECT u.username, (SELECT COUNT(*) FROM Comments c WHERE c.user_id = u.id) AS comment_count FROM Users u;` | Получить пользователей с количеством их комментариев. | Подзапрос для подсчёта. |
| 58 | Продвинутый | `SELECT t.title FROM Tracks t JOIN Reactions r ON t.id = r.track_id GROUP BY t.id HAVING COUNT(r.id) > 5;` | Найти треки с более чем 5 лайками. | `HAVING` для фильтрации групп. |
| 59 | Продвинутый | `SELECT g.name, COUNT(t.id) FROM Genres g LEFT JOIN Tracks t ON g.id = t.genre_id GROUP BY g.id HAVING COUNT(t.id) = 0;` | Найти жанры без треков. | `HAVING` с нулевым счётом. |
| 60 | Продвинутый | `SELECT u.username FROM Users u JOIN Reactions r ON u.id = r.user_id WHERE r.track_id IS NOT NULL GROUP BY u.id HAVING COUNT(r.id) > 3;` | Найти пользователей с более чем 3 лайками треков. | Группировка с `HAVING`. |
| 61 | Сложный | `WITH active_users AS (SELECT id, username FROM Users WHERE is_active = TRUE) SELECT au.username, COUNT(c.id) FROM active_users au LEFT JOIN Comments c ON au.id = c.user_id GROUP BY au.id;` | Подсчитать комментарии активных пользователей. | Использование CTE (`WITH`). |
| 62 | Сложный | `WITH top_tracks AS (SELECT track_id, COUNT(*) AS like_count FROM Reactions GROUP BY track_id) SELECT t.title, tt.like_count FROM Tracks t JOIN top_tracks tt ON t.id = tt.track_id ORDER BY tt.like_count DESC LIMIT 10;` | Найти 10 самых популярных треков по лайкам. | CTE с сортировкой. |
| 63 | Сложный | `SELECT t.title, COALESCE((SELECT COUNT(*) FROM Reactions r WHERE r.track_id = t.id), 0) AS like_count FROM Tracks t;` | Получить треки с количеством лайков (0 для треков без лайков). | `COALESCE` для обработки NULL. |
| 64 | Сложный | `SELECT p.title FROM Posts p WHERE p.id IN (SELECT post_id FROM Comments GROUP BY post_id HAVING COUNT(*) > 10);` | Найти посты с более чем 10 комментариями. | Подзапрос с группировкой. |
| 65 | Сложный | `SELECT a.name FROM Artists a WHERE a.id IN (SELECT artist_id FROM Tracks WHERE genre_id = (SELECT id FROM Genres WHERE slug = 'rock'));` | Найти артистов с треками в жанре "rock". | Вложенный подзапрос. |
| 66 | Сложный | `SELECT u.username FROM Users u WHERE u.id IN (SELECT user_id FROM Reactions WHERE track_id IN (SELECT id FROM Tracks WHERE genre_id = 2));` | Найти пользователей, лайкнувших треки жанра (ID=2). | Многоуровневый подзапрос. |
| 67 | Сложный | `UPDATE Tracks SET duration = (SELECT AVG(duration) FROM Tracks) WHERE duration IS NULL;` | Установить среднюю длительность для треков без длительности. | Подзапрос в `UPDATE`. |
| 68 | Сложный | `DELETE FROM Comments WHERE post_id IN (SELECT id FROM Posts WHERE created_at < '2024-01-01');` | Удалить комментарии к старым постам. | Подзапрос в `DELETE`. |
| 69 | Сложный | `SELECT t.title, g.name FROM Tracks t JOIN Genres g ON t.genre_id = g.id WHERE g.id IN (SELECT genre_id FROM Tracks GROUP BY genre_id HAVING COUNT(*) > 5);` | Найти треки из жанров с более чем 5 треками. | Подзапрос с `HAVING`. |
| 70 | Сложный | `SELECT u.username FROM Users u WHERE u.join_date > (SELECT MIN(created_at) FROM Posts);` | Найти пользователей, зарегистрированных после первого поста. | Подзапрос для сравнения дат. |
| 71 | Сложный | `WITH RECURSIVE genre_hierarchy AS (SELECT id, name, parent_id FROM Genres WHERE parent_id IS NULL UNION ALL SELECT g.id, g.name, g.parent_id FROM Genres g JOIN genre_hierarchy gh ON g.parent_id = gh.id) SELECT * FROM genre_hierarchy;` | Получить иерархию жанров (если есть родительские жанры). | Рекурсивный CTE (PostgreSQL). |
| 72 | Сложный | `SELECT t.title, COUNT(r.id) AS like_count FROM Tracks t LEFT JOIN Reactions r ON t.id = r.track_id GROUP BY t.id ORDER BY like_count DESC LIMIT 5;` | Найти 5 треков с наибольшим количеством лайков. | Сортировка по агрегации. |
| 73 | Сложный | `SELECT p.title, u.username FROM Posts p JOIN Users u ON p.author_id = u.id WHERE p.created_at >= NOW() - INTERVAL '7 days';` | Найти посты за последние 7 дней с именами авторов. | `JOIN` с временным фильтром. |
| 74 | Сложный | `SELECT a.name, (SELECT COUNT(*) FROM Tracks t WHERE t.artist_id = a.id) AS track_count FROM Artists a WHERE (SELECT COUNT(*) FROM Tracks t WHERE t.artist_id = a.id) > 0;` | Найти артистов с треками и их количество. | Подзапрос в `SELECT` и `WHERE`. |
| 75 | Сложный | `SELECT u.username FROM Users u WHERE u.id IN (SELECT user_id FROM Comments WHERE post_id IN (SELECT id FROM Posts WHERE genre_id = 1));` | Найти пользователей, комментировавших посты жанра (ID=1). | Многоуровневый подзапрос. |
| 76 | Сложный | `UPDATE Comments SET content = 'Edited' WHERE id IN (SELECT id FROM Comments WHERE created_at < NOW() - INTERVAL '30 days');` | Обновить старые комментарии (старше 30 дней). | Подзапрос в `UPDATE`. |
| 77 | Сложный | `DELETE FROM Reactions WHERE track_id IN (SELECT id FROM Tracks WHERE artist_id = 1);` | Удалить реакции к трекам артиста (ID=1). | Подзапрос в `DELETE`. |
| 78 | Сложный | `SELECT t.title, g.name FROM Tracks t JOIN Genres g ON t.genre_id = g.id WHERE t.id IN (SELECT track_id FROM Reactions GROUP BY track_id HAVING COUNT(*) > 3);` | Найти треки с более чем 3 лайками и их жанры. | Подзапрос с `HAVING`. |
| 79 | Сложный | `SELECT u.username, COUNT(c.id) AS comment_count FROM Users u LEFT JOIN Comments c ON u.id = c.user_id GROUP BY u.id HAVING COUNT(c.id) > 5;` | Найти пользователей с более чем 5 комментариями. | `HAVING` с группировкой. |
| 80 | Сложный | `SELECT t.title, COALESCE((SELECT COUNT(*) FROM Reactions r WHERE r.comment_id IS NOT NULL AND r.comment_id IN (SELECT id FROM Comments WHERE post_id = p.id)), 0) AS comment_likes FROM Posts p JOIN Tracks t ON p.genre_id = t.genre_id;` | Получить треки и количество лайков комментариев к постам того же жанра. | Сложный подзапрос с `COALESCE`. |
| 81 | Эксперт | `CREATE INDEX idx_tracks_genre_id ON Tracks (genre_id);` | Создать индекс для ускорения поиска треков по жанру. | Улучшает производительность запросов с `WHERE genre_id`. |
| 82 | Эксперт | `CREATE UNIQUE INDEX idx_users_email ON Users (email);` | Создать уникальный индекс для email пользователей. | Гарантирует уникальность email. |
| 83 | Эксперт | `SELECT t.title, g.name FROM Tracks t JOIN Genres g ON t.genre_id = g.id WHERE t.id IN (SELECT track_id FROM Reactions r JOIN Users u ON r.user_id = u.id WHERE u.is_active = TRUE);` | Найти треки, лайкнутые активными пользователями, с жанрами. | Многоуровневый `JOIN` с подзапросом. |
| 84 | Эксперт | `WITH popular_posts AS (SELECT post_id, COUNT(*) AS comment_count FROM Comments GROUP BY post_id HAVING COUNT(*) > 10) SELECT p.title, pp.comment_count FROM Posts p JOIN popular_posts pp ON p.id = pp.post_id;` | Найти посты с более чем 10 комментариями. | CTE с группировкой. |
| 85 | Эксперт | `SELECT u.username, (SELECT COUNT(*) FROM Posts p WHERE p.author_id = u.id) AS post_count, (SELECT COUNT(*) FROM Comments c WHERE c.user_id = u.id) AS comment_count FROM Users u;` | Получить пользователей с количеством их постов и комментариев. | Множественные подзапросы в `SELECT`. |
| 86 | Эксперт | `SELECT t.title FROM Tracks t WHERE t.id IN (SELECT track_id FROM Reactions GROUP BY track_id HAVING COUNT(DISTINCT user_id) > 5);` | Найти треки, лайкнутые более чем 5 уникальными пользователями. | `DISTINCT` в подзапросе с `HAVING`. |
| 87 | Эксперт | `UPDATE Tracks SET genre_id = (SELECT id FROM Genres WHERE slug = 'pop') WHERE artist_id IN (SELECT id FROM Artists WHERE name = 'Artist1');` | Изменить жанр треков артиста на "pop". | Подзапросы в `UPDATE`. |
| 88 | Эксперт | `DELETE FROM Comments WHERE user_id IN (SELECT id FROM Users WHERE is_active = FALSE);` | Удалить комментарии неактивных пользователей. | Подзапрос в `DELETE`. |
| 89 | Эксперт | `SELECT a.name, t.title FROM Artists a JOIN Tracks t ON a.id = t.artist_id WHERE t.id IN (SELECT track_id FROM Reactions WHERE created_at >= NOW() - INTERVAL '7 days');` | Найти артистов и их треки с лайками за последние 7 дней. | Сложный запрос с временным фильтром. |
| 90 | Эксперт | `SELECT g.name, COUNT(t.id) AS track_count FROM Genres g LEFT JOIN Tracks t ON g.id = t.genre_id GROUP BY g.id ORDER BY track_count DESC LIMIT 3;` | Найти 3 жанра с наибольшим количеством треков. | Сортировка по агрегации. |
| 91 | Эксперт | `SELECT u.username FROM Users u WHERE u.id IN (SELECT user_id FROM Reactions WHERE track_id IN (SELECT id FROM Tracks WHERE genre_id IN (SELECT id FROM Genres WHERE slug = 'jazz')));` | Найти пользователей, лайкнувших джазовые треки. | Тройной подзапрос. |
| 92 | Эксперт | `WITH comment_stats AS (SELECT post_id, COUNT(*) AS comment_count, MAX(created_at) AS last_comment FROM Comments GROUP BY post_id) SELECT p.title, cs.comment_count, cs.last_comment FROM Posts p JOIN comment_stats cs ON p.id = cs.post_id;` | Получить посты с количеством и датой последнего комментария. | CTE с несколькими агрегациями. |
| 93 | Эксперт | `SELECT t.title FROM Tracks t WHERE t.id NOT IN (SELECT track_id FROM Reactions WHERE user_id IN (SELECT id FROM Users WHERE is_active = TRUE));` | Найти треки, не лайкнутые активными пользователями. | Подзапрос с `NOT IN`. |
| 94 | Эксперт | `SELECT u.username, COUNT(DISTINCT p.id) AS post_count, COUNT(DISTINCT c.id) AS comment_count FROM Users u LEFT JOIN Posts p ON u.id = p.author_id LEFT JOIN Comments c ON u.id = c.user_id GROUP BY u.id;` | Подсчитать посты и комментарии каждого пользователя. | Множественные `JOIN` и `DISTINCT`. |
| 95 | Эксперт | `CREATE TABLE temp_users AS SELECT id, username FROM Users WHERE is_active = TRUE;` | Создать временную таблицу с активными пользователями. | Создание таблицы на основе запроса. |
| 96 | Эксперт | `SELECT t.title, g.name FROM Tracks t JOIN Genres g ON t.genre_id = g.id WHERE t.release_date = (SELECT MAX(release_date) FROM Tracks WHERE genre_id = g.id);` | Найти последний трек для каждого жанра. | Подзапрос с `MAX`. |
| 97 | Эксперт | `UPDATE Users SET email = CONCAT(username, '@vibemusic.com') WHERE email IS NULL;` | Установить email на основе username для пользователей без email. | Использование `CONCAT`. |
| 98 | Эксперт | `SELECT p.title FROM Posts p WHERE p.id IN (SELECT post_id FROM Comments c JOIN Users u ON c.user_id = u.id WHERE u.join_date > '2025-01-01');` | Найти посты с комментариями новых пользователей. | `JOIN` в подзапросе. |
| 99 | Эксперт | `WITH RECURSIVE user_activity AS (SELECT user_id, COUNT(*) AS activity_count FROM (SELECT user_id FROM Comments UNION ALL SELECT user_id FROM Reactions) AS actions GROUP BY user_id) SELECT u.username, ua.activity_count FROM Users u JOIN user_activity ua ON u.id = ua.user_id;` | Подсчитать общее количество действий пользователей (комментарии + реакции). | Рекурсивный CTE с `UNION ALL`. |
| 100 | Эксперт | `SELECT t.title, g.name, (SELECT COUNT(*) FROM Reactions r WHERE r.track_id = t.id AND r.created_at >= NOW() - INTERVAL '30 days') AS recent_likes FROM Tracks t JOIN Genres g ON t.genre_id = g.id ORDER BY recent_likes DESC LIMIT 10;` | Найти 10 треков с наибольшим количеством лайков за последние 30 дней. | Сложный запрос с подзапросом и сортировкой. |
Примечания