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
