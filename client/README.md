# Police Radar Project: Motion Estimation from Monocular Sequences

Acest proiect își propune să creeze un sistem automatizat de detectare și monitorizare a vehiculelor folosind secvențe video monoculare. Sistemul poate identifica mașini în mișcare, calcula viteza acestora și genera rapoarte detaliate în format JSON. Proiectul este destinat utilizării de către forțele de ordine pentru monitorizarea traficului și aplicarea amenzilor în cazul depășirii limitelor de viteză.

---

## Caracteristici Principale

-   **Detecție Vehicule**: Identificarea precisă a vehiculelor în mișcare pe baza fluxurilor video monoculare.
-   **Estimare Viteză**: Calcularea vitezei fiecărui vehicul detectat în timp real.
-   **Urmărire Vehicule**: Atribuirea unui ID unic fiecărui vehicul pentru monitorizare continuă.
-   **Logare și Raportare**: Generarea de rapoarte detaliate în format JSON, incluzând viteza vehiculului și aplicabilitatea amenzilor.
-   **Interfață User-Friendly**: O interfață intuitivă pentru încărcarea videoclipurilor și vizualizarea rezultatelor.

---

## Etape de Dezvoltare

### 1. Etapa Intermediară

-   Identificarea obiectelor în mișcare și încadrarea acestora cu dreptunghiuri de dimensiunea aproximativă a unei mașini.
-   Ajustarea dinamică a dimensiunilor dreptunghiurilor în funcție de mișcarea vehiculului detectat.
-   Implementarea unui algoritm de urmărire pentru menținerea consistenței detecției vehiculului pe parcursul videoclipului.

### 2. Etapa Finală

-   Detectarea precisă a vehiculelor și ajustarea dimensiunilor dreptunghiurilor pentru a reflecta corect conturul fiecărui vehicul.
-   Estimarea vitezei fiecărei mașini detectate.
-   Atribuirea unui ID unic fiecărui vehicul pentru identificare pe termen lung.
-   Logarea vitezei fiecărui vehicul împreună cu ID-ul unic asociat.
-   Generarea unui raport în format JSON, indicând dacă vehiculul respectiv a depășit limita de viteză și dacă este aplicabilă o amendă.
-   Optimizarea performanței sistemului pentru procesarea rapidă a videoclipurilor de mari dimensiuni.
-   Implementarea unor mecanisme de verificare a acurateței detecției și estimării vitezei.
-   Integrarea sistemului cu baze de date existente pentru stocarea și gestionarea rapoartelor generate.
-   Crearea de notificări automate pentru vehiculele care depășesc limitele de viteză.
-   Asigurarea securității datelor procesate și protecția informațiilor sensibile.

---

Instalare și Configurare
Pre-rechizite
Python 3.8+
Node.js și npm
Git

1. Clonarea Proiectului
   bash
   Copy code
   git clone https://github.com/username/police-radar.git
   cd police-radar
2. Configurarea Backend-ului
   Backend-ul este construit folosind Flask. Urmează pașii de mai jos pentru a-l configura și rula:

a. Navighează în directorul backend
bash
Copy code
cd backend
b. Creează și activează un mediu virtual
bash
Copy code
python -m venv venv

# Activează mediul virtual:

# Pe Windows:

venv\Scripts\activate

# Pe Linux/Mac:

source venv/bin/activate
c. Instalează dependențele
bash
Copy code
pip install -r requirements.txt
d. Rulează backend-ul
bash
Copy code
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "index.py"
Notă: Asigură-te că fișierul principal al backend-ului este index.py. Dacă este altul, înlocuiește index.py cu numele corect al fișierului.

3. Configurarea Frontend-ului
   Frontend-ul este dezvoltat folosind React. Urmează pașii de mai jos pentru a-l configura și rula:

a. Navighează în directorul client
bash
Copy code
cd ../client
b. Instalează dependențele
bash
Copy code
npm install
c. Rulează aplicația React
bash
Copy code
npm run dev

Aplicația va fi disponibilă de obicei la http://localhost:5173.
