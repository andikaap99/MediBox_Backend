# MediBox AI — Backend

Backend untuk sistem kotak obat pintar berbasis IoT dengan chatbot AI context-aware. Pengguna menceritakan gejala sakit, lalu sistem merekomendasikan obat yang tersedia di kotak obat mereka secara real-time.

## Fitur

- Chatbot AI yang memahami konteks obat di kotak obat pengguna
- Rekomendasi obat berdasarkan data real-time dari sensor ESP32
- RAG (Retrieval-Augmented Generation) dari dokumen referensi obat
- Multi-turn conversation dengan riwayat percakapan
- Autentikasi JWT untuk keamanan akses

## Tech Stack

- FastAPI
- Supabase (PostgreSQL)
- ChromaDB + LlamaIndex + HuggingFace Embeddings
- Groq API (Llama 3.3 70B)
- python-jose + bcrypt (autentikasi)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Isi variabel di .env
uvicorn app.main:app --reload
```

---

## Base URL

```
https://medibox.rutherweb.my.id/
```

Semua endpoint mengembalikan response dalam format **JSON** dengan `Content-Type: application/json`.

---

## API Endpoints

### 1. Health Check

Melakukan pengecekan apakah server berjalan.

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/` |
| **Auth** | Tidak |

**Response `200 OK`**

```json
{
  "status": "MediBox AI is running"
}
```

---

### 2. Register

Mendaftarkan akun pengguna baru.

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/auth/register` |
| **Auth** | Tidak |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `email` | `string` | Ya | Email unik pengguna |
| `password` | `string` | Ya | Password (akan di-hash dengan bcrypt) |
| `full_name` | `string` | Tidak | Nama lengkap (default: `""`) |

```json
{
  "email": "user@example.com",
  "password": "rahasia123",
  "full_name": "Budi Santoso"
}
```

**Response `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "full_name": "Budi Santoso"
}
```

**Response `400 Bad Request`**

```json
{
  "detail": "Email sudah terdaftar"
}
```

---

### 3. Login

Melakukan autentikasi dan mendapatkan JWT token.

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/auth/login` |
| **Auth** | Tidak |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `email` | `string` | Ya | Email yang sudah terdaftar |
| `password` | `string` | Ya | Password yang sesuai |

```json
{
  "email": "user@example.com",
  "password": "rahasia123"
}
```

**Response `200 OK`**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "full_name": "Budi Santoso"
}
```

**Response `401 Unauthorized`**

```json
{
  "detail": "Email atau password salah"
}
```

---

### 4. Chat

Mengirim pesan ke chatbot AI. Sistem akan mengambil konteks obat dari kotak obat pengguna, mengambil referensi obat dari database RAG, serta mempertimbangkan riwayat percakapan sebelumnya, lalu mengembalikan rekomendasi dari LLM.

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/chat` |
| **Auth** | Tidak* |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `user_id` | `string` | Ya | UUID pengguna (dari response register/login) |
| `message` | `string` | Ya | Pesan/ pertanyaan pengguna |

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Saya sakit kepala dan demam, obat apa yang cocok?"
}
```

**Response `200 OK`**

```json
{
  "response": "Berdasarkan gejala yang Anda ceritakan (sakit kepala dan demam), Anda bisa mengonsumsi Paramex atau Sanmol yang tersedia di kotak obat Anda. Dosis yang dianjurkan adalah 1 tablet setiap 4-6 jam. Perbanyak minum air putih dan istirahat yang cukup."
}
```

**Flow pemrosesan:**
1. Query pengguna di-embed dan dicari kemiripannya di ChromaDB (RAG)
2. Status slot obat pengguna diambil dari database
3. Riwayat percakapan terakhir (maks. 10 pesan) diambil
4. Ketiga konteks tersebut digabung menjadi system prompt untuk LLM
5. LLM menghasilkan respons yang hanya merekomendasikan obat yang tersedia di kotak

---

### 5. Get Chat History

Mengambil riwayat percakapan pengguna dengan chatbot (maks. 10 pesan terakhir, urut dari yang paling lama).

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/chat/history/{user_id}` |
| **Auth** | Tidak* |

**Path Parameter**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `user_id` | `string` | Ya | UUID pengguna |

**Response `200 OK`**

```json
{
  "history": [
    {
      "user_message": "Saya sakit kepala",
      "bot_response": "Untuk sakit kepala, Anda bisa minum Paramex atau Sanmol..."
    },
    {
      "user_message": "Berapa dosisnya?",
      "bot_response": "Dosis yang dianjurkan adalah 1 tablet setiap 4-6 jam..."
    }
  ]
}
```

---

### 6. Update Sensor Data

Endpoint untuk menerima data dari sensor ESP32 pada kotak obat pintar. Sensor mendeteksi apakah suatu slot obat terisi atau kosong. Jika slot belum ada, akan dibuat otomatis.

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/sensor/update` |
| **Auth** | Tidak* |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `user_id` | `string` | Ya | UUID pengguna pemilik kotak obat |
| `slot_label` | `string` | Ya | Label slot (misal: `"A"`, `"B"`, `"C"`) |
| `is_filled` | `boolean` | Ya | `true` = terisi obat, `false` = kosong |

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "slot_label": "A",
  "is_filled": true
}
```

**Response `200 OK`**

```json
{
  "status": "ok"
}
```

**Catatan:**
- Data sensor akan di-upsert ke tabel `slots` (update jika slot sudah ada, insert jika baru)
- Setiap pembaruan selalu tercatat ke tabel `slot_history` sebagai audit trail

---

### 7. Get All Slots

Mengambil semua slot obat beserta statusnya untuk pengguna tertentu.

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/slots/{user_id}` |
| **Auth** | Tidak* |

**Path Parameter**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `user_id` | `string` | Ya | UUID pengguna |

**Response `200 OK`**

```json
{
  "slots": [
    {
      "id": "slot-uuid-1",
      "slot_label": "A",
      "medicine_name": "Paramex",
      "is_filled": true
    },
    {
      "id": "slot-uuid-2",
      "slot_label": "B",
      "medicine_name": "Sanmol",
      "is_filled": false
    }
  ]
}
```

| Field | Tipe | Keterangan |
|-------|------|------------|
| `id` | `string (uuid)` | ID unik slot di database |
| `slot_label` | `string` | Label slot pada kotak obat |
| `medicine_name` | `string` | Nama obat yang ditugaskan ke slot (kosong jika belum dikonfigurasi) |
| `is_filled` | `boolean` | Status pengisian dari sensor |

---

### 8. Add Slot

Menambahkan slot obat baru ke kotak obat pengguna.

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/slots/{user_id}` |
| **Auth** | Tidak* |

**Path Parameter**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `user_id` | `string` | Ya | UUID pengguna |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `slot_label` | `string` | Ya | Label slot (misal: `"A"`, `"B"`, `"C"`) |
| `medicine_name` | `string` | Tidak | Nama obat (default: `""`) |

```json
{
  "slot_label": "D",
  "medicine_name": "Entrostop"
}
```

**Response `200 OK`**

```json
{
  "status": "ok",
  "slot": {
    "id": "slot-uuid-3",
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "slot_label": "D",
    "medicine_name": "Entrostop",
    "is_filled": false
  }
}
```

**Response `400 Bad Request`**

```json
{
  "detail": "Slot D sudah ada untuk user ini"
}
```

**Catatan:**
- Slot baru akan dibuat dengan status `is_filled: false` (kosong) secara default
- `slot_label` harus unik per pengguna

---

### 9. Configure Slot

Mengubah nama obat yang ditugaskan ke suatu slot.

| | |
|---|---|
| **Method** | `PUT` |
| **Endpoint** | `/slots/{slot_id}/config` |
| **Auth** | Tidak* |

**Path Parameter**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `slot_id` | `string` | Ya | ID slot (UUID, dari response GET slots) |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `medicine_name` | `string` | Ya | Nama obat baru untuk slot ini |

```json
{
  "medicine_name": "Promag"
}
```

**Response `200 OK`**

```json
{
  "status": "ok"
}
```

---

### 10. Update Profile

Memperbarui data profil pengguna (nama, email, atau password).

| | |
|---|---|
| **Method** | `PUT` |
| **Endpoint** | `/auth/profile/{user_id}` |
| **Auth** | Tidak* |

**Path Parameter**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `user_id` | `string` | Ya | UUID pengguna |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `full_name` | `string` | Tidak | Nama lengkap baru |
| `email` | `string` | Tidak | Email baru (harus unik) |
| `password` | `string` | Tidak | Password baru (akan di-hash) |

```json
{
  "full_name": "Budi Santoso",
  "email": "budi@example.com"
}
```

**Response `200 OK`**

```json
{
  "status": "ok"
}
```

**Response `400 Bad Request`**

```json
{
  "detail": "Email sudah digunakan oleh pengguna lain"
}
```

```json
{
  "detail": "Tidak ada data yang diperbarui"
}
```

**Response `404 Not Found`**

```json
{
  "detail": "User tidak ditemukan"
}
```

**Catatan:**
- Semua field bersifat opsional, kirim hanya yang ingin diubah
- Jika mengubah email, sistem akan mengecek keunikannya
- Jika mengubah password, password akan di-hash ulang dengan bcrypt

---

### 11. Get Device by MAC Address

Mengambil data perangkat ESP32 berdasarkan MAC address. Berguna saat pengguna tidak mengetahui `user_id` tetapi mengetahui MAC address perangkatnya.

| | |
|---|---|
| **Method** | `GET` |
| **Endpoint** | `/device/{mac_address}` |
| **Auth** | Tidak* |

**Path Parameter**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `mac_address` | `string` | Ya | MAC address perangkat ESP32 |

**Response `200 OK` (ada device)**

```json
{
  "device": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "device_name": "MediBox Ruang Tamu",
    "created_at": "2026-07-10T12:00:00Z"
  }
}
```

**Response `200 OK` (belum ada device)**

```json
{
  "device": null
}
```

---

### 12. Register / Update Device

Mendaftarkan atau memperbarui perangkat ESP32 milik pengguna. MAC address disimpan langsung di tabel `users`, sehingga satu akun otomatis hanya bisa memiliki satu perangkat.

| | |
|---|---|
| **Method** | `POST` |
| **Endpoint** | `/device` |
| **Auth** | Tidak* |

**Request Body**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `user_id` | `string` | Ya | UUID pengguna pemilik perangkat |
| `mac_address` | `string` | Ya | MAC address perangkat ESP32 |
| `device_name` | `string` | Tidak | Nama/label perangkat (default: `""`) |

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "device_name": "MediBox Ruang Tamu"
}
```

**Response `200 OK`**

```json
{
  "status": "ok",
  "device": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "device_name": "MediBox Ruang Tamu",
    "created_at": "2026-07-10T12:00:00Z"
  }
}
```

**Catatan:**
- MAC address akan dinormalisasi ke huruf besar sebelum disimpan
- Data device tersimpan langsung di tabel `users`, cukup update kolom `mac_address` dan `device_name`
- `user_id` dapat diperoleh dari endpoint GET `/device/{mac_address}` atau dari response login

---

### 13. Delete Device

Menghapus perangkat ESP32 milik pengguna berdasarkan MAC address.

| | |
|---|---|
| **Method** | `DELETE` |
| **Endpoint** | `/device/{mac_address}` |
| **Auth** | Tidak* |

**Path Parameter**

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|------------|
| `mac_address` | `string` | Ya | MAC address perangkat ESP32 |

**Response `200 OK`**

```json
{
  "status": "ok"
}
```

---

## Struktur Database

### Tabel `users`

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | `uuid` | Primary key |
| `email` | `text` | Unique, email pengguna |
| `password` | `text` | Password bcrypt-hashed |
| `full_name` | `text` | Nama lengkap |
| `mac_address` | `text` | Unique, nullable — MAC address perangkat ESP32 |
| `device_name` | `text` | Nama/label perangkat (default `''`) |
| `created_at` | `timestamptz` | Waktu pendaftaran |

### Tabel `slots`

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | `uuid` | Primary key |
| `user_id` | `uuid` | Foreign key → `users.id` |
| `slot_label` | `text` | Label slot (A, B, C, dst.) |
| `medicine_name` | `text` | Nama obat di slot |
| `is_filled` | `boolean` | Status terisi/kosong dari sensor |

### Tabel `slot_history`

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | `uuid` | Primary key |
| `user_id` | `uuid` | Foreign key → `users.id` |
| `slot_label` | `text` | Label slot |
| `is_filled` | `boolean` | Status terisi/kosong |
| `timestamp` | `timestamptz` | Waktu pencatatan |

### Tabel `chat_sessions`

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | `uuid` | Primary key |
| `user_id` | `uuid` | Foreign key → `users.id` |
| `user_message` | `text` | Pesan dari pengguna |
| `bot_response` | `text` | Respons dari chatbot |
| `created_at` | `timestamptz` | Waktu pesan |

> **Catatan:** Tabel `devices` sudah tidak digunakan. MAC address dan device name sekarang disimpan langsung di tabel `users`.

---

## Referensi Obat (RAG)

Saat ini sistem memiliki 5 dokumen referensi obat yang tersimpan di ChromaDB:

| Obat | Indikasi |
|------|----------|
| Paramex | Sakit kepala, pusing, sakit gigi |
| Sanmol | Sakit kepala, demam, nyeri ringan-sedang |
| Promag | Maag, asam lambung, kembung |
| Vicks Formula 44 | Batuk kering, bersin, alergi |
| Entrostop | Diare |

---

## Catatan Penting

> \* *Endpoint saat ini belum menerapkan enforce autentikasi JWT meskipun modul autentikasi sudah tersedia. Semua endpoint dapat diakses tanpa token.*

> Token JWT berlaku selama **24 jam** setelah diterbitkan.

> Format token: `Bearer <token>` pada header `Authorization` (jika diterapkan).
