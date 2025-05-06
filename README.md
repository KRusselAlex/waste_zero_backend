![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)


# 🌿 Waste Zero E-commerce Backend API

## 📖 Description

Ce projet est le backend d’un système **e-commerce** pour la plateforme Waste Zero.  
Il permet de :
- vendre des articles de seconde main,
- gérer des dons d’objets ou de vêtements,
- suivre les commandes,
- connecter vendeurs, acheteurs et donateurs.

---

## 🔧 Technologies et packages utilisés

- **Django** → Framework web principal
- **Django REST Framework (DRF)** → Création de l’API REST
- **drf-yasg** → Documentation Swagger / Redoc automatique
- **djangorestframework-simplejwt** → Authentification JWT
- **django-cors-headers** → Gestion des requêtes frontend (Next.js, React, etc.)
- **django-environ** → Gestion des variables d’environnement (.env)
- **django-filter** → Filtrage et recherche API
- **psycopg2-binary** → Connexion PostgreSQL
- **gunicorn** → Serveur WSGI pour déploiement
- **whitenoise** → Gestion des fichiers statiques en production

---

## 📦 Installation

1. Cloner le repo :
   ```bash
   git clone https://github.com/ton-username/wastezero-backend.git
   cd wastezero-backend
````

2. Créer et activer l’environnement virtuel :

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Créer le fichier `.env` :

   ```
   DEBUG=True
   SECRET_KEY=ta_cle_secrete
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgres://username:password@localhost:5432/wastezero_db
   ```

5. Appliquer les migrations :

   ```bash
   python manage.py migrate
   ```

6. Créer un superutilisateur :

   ```bash
   python manage.py createsuperuser
   ```

7. Lancer le serveur :

   ```bash
   python manage.py runserver
   ```

---

## 🛣️ Endpoints principaux

* `/api/auth/` → Login / refresh / logout JWT
* `/api/users/` → Gestion utilisateurs
* `/api/products/` → Produits en vente
* `/api/donations/` → Objets en don
* `/api/orders/` → Commandes clients
* `/api/payments/` → Paiements (Momo, Orange Money)
* `/swagger/` → Documentation Swagger
* `/redoc/` → Documentation Redoc

---

## ⚙️ Documentation API

Accès via navigateur après avoir lancé le serveur :

* Swagger : [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
* Redoc : [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## 📂 Structure recommandée du projet

```
/wastezero
    /users         → Authentification, profils
    /products      → Produits, catégories
    /donations     → Gestion des dons
    /orders        → Commandes, statuts
    /payments      → Intégration paiements Momo, Orange Money
    /core         → Paramètres globaux
    manage.py
requirements.txt
.env
```

---

## 📜 Exemple de requirements.txt

```
Django>=4.2
djangorestframework
drf-yasg
djangorestframework-simplejwt
django-cors-headers
django-environ
django-filter
psycopg2-binary
gunicorn
whitenoise
```

---

## 💡 Fonctionnalités clés

✅ Gestion des utilisateurs et des rôles
✅ Catalogue de produits à vendre et à donner
✅ Suivi des commandes et paiements
✅ Authentification sécurisée JWT
✅ Documentation API interactive
✅ Intégration avec Momo / Orange Money (prévu)

---

## 🤝 Contribution

Les contributions sont les bienvenues !
Merci de créer une issue avant de soumettre une PR.

---

## 📄 Licence

Projet sous licence [MIT](LICENSE).

```

