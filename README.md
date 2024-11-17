<<<<<<< HEAD
# Police Radar Project: Motion Estimation from Monocular Sequences

Acest proiect își propune să creeze un sistem automatizat de detectare și monitorizare a vehiculelor folosind secvențe video monoculare. Sistemul poate identifica mașini în mișcare, calcula viteza acestora și genera rapoarte detaliate în format JSON. Este destinat utilizării de către forțele de ordine pentru monitorizarea traficului și aplicarea amenzilor în cazuri de depășire a limitelor de viteză.

---

## 📌 Caracteristici Principale

-   **Detecție Vehicule**: Identificarea precisă a vehiculelor în mișcare pe baza fluxurilor video monoculare.
-   **Estimare Viteză**: Calcularea vitezei fiecărui vehicul detectat în timp real.
-   **Urmărire Vehicule**: Atribuirea unui ID unic fiecărui vehicul pentru monitorizare continuă.
-   **Logare și Raportare**: Generarea de rapoarte detaliate în format JSON, incluzând viteza vehiculului și aplicabilitatea amenzilor.
-   **Interfață User-Friendly**: O interfață intuitivă pentru încărcarea videoclipurilor și vizualizarea rezultatelor.

---

## 🚀 Etape de Dezvoltare

### 1️⃣ Etapa Intermediară

-   Identificarea obiectelor în mișcare și încadrarea acestora cu dreptunghiuri de dimensiunea aproximativă a unei mașini.
-   Ajustarea dinamică a dimensiunilor dreptunghiurilor în funcție de mișcarea vehiculului detectat.
-   Implementarea unui algoritm de urmărire pentru menținerea consistenței detecției vehiculului pe parcursul videoclipului.

### 2️⃣ Etapa Finală

-   Detectarea precisă a vehiculelor și ajustarea dreptunghiurilor pentru a reflecta corect conturul vehiculului.
-   Estimarea vitezei fiecărui vehicul detectat.
-   Atribuirea unui ID unic fiecărui vehicul pentru identificare pe termen lung.
-   Generarea de rapoarte în format JSON, indicând:
    -   Viteza vehiculului
    -   Depășirea limitei legale și aplicabilitatea amenzilor.
-   Optimizarea performanței pentru procesarea rapidă a videoclipurilor mari.
-   Crearea de notificări automate pentru vehiculele care depășesc limitele de viteză.
-   Asigurarea securității datelor procesate.

---

## ⚙️ Instalare și Configurare

### Pre-rechizite

-   **Python** 3.8+
-   **Node.js** și **npm**
-   **Git**

### 1️⃣ Clonarea Proiectului

```bash
git clone https://github.com/username/police-radar.git
cd police-radar
```

### Instalare și Configurare

## Pre-rechizite

## Python 3.8+

## Node.js și npm

Git

### 1. Clonarea Proiectului

git clone https://github.com/username/police-radar.git
cd police-radar

### 2. Configurarea Backend-ului

Backend-ul este construit folosind Flask. Urmează pașii de mai jos pentru a-l configura și rula:

a. Navighează în directorul backend

```bash
cd backend
```

c. Instalează dependențele

```bash
pip install -r requirements.txt
```

d. Rulează backend-ul

```bash
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "index.py"
```

Notă: Asigură-te că fișierul principal al backend-ului este index.py. Dacă este altul, înlocuiește index.py cu numele corect al fișierului.

### 3. Configurarea Frontend-ului

Frontend-ul este dezvoltat folosind React. Urmează pașii de mai jos pentru a-l configura și rula:

a. Navighează în directorul client

```bash
cd ../client
```

b. Instalează dependențele

```bash
npm install
```

c. Rulează aplicația React

```bash
npm run dev
```

Aplicația va fi disponibilă de obicei la http://localhost:5173.
=======
Police Radar Project: Motion Estimation from Monocular Sequences
Acest proiect își propune să creeze un sistem automatizat de detectare și monitorizare a vehiculelor folosind secvențe video monoculare. Sistemul poate identifica mașini în mișcare, calcula viteza acestora și genera rapoarte detaliate în format JSON.

Instalare și Rulare
Cerințe preliminare
Python 3.8+
Node.js 14+
npm
Backend

cd backend
pip install -r requirements.txt
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "index.py"
Frontend

cd client
npm install
npm run dev
Etape de Dezvoltare
1. Etapa Intermediară
Identificarea obiectelor în mișcare și încadrarea acestora cu dreptunghiuri de dimensiunea aproximativă a unei mașini.
Ajustarea dinamică a dimensiunilor dreptunghiurilor în funcție de mișcarea vehiculului detectat.
2. Etapa Finală
Detectarea precisă a vehiculelor și ajustarea dimensiunilor dreptunghiurilor pentru a reflecta corect conturul fiecărui vehicul.
Estimarea vitezei fiecărei mașini detectate.
Atribuirea unui ID unic fiecărui vehicul pentru identificare pe termen lung.
Logarea vitezei fiecărui vehicul împreună cu ID-ul unic asociat.
Generarea unui raport în format JSON, indicând dacă vehiculul respectiv a depășit limita de viteză și dacă este aplicabilă o amendă.
Structura Proiectului

├── backend/
│   ├── index.py
│   └── requirements.txt
├── client/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
Exemplu de Output JSON

[
  {
    "id": "vehicle_001",
    "speed": 82,
    "fine_applicable": true
  },
  {
    "id": "vehicle_002",
    "speed": 45,
    "fine_applicable": false
  }
]
Tehnologii Utilizate
Backend: Python, Flask
Frontend: React, Vite
Procesare video: OpenCV
Comunicare: REST API
Note
Asigurați-vă că toate dependențele sunt instalate înainte de rulare
Backend-ul rulează pe portul 5000 implicit
Frontend-ul rulează pe portul 5173 implicit
Verificați fișierul requirements.txt pentru dependențele Python necesare
Contribuții
Contribuțiile sunt binevenite. Vă rugăm să creați un pull request pentru orice modificări propuse.

Licență
>>>>>>> 71383b07903f4777daca57db5c53c884af7e36e7
