const DB_NAME = 'TryageOfflineDB';
const STORE_NAME = 'triage_records';
const DB_VERSION = 1;

let db;

// Inicializar IndexedDB
const request = indexedDB.open(DB_NAME, DB_VERSION);

request.onerror = (event) => {
    console.error("Error abriendo DB:", event.target.error);
};

request.onupgradeneeded = (event) => {
    db = event.target.result;
    if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id", autoIncrement: true });
    }
};

request.onsuccess = (event) => {
    db = event.target.result;
    updatePendingCount();
};

// Guardar Registro
document.getElementById('triageForm').addEventListener('submit', (e) => {
    e.preventDefault();

    const record = {
        nombre: document.getElementById('nombre').value,
        dni: document.getElementById('dni').value,
        edad: document.getElementById('edad').value,
        genero: document.getElementById('genero').value,
        vital_signs: {
            fc: document.getElementById('fc').value,
            sat: document.getElementById('sat').value,
            tas: document.getElementById('tas').value
        },
        motivo: document.getElementById('motivo').value,
        timestamp: new Date().toISOString(),
        synced: false
    };

    const transaction = db.transaction([STORE_NAME], "readwrite");
    const store = transaction.objectStore(STORE_NAME);
    const addRequest = store.add(record);

    addRequest.onsuccess = () => {
        showMessage("✅ Registro guardado localmente", "success");
        document.getElementById('triageForm').reset();
        updatePendingCount();
    };

    addRequest.onerror = () => {
        showMessage("❌ Error al guardar", "error");
    };
});

// Actualizar contador
function updatePendingCount() {
    const transaction = db.transaction([STORE_NAME], "readonly");
    const store = transaction.objectStore(STORE_NAME);
    const countRequest = store.count();

    countRequest.onsuccess = () => {
        document.getElementById('pendingCount').innerText = countRequest.result;
    };
}

// Borrar Todo (Debug)
document.getElementById('clearBtn').addEventListener('click', () => {
    if (confirm("¿Borrar todos los registros locales?")) {
        const transaction = db.transaction([STORE_NAME], "readwrite");
        const store = transaction.objectStore(STORE_NAME);
        store.clear();
        updatePendingCount();
        showMessage("Registros borrados", "success");
    }
});

function showMessage(msg, type) {
    const el = document.getElementById('statusMessage');
    el.innerText = msg;
    el.className = type;
    setTimeout(() => {
        el.innerText = "";
        el.className = "";
    }, 3000);
}
