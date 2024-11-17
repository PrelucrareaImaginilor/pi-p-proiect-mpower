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
