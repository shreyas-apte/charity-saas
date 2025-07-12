# Charity Management SaaS

This document provides a complete guide to setting up and running the MVP of the Charity Management SaaS platform.

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python (3.8 or newer)
- pip (Python package installer)
- PostgreSQL (and a running PostgreSQL server)

## 2. Database Setup

You need to create a PostgreSQL database for this project.

1.  Open your PostgreSQL command-line interface (like `psql`).
2.  Create a new database. You can name it whatever you like, for this example, we'll use `charity_db`.
    ```sql
    CREATE DATABASE charity_db;
    ```
3.  Create a database user and grant it privileges. Replace `your_user` and `your_password` with your desired credentials.
    ```sql
    CREATE USER your_user WITH PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE charity_db TO your_user;
    ALTER ROLE your_user SET client_encoding TO 'utf8';
    ALTER ROLE your_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE your_user SET timezone TO 'UTC';
    ```

## 3. Project Setup

Follow these steps to create the Django project and install dependencies.

1.  **Create a project directory and navigate into it:**
    ```bash
    mkdir charity_saas
    cd charity_saas
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install necessary Python packages:**
    ```bash
    pip install Django psycopg2-binary django-tenants
    ```

4.  **Create the Django project:**
    ```bash
    django-admin startproject charity_project .
    ```

5.  **Create the required Django apps:**
    ```bash
    python manage.py startapp tenants
    python manage.py startapp campaigns
    python manage.py startapp donors
    python manage.py startapp public
    ```

## 4. Code Implementation

Now, you will populate the files with the code provided below.

### 4.1. `charity_project/settings.py`

Replace the entire content of this file with the following code. **Remember to update the `DATABASES` section with your PostgreSQL credentials.**

```python
# In charity_project/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-mvp-secret-key-for-demonstration'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
SHARED_APPS = [
    'django_tenants',
    'public', # App for public schema
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tenants', # App for tenant management
]

TENANT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'campaigns',
    'donors',
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'charity_project.urls'
PUBLIC_SCHEMA_URLCONF = 'public.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'charity_project.wsgi.application'

# !!! IMPORTANT: Update with your PostgreSQL credentials !!!
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'charity_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

### 4.2. `tenants/models.py`

```python
# In tenants/models.py

from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

class Domain(DomainMixin):
    pass
```

### 4.3. `campaigns/models.py`

```python
# In campaigns/models.py

from django.db import models

class Campaign(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    goal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

### 4.4. `donors/models.py`

```python
# In donors/models.py

from django.db import models

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    total_donated = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name
```

### 4.5. `public/views.py`

```python
# In public/views.py

from django.shortcuts import render
from tenants.models import Client

def home(request):
    clients = Client.objects.all()
    return render(request, 'public/home.html', {'clients': clients})
```

### 4.6. `campaigns/views.py`

```python
# In campaigns/views.py

from django.shortcuts import render
from .models import Campaign
from donors.models import Donor

def dashboard(request):
    campaigns = Campaign.objects.all()
    donors = Donor.objects.all()
    tenant = request.tenant
    return render(request, 'tenant/dashboard.html', {
        'campaigns': campaigns,
        'donors': donors,
        'tenant': tenant
    })
```

### 4.7. URL Configuration

#### `charity_project/urls.py`
```python
# In charity_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # The public schema URL will be handled by public.urls
]
```

#### `public/urls.py`
```python
# In public/urls.py

from django.urls import path
from .views import home

urlpatterns = [
    path('', home, name='public_home'),
]
```

#### `campaigns/urls.py`
Create a new file `campaigns/urls.py` and add the following:
```python
# In campaigns/urls.py

from django.urls import path
from .views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
]
```

### 4.8. Templates

Create a `templates` directory in your project's root folder. Inside `templates`, create a `public` folder and a `tenant` folder.

#### `templates/base.html`
Create a `base.html` file in the `templates` directory.
```html
<!-- In templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Charity SaaS{% endblock %}</title>
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap)" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-50">
    <div class="min-h-screen">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

#### `templates/public/home.html`
```html
<!-- In templates/public/home.html -->
{% extends 'base.html' %}

{% block title %}Welcome - Charity SaaS Platform{% endblock %}

{% block content %}
<div class="bg-white">
    <header class="absolute inset-x-0 top-0 z-50">
      <nav class="flex items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div class="flex lg:flex-1">
          <a href="#" class="-m-1.5 p-1.5">
            <span class="text-xl font-bold text-indigo-600">CharitySaaS</span>
          </a>
        </div>
        <div class="lg:flex lg:flex-1 lg:justify-end">
          <a href="#" class="text-sm font-semibold leading-6 text-gray-900">Log in <span aria-hidden="true">&rarr;</span></a>
        </div>
      </nav>
    </header>

    <div class="relative isolate px-6 pt-14 lg:px-8">
      <div class="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
        <div class="text-center">
          <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">A Better Way to Manage Your Charity</h1>
          <p class="mt-6 text-lg leading-8 text-gray-600">Our SaaS platform provides all the tools you need to run successful campaigns, manage donors, and organize volunteers, all in one place.</p>
          <div class="mt-10 flex items-center justify-center gap-x-6">
            <a href="#" class="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Get started</a>
            <a href="#" class="text-sm font-semibold leading-6 text-gray-900">Learn more <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </div>
    </div>
</div>

<div class="bg-gray-50 py-12">
    <div class="mx-auto max-w-4xl px-6 lg:px-8">
        <h2 class="text-center text-2xl font-bold leading-8 text-gray-900">Our Active Charity Organizations</h2>
        <div class="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {% for client in clients %}
            <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow">
                <h3 class="text-lg font-semibold text-indigo-600">{{ client.name }}</h3>
                <p class="mt-2 text-sm text-gray-600">Joined on: {{ client.created_on }}</p>
                {% for domain in client.domains.all %}
                <a href="http://{{ domain.domain }}:8000" target="_blank" class="mt-4 inline-block text-sm font-semibold text-indigo-500 hover:text-indigo-700">
                    Visit Dashboard &rarr;
                </a>
                {% endfor %}
            </div>
            {% empty %}
            <p class="text-center text-gray-500 col-span-full">No organizations have signed up yet.</p>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
```

#### `templates/tenant/dashboard.html`
```html
<!-- In templates/tenant/dashboard.html -->
{% extends 'base.html' %}

{% block title %}Dashboard - {{ tenant.name }}{% endblock %}

{% block content %}
<div class="min-h-full">
  <nav class="bg-indigo-600">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <h1 class="text-2xl font-bold text-white">{{ tenant.name }}</h1>
          </div>
        </div>
        <div class="flex items-center">
            <a href="http://localhost:8000" class="text-sm font-medium text-indigo-200 hover:text-white">Back to Main Site</a>
        </div>
      </div>
    </div>
  </nav>

  <header class="bg-white shadow-sm">
    <div class="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
      <h1 class="text-lg font-semibold leading-6 text-gray-900">Dashboard</h1>
    </div>
  </header>

  <main>
    <div class="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <!-- Campaigns Section -->
        <div>
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Campaign Management</h2>
          <div class="bg-white p-6 rounded-lg shadow">
            <ul role="list" class="divide-y divide-gray-200">
              {% for campaign in campaigns %}
              <li class="py-4">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-md font-medium text-indigo-600">{{ campaign.name }}</p>
                        <p class="text-sm text-gray-500">{{ campaign.description|truncatewords:10 }}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-md font-semibold text-gray-900">${{ campaign.goal }}</p>
                        <p class="text-sm text-gray-500">Goal</p>
                    </div>
                </div>
                <!-- AI Placeholder -->
                <div class="mt-2">
                    <button disabled class="text-xs bg-gray-200 text-gray-500 font-semibold py-1 px-2 rounded-full cursor-not-allowed">
                        AI: Predict Success
                    </button>
                </div>
              </li>
              {% empty %}
              <p class="text-gray-500">No campaigns created yet.</p>
              {% endfor %}
            </ul>
          </div>
        </div>

        <!-- Donors Section -->
        <div>
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Donor Management</h2>
          <div class="bg-white p-6 rounded-lg shadow">
            <ul role="list" class="divide-y divide-gray-200">
              {% for donor in donors %}
              <li class="py-4">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-md font-medium text-gray-900">{{ donor.name }}</p>
                        <p class="text-sm text-gray-500">{{ donor.email }}</p>
                    </div>
                     <div class="text-right">
                        <p class="text-md font-semibold text-gray-900">${{ donor.total_donated }}</p>
                        <p class="text-sm text-gray-500">Total Donated</p>
                    </div>
                </div>
                 <!-- AI Placeholder -->
                <div class="mt-2">
                    <button disabled class="text-xs bg-gray-200 text-gray-500 font-semibold py-1 px-2 rounded-full cursor-not-allowed">
                        AI: Predict Churn Risk
                    </button>
                </div>
              </li>
              {% empty %}
              <p class="text-gray-500">No donors added yet.</p>
              {% endfor %}
            </ul>
          </div>
        </div>

      </div>
    </div>
  </main>
</div>
{% endblock %}
```

## 5. Running the Application

After setting up the project and code, run these commands from your project's root directory.

1.  **Run migrations for the public schema:**
    This command sets up the tables needed for tenant management in the `public` schema.
    ```bash
    python manage.py migrate_schemas --shared
    ```

2.  **Create a superuser for the public schema:**
    This user will be able to access the Django admin for the public site.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create a username, email, and password.

3.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    Your public-facing site is now running at `http://localhost:8000`. You can visit this URL in your browser to see the main landing page.

## 6. Creating and Accessing Tenants

Now, let's create a couple of tenants (charity organizations) to demonstrate the multi-tenancy.

1.  **Open the Django shell:**
    ```bash
    python manage.py shell
    ```

2.  **Inside the shell, run the following Python code to create two tenants:**

    ```python
    from tenants.models import Client, Domain

    # --- Create Tenant 1: "Hope Foundation" ---
    # The schema_name will be used for the PostgreSQL schema.
    tenant1 = Client(schema_name='hope', name='Hope Foundation')
    tenant1.save()

    # The domain is how we'll access this tenant's site.
    domain1 = Domain()
    domain1.domain = 'hope.localhost' # We use .localhost for local development
    domain1.tenant = tenant1
    domain1.is_primary = True
    domain1.save()

    # --- Create Tenant 2: "Green Earth Org" ---
    tenant2 = Client(schema_name='greenearth', name='Green Earth Org')
    tenant2.save()

    domain2 = Domain()
    domain2.domain = 'greenearth.localhost'
    domain2.tenant = tenant2
    domain2.is_primary = True
    domain2.save()

    print("Tenants created successfully!")
    ```

3.  **Exit the shell** by typing `exit()` and pressing Enter.

4.  **Edit your computer's `hosts` file** to resolve your new domains.
    * **macOS/Linux:** Open `/etc/hosts` with sudo privileges (e.g., `sudo nano /etc/hosts`).
    * **Windows:** Open `C:\Windows\System32\drivers\etc\hosts` as an administrator.

    Add the following lines to the file:
    ```
    127.0.0.1 hope.localhost
    127.0.0.1 greenearth.localhost
    ```
    Save the file. This tells your computer to direct requests for these domains to your local machine.

5.  **Access the tenant dashboards:**
    * Restart your development server if it's not running (`python manage.py runserver`).
    * Visit `http://hope.localhost:8000` in your browser.
    * Visit `http://greenearth.localhost:8000` in your browser.

    You will see the dashboard for each respective organization. The data (campaigns, donors) for each tenant is completely isolated.

## 7. Adding Data (Optional)

You can add campaigns and donors for each tenant via the Django admin.

1.  For each tenant, you need to create a superuser. Use the `create_tenant_superuser` command:
    ```bash
    python manage.py create_tenant_superuser --schema=hope
    python manage.py create_tenant_superuser --schema=greenearth
    ```
    Follow the prompts for each.

2.  Register your models in `campaigns/admin.py` and `donors/admin.py`.
    ```python
    # In campaigns/admin.py
    from django.contrib import admin
    from .models import Campaign
    admin.site.register(Campaign)

    # In donors/admin.py
    from django.contrib import admin
    from .models import Donor
    admin.site.register(Donor)
    ```

3.  Now you can log in to the admin panel for each tenant at `http://hope.localhost:8000/admin` and `http://greenearth.localhost:8000/admin` to add data. The data you add will only appear on that tenant's dashboard.
