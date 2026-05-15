<div align="center">
  <h1>ITB Press B2B</h1>
  <p><em>Proyek ini dibuat untuk memenuhi Tugas Besar IF3141 Sistem Informasi</em></p>
</div>

## Identitas Kelompok
**Nomor Kelompok:** G08<br/>
**Nomor Kelas:** K01
<table align="center">
  <tr>
    <td align="center">
      <a href="https://github.com/zirachw">
        <img src="https://github.com/zirachw.png" width="80" style="border-radius: 50%;" /><br />
        <b>Razi Rachman Widyadhana</b><br/>
        <sub>13523004</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/bry-ho">
        <img src="https://github.com/bry-ho.png" width="80" style="border-radius: 50%;" /><br />
        <b>Bryan Ho</b><br/>
        <sub>13523029</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/julius123123">
        <img src="https://github.com/julius123123.png" width="80" style="border-radius: 50%;" /><br />
        <b>Julius Arthur</b><br/>
        <sub>13523030</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/buege-putra">
        <img src="https://github.com/buege-putra.png" width="80" style="border-radius: 50%;" /><br />
        <b>Buege Mahara Putra</b><br/>
        <sub>13523037</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/FerdinandGabe1805">
        <img src="https://github.com/FerdinandGabe1805.png" width="80" style="border-radius: 50%;" /><br />
        <b>Ferdinand Gabe Tua Sinaga</b><br/>
        <sub>13523051</sub>
      </a>
    </td>
  </tr>
</table>

---

## Nama Sistem & Perusahaan
**Nama Sistem:** ITB Press B2B - Sistem Manajemen Kolaborasi Mitra B2B<br/>
**Perusahaan:** PT Inovasi Teknologi Bermedia Press (PT ITB Press)


<p align="center">
    <img width="320px" src="https://github.com/user-attachments/assets/3fe69476-0e2d-45d3-9971-7c974634a935">
</p>


---

## Deskripsi Sistem
ITB Press B2B adalah sistem manajemen kolaborasi produk berbasis web yang dibangun di atas platform Odoo 17. Sistem ini menjembatani dua sisi pengguna: mitra B2B yang mengakses portal pelanggan untuk mengajukan pesanan dan memantau penjualan, serta tim internal ITB Press yang mengelola pipeline CRM, historis HPP, dan laporan penjualan melalui halaman manajemen khusus.

Pada sisi portal, mitra dapat mengajukan permintaan kerja sama produk, memantau status produk yang sedang berjalan, serta melihat dasbor penjualan dengan filter periode. Pada sisi internal, Staf Marketing mengelola seluruh alur CRM dari pengajuan hingga selesai produksi, sementara Direktur dapat memantau laporan penjualan dan historis HPP untuk keperluan evaluasi bisnis.

<p align="center">
<img width="854" height="544" alt="image" src="https://github.com/user-attachments/assets/08bf84e1-dc6a-41bb-a93a-815c66abbbb7" />
</p>

---

## Cara Menjalankan Sistem
Berikut langkah persiapan dan menjalankan sistem pada lingkungan *development* berbasis Docker.

**Prasyarat:** Docker Desktop terpasang ([unduh di sini](https://www.docker.com/products/docker-desktop/))

Langkah-langkah:

1. *Clone repository*

```bash
git clone https://github.com/zirachw/IF3141-Implementasi-K01-G08.git
cd IF3141-Implementasi-K01-G08
```

*Expected result:* folder proyek tersedia.

<img width="1173" height="407" alt="image" src="https://github.com/user-attachments/assets/7e9b127e-9d85-4f13-9f46-776e86be0bf9" />


2. Jalankan Docker *services*

```bash
docker compose up -d
```

*Expected result:* container `web` (Odoo) dan `db` (PostgreSQL) berjalan; Odoo tersedia di `http://localhost:8069`.

<img width="1346" height="177" alt="image" src="https://github.com/user-attachments/assets/6546cf54-a5a9-4de7-9ad7-e600015f49da" />


3. Instal modul dan muat data demo

```bash
docker compose run --rm web odoo -d postgres -i itbpress_b2b --stop-after-init
docker compose restart web
```

> Catatan: jika mengalami *error* saat instalasi, reset *volume* terlebih dahulu dengan `docker compose down -v` dan `docker compose up -d`, lalu jalankan kembali perintah di atas.

*Expected result:* log Odoo menunjukkan bahwa data `demo_users`, `demo_leads`, dan data lainnya berhasil dimuat.

<img width="1339" height="278" alt="image" src="https://github.com/user-attachments/assets/dfddcaae-7d2c-425b-917a-42b8cdf08694" />


4. Buka aplikasi di *browser*

```
http://localhost:8069
```

*Expected result:* halaman *login* ITB Press muncul.

<img width="1112" height="542" alt="image" src="https://github.com/user-attachments/assets/89ccde61-abcf-4287-acd9-3cf3b1532698" />

<br>

5. *Login* dan akses sistem

*Login* ke salah satu kredensial yang tersedia dan pastikan halaman sesuai dengan peran yang digunakan.

*Expected result:* setiap peran melihat halaman dan menu sesuai haknya.

Staf Marketing (internal):

<img width="1600" height="931" alt="image" src="https://github.com/user-attachments/assets/8a74a705-1e80-4ce3-a017-e160eb1c009a" />


<br>

Direktur (internal):

<img width="1600" height="931" alt="image" src="https://github.com/user-attachments/assets/da7828ea-6c66-4b7c-943b-636b00df8921" />


<br>

Mitra B2B (portal):

<img width="1600" height="931" alt="image" src="https://github.com/user-attachments/assets/568c62eb-2408-487c-ae6a-66e2253f65b1" />

<br>

6. Setelah selesai, hentikan Docker *services*

```bash
docker compose down
```

> Catatan: gunakan `docker compose down -v` jika ingin sekaligus menghapus *volume* database dan seluruh data lokal container.

*Expected result:* seluruh container Docker berhenti dan *network* proyek dibersihkan.

<img width="1332" height="300" alt="image" src="https://github.com/user-attachments/assets/4e006644-9ab1-4d87-9d1d-1a8710fa9e01" />


---

## Kredensial Tiap Peran
Berikut kredensial akun demo untuk tiap peran (akun lengkap tersedia di `custom_addons/itbpress_b2b/data/demo_users.xml`):

| Nama | Username | Password | Peran |
|------|----------|----------|-------|
| Budi Santoso | `marketing@itbpress.id` | `itbpress123` | Staf Marketing |
| Siti Rahayu | `direktur@itbpress.id` | `itbpress123` | Direktur |
| PT Akademia Nusantara | `mitra1@akademia.id` | `mitra123` | Mitra B2B |
| CV Gamma Persada | `mitra2@gamma.id` | `mitra123` | Mitra B2B |

> Catatan: terdapat juga akun `admin` Odoo bawaan, tetapi akun tersebut berbeda dari akun peran di atas. Gunakan kredensial demo di atas untuk menguji fitur ITB Press B2B.

---

## Kesimpulan dan Saran
Sistem ITB Press B2B berhasil menyediakan platform kolaborasi produk yang terintegrasi antara mitra eksternal dan tim internal ITB Press dalam satu aplikasi berbasis Odoo 17. Sistem ini mencakup alur pengajuan produk B2B, manajemen pipeline CRM, pemantauan historis HPP, serta pelaporan penjualan dengan filter periode yang fleksibel.

Ke depannya, sistem dapat dikembangkan dengan menambahkan notifikasi *real-time* perubahan status pesanan, integrasi dengan sistem keuangan dan logistik ITB Press, serta fitur pengelolaan kontrak dan dokumen kerja sama secara digital. Penerapan *backup* data berkala dan pengamanan akses berbasis *role* yang lebih granular juga perlu diperhatikan agar keberlangsungan operasional sistem tetap terjaga.
