# Команды по Bootstrap 5

**Вот таблица с часто используемыми классами и атрибутами Bootstrap 5, которые помогут быстро создавать элементы интерфейса. Я сосредоточусь на наиболее популярных командах для кнопок, навигации, форм, сетки и утилит.**


| Категория       | Класс/Атрибут                              | Описание                                           | Пример                                                                 |
|-----------------|--------------------------------------------|----------------------------------------------------|----------------------------------------------------------------------|
| **Кнопки**      | `.btn`                                     | Базовый стиль кнопки                               | `<button class="btn">Кнопка</button>`                                |
|                 | `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`, `.btn-warning`, `.btn-info`, `.btn-light`, `.btn-dark` | Цветовые варианты кнопок                            | `<button class="btn btn-primary">Primary</button>`                    |
|                 | `.btn-outline-*`                           | Кнопка с контуром                                  | `<button class="btn btn-outline-primary">Outline</button>`            |
|                 | `.btn-lg`, `.btn-sm`                       | Размеры кнопок (большая, маленькая)                | `<button class="btn btn-primary btn-lg">Large</button>`              |
|                 | `disabled`                                 | Отключает кнопку                                   | `<button class="btn btn-primary" disabled>Disabled</button>`          |
||
| **Навигация**   | `.navbar`                                  | Контейнер для навигационной панели                 | `<nav class="navbar navbar-expand-lg bg-light">...</nav>`             |
|                 | `.navbar-toggler`                          | Кнопка для сворачивания меню                       | `<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav"><span class="navbar-toggler-icon"></span></button>` |
|                 | `.collapse.navbar-collapse`                | Сворачиваемый контейнер меню                       | `<div class="collapse navbar-collapse" id="nav">...</div>`           |
|                 | `.nav-link`                                | Ссылка в навигации                                 | `<a class="nav-link" href="#">Link</a>`                              |
||
| **Сетка**       | `.container`, `.container-fluid`           | Контейнеры для контента (фиксированный или на всю ширину) | `<div class="container">Content</div>`                        |
|                 | `.row`                                     | Строка для колонок                                 | `<div class="row">...</div>`                                         |
|                 | `.col`, `.col-*`, `.col-*-*`              | Колонки (авто, фиксированные, адаптивные)          | `<div class="col-md-6">Column</div>`                                 |
|                 | `.g-*`                                     | Отступы между колонками (gutter)                   | `<div class="row g-3">...</div>`                                     |
||
| **Формы**       | `.form-control`                            | Стили для полей ввода                              | `<input type="text" class="form-control">`                           |
|                 | `.form-label`                              | Метка для полей формы                              | `<label class="form-label">Label</label>`                            |
|                 | `.form-select`                             | Стили для выпадающего списка                       | `<select class="form-select"><option>Option</option></select>`       |
|                 | `.form-check`, `.form-check-input`, `.form-check-label` | Чекбоксы и радио-кнопки                    | `<input type="checkbox" class="form-check-input" id="check"><label class="form-check-label" for="check">Check</label>` |
||
| **Утилиты**     | `.m-*`, `.p-*`                             | Отступы (margin, padding)                          | `<div class="m-3 p-2">Content</div>`                                |
|                 | `.text-*`                                  | Выравнивание и стили текста                        | `<p class="text-center text-primary">Text</p>`                       |
|                 | `.bg-*`                                    | Цвет фона                                          | `<div class="bg-light">Background</div>`                             |
|                 | `.d-*`                                     | Управление отображением (display)                  | `<div class="d-none d-md-block">Visible on md+</div>`                |
|                 | `.w-*`, `.h-*`                             | Ширина и высота                                    | `<div class="w-50 h-100">50% width</div>`                           |
||
| **Модальные окна** | `.modal`                                | Контейнер модального окна                          | `<div class="modal fade" id="modal">...</div>`                       |
|                 | `data-bs-toggle="modal"`, `data-bs-target="#id"` | Открытие модального окна                     | `<button class="btn" data-bs-toggle="modal" data-bs-target="#modal">Open</button>` |
||
| **Алерты**      | `.alert`, `.alert-*`                       | Стили для уведомлений                              | `<div class="alert alert-success">Success!</div>`                    |
|                 | `.alert-dismissible`                       | Уведомление с кнопкой закрытия                     | `<div class="alert alert-danger alert-dismissible"><button type="button" class="btn-close" data-bs-dismiss="alert"></button>Message</div>` |


---

## *Подключение Bootstrap*
```
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
```

* **Адаптивность: Используйте суффиксы `-sm`, `-md`, `-lg`, `-xl`, `-xxl` для адаптивных стилей (например, `col-md-6`, `d-md-none`).**  
* **Интерактивность: Для компонентов вроде `navbar-toggler`,` modal`, `collapse` требуется JavaScript Bootstrap.**  
* **Кастомизация: Используйте утилитные классы для быстрого изменения стилей или создавайте свои через CSS.**  