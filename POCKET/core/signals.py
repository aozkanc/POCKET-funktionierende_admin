import json
import random
import string
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Mitarbeiter

PASSWORD_FILE = "passwords.json"

def load_passwords():
    """JSON dosyasını yükler veya yoksa boş bir yapı oluşturur."""
    try:
        with open(PASSWORD_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}}

def save_passwords(passwords):
    """JSON dosyasına kullanıcı verilerini kaydeder."""
    with open(PASSWORD_FILE, "w", encoding="utf-8") as file:
        json.dump(passwords, file, indent=4, ensure_ascii=False)

def generate_unique_username(vorname, nachname):
    """ Kullanıcı adı oluşturur: İsimleri '-' ile birleştirir, soyisim ile '.' kullanır. """
    base_username = f"{vorname.replace(' ', '-').lower()}.{nachname.lower()}"
    username = base_username
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    return username

def generate_custom_password(vorname, nachname):
    """ Kullanıcı için özel formatta şifre üretir: 2 harf isim + 2 harf soyisim + sembol + 3 rakam """
    symbol = random.choice("!@#$%^&*")
    numbers = ''.join(random.choices(string.digits, k=3))
    password = f"{vorname.replace(' ', '')[:2].lower()}{nachname[:2].lower()}{symbol}{numbers}"
    return password

@receiver(post_save, sender=Mitarbeiter)
def create_user_for_mitarbeiter(sender, instance, created, **kwargs):
    """ Yeni bir çalışan oluşturulduğunda otomatik kullanıcı ve şifre oluşturur. """
    passwords = load_passwords()

    if created and not instance.user:
        username = generate_unique_username(instance.vorname, instance.nachname)
        raw_password = generate_custom_password(instance.vorname, instance.nachname)

        user = User.objects.create(username=username)
        user.set_password(raw_password)  # Django'nun kendi hashleme sistemini kullanarak şifreyi saklar
        user.save()

        instance.user = user
        instance.save()

        group = Group.objects.get(name=instance.rolle)
        user.groups.add(group)

        # 🔹 JSON dosyasına sadece OLUŞTURULAN İLK ŞİFREYİ kaydet
        passwords["users"][username] = {
            "password_plain": raw_password,  # Sadece ilk oluşturulan şifreyi kaydediyoruz
            "created_at": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
        }

        save_passwords(passwords)

        print(f"✅ Kullanıcı '{username}' oluşturuldu. İlk şifresi: {raw_password}")
