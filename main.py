from datetime import date
from typing import List, Tuple, Dict


# --- Часть A. Функции ---

def normalize_addresses(value: str) -> str:
    """
    Возвращает значение, в котором адрес приведен к нижнему регистру и очищен от пробелов по краям.
    """
    return value.strip().lower()


def add_short_body(email: dict) -> dict:
    """
    Возвращает email с новым ключом email["short_body"] — первые 10 символов тела письма + "...".
    """
    body = email.get("body", "")
    short_body = body[:10] + "..." if len(body) > 10 else body
    email["short_body"] = short_body
    return email


def clean_body_text(body: str) -> str:
    """
    Заменяет табы и переводы строк на пробелы.
    """
    return body.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def build_sent_text(email: dict) -> str:
    """
    Формирует текст письма в формате:
    Кому: {to}, от {from}
    Тема: {subject}, дата {date}
    {clean_body}
    """
    return (
        f"Кому: {email['recipient']}, от {email['sender']}\n"
        f"Тема: {email['subject']}, дата {email['date']}\n"
        f"{email['clean_body']}"
    )


def check_empty_fields(subject: str, body: str) -> Tuple[bool, bool]:
    """
    Возвращает кортеж (is_subject_empty, is_body_empty).
    True, если поле пустое.
    """
    is_subject_empty = not subject.strip()
    is_body_empty = not body.strip()
    return is_subject_empty, is_body_empty


def mask_sender_email(login: str, domain: str) -> str:
    """
    Возвращает маску email: первые 2 символа логина + "***@" + домен.
    """
    masked_login = login[:2] + "***" if len(login) > 2 else login + "***"
    return f"{masked_login}@{domain}"


def get_correct_email(email_list: List[str]) -> List[str]:
    """
    Возвращает список корректных email.
    Адрес считается корректным, если:
    - содержит символ @;
    - оканчивается на один из доменов: .com, .ru, .net.
    """
    valid_domains = {".com", ".ru", ".net"}
    correct_emails = []
    for email in email_list:
        if "@" not in email:
            continue
        parts = email.split("@")
        if len(parts) != 2:
            continue
        domain = parts[1]
        if any(domain.endswith(d) for d in valid_domains):
            correct_emails.append(email)
    return correct_emails


def create_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    """
    Создает словарь email с базовыми полями: 'sender', 'recipient', 'subject', 'body'
    """
    return {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }


def add_send_date(email: dict) -> dict:
    """
    Возвращает email с добавленным ключом email["date"] — текущая дата в формате YYYY-MM-DD.
    """
    email["date"] = date.today().strftime("%Y-%m-%d")
    return email


def extract_login_domain(address: str) -> Tuple[str, str]:
    """
    Возвращает логин и домен отправителя.
    Пример: "user@mail.ru" -> ("user", "mail.ru")
    """
    if "@" not in address:
        raise ValueError("Invalid email format")
    login, domain = address.split("@", 1)
    return login, domain


# --- Часть B. Отправка письма ---

def sender_email(
    recipient_list: List[str],
    subject: str,
    message: str,
    *,
    sender: str = "default@study.com"
) -> List[dict]:
    """
    Функция отправки письма с валидацией и обработкой.
    Принимает список получателей, тему, сообщение и отправителя (по умолчанию default@study.com).

    Возвращает список готовых писем (словарей) с обработанными данными.
    """
    # 1. Проверить, что recipient_list не пустой
    if not recipient_list:
        return []

    # 2. Проверить корректность email отправителя и получателей через get_correct_email()
    all_emails = [sender] + recipient_list
    correct_emails = get_correct_email(all_emails)

    # Если отправитель некорректен — вернуть пустой список
    if sender not in correct_emails:
        return []

    # Оставить только корректных получателей
    valid_recipients = [email for email in recipient_list if email in correct_emails]

    # 3. Проверить пустоту темы и тела письма через check_empty_fields()
    is_subject_empty, is_body_empty = check_empty_fields(subject, message)
    if is_subject_empty or is_body_empty:
        return []

    # 4. Исключить отправку самому себе
    valid_recipients = [email for email in valid_recipients if email != sender]

    # 5. Нормализовать: subject и body → clean_body_text(), recipient_list и sender → normalize_addresses()
    normalized_subject = clean_body_text(subject)
    normalized_body = clean_body_text(message)
    normalized_sender = normalize_addresses(sender)
    normalized_recipients = [normalize_addresses(email) for email in valid_recipients]

    # 6–10. Обработка каждого получателя
    emails = []
    for recipient in normalized_recipients:
        # 6. Создать письмо
        email = create_email(
            sender=normalized_sender,
            recipient=recipient,
            subject=normalized_subject,
            body=normalized_body
        )

        # Добавляем ключ 'clean_body' — он нужен для build_sent_text
        email["clean_body"] = normalized_body

        # 7. Добавить дату отправки
        email = add_send_date(email)

        # 8. Замаскировать email отправителя
        login, domain = extract_login_domain(normalized_sender)
        email["masked_sender"] = mask_sender_email(login, domain)

        # 9. Сохранить короткую версию тела
        email = add_short_body(email)

        # 10. Сформировать итоговый текст письма
        email["sent_text"] = build_sent_text(email)

        emails.append(email)

    return emails


# --- Пример использования ---
if __name__ == "__main__":
    test_emails = [
        "user@gmail.com",
        "admin@company.ru",
        "test_123@service.net",
        "Example.User@domain.com",
        "default@study.com",
        " hello@corp.ru ",
        "user@site.NET",
        "user@domain.coM",
        "user.name@domain.ru",
        "usergmail.com",
        "user@domain",
        "user@domain.org",
        "@mail.ru",
        "name@.com",
        "name@domain.comm",
        "",
        "   ",
    ]

    result = sender_email(
        recipient_list=test_emails,
        subject="Hello!\n\tHow are you?",
        message="Привет,\n\tколлега!\n\nС уважением.",
        sender="default@study.com"
    )

    for email in result:
        print("=" * 50)
        print(email["sent_text"])
        print("=" * 50)