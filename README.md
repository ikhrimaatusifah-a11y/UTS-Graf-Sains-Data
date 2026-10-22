# UTS Graf Sains Data — Tugas Pendahuluan

## 1.1 Persiapan dan Perkenalan Lingkungan

Menggunakan Python 3.10.0 di Windows. Virtual environment `myenv` berhasil dibuat dan diaktifkan dengan `python -m venv myenv` dan `myenv\Scripts\activate`. Folder proyek `UTS-GSD` dibuat, diikuti file `requirements.txt`. Instalasi awal sesuai berkas soal menghasilkan Neo4j Driver 4.2.1. Karena contoh tutorial menggunakan `RoutingControl` dan `execute_query` yang tidak tersedia pada 4.2.1, driver ditingkatkan ke 6.4.1. Instalasi `pandas` dilakukan untuk membaca CSV. File requirements pada repositori ini mencerminkan versi modern yang dipakai pada kode final, bukan salinan persis versi awal di PDF.

## 1.2 Mempelajari Penggunaan Driver Neo4j

Koneksi Python–Neo4j diuji. Awalnya muncul error autentikasi, lalu diperbaiki sehingga menghasilkan `Berhasil terhubung!`. Program `neo4j_driver.py` membuat node `Person` Arthur, Guinevere, Lancelot, Merlin dengan relationship `KNOWS`, lalu mencetak:

```text
Teman Arthur:
Guinevere
Lancelot
Merlin
```

`MERGE` dipakai untuk mencegah pembuatan ulang node/relationship yang sama pada contoh tersebut. Query `MATCH` mencari teman Arthur, `RETURN` mengembalikan nama, dan `ORDER BY` mengurutkan hasil.

## 1.3 Impor Data RetailRocket ke Neo4j

Dataset RetailRocket diperoleh dari Kaggle, dan ZIP diekstrak ke folder `data/`. Empat file hasil ekstraksi adalah `events.csv`, `category_tree.csv`, `item_properties_part1.csv`, dan `item_properties_part2.csv`. `events.csv` memiliki kolom `timestamp`, `visitorid`, `event`, `itemid`, `transactionid`. Data ini memodelkan `Visitor` dan `Item`, dengan tiga tipe hubungan: `VIEWED` untuk view, `ADDED_TO_CART` untuk addtocart, dan `BOUGHT` untuk transaction. `transactionid` kosong untuk interaksi non-transaksi.

Pengujian sebelumnya menggunakan `test_import.py` dan berhasil memproses 5 baris. Screenshot Neo4j menunjukkan 5 `Visitor`, 5 `Item`, dan 5 hubungan `PERFORMED`. **Hasil tersebut membuktikan uji awal, bukan impor batch seluruh data dengan tiga jenis relationship yang diminta soal.** Script `import_retailrocket.py` di repositori ini melengkapi mekanisme batch sesuai instruksi dosen, tetapi hasil eksekusi script baru belum diverifikasi pada database lokal.

### Cara menjalankan di CMD Windows

```bat
cd C:\Users\RIMA\UTS-GSD
C:\Users\RIMA\myenv\Scripts\activate
python -m pip install -r requirements.txt
set NEO4J_PASSWORD=ISI_PASSWORD_NEO4J_ANDA
python neo4j_driver.py
python import_retailrocket.py --source data --batch-size 1000 --limit 5
```

Jika tes berhasil, lakukan impor keseluruhan dengan menghilangkan `--limit 5` (data besar; perhatikan kapasitas disk/RAM). **Jangan menjalankan impor penuh berulang kali tanpa membersihkan relasi hasil impor sebelumnya**, karena skrip menggunakan `CREATE` untuk mempertahankan setiap peristiwa dan pengulangan akan menggandakan relasi. Tidak perlu menghapus node `Person` contoh.

### Verifikasi di Neo4j Query

```cypher
MATCH (v:Visitor)-[r]->(i:Item)
RETURN type(r) AS jenisRelasi, count(r) AS jumlah
ORDER BY jumlah DESC;
```

```cypher
MATCH (v:Visitor)-[r]->(i:Item)
WHERE type(r) IN ['VIEWED', 'ADDED_TO_CART', 'BOUGHT']
RETURN v, r, i LIMIT 25;
```

### GitHub

Unggah `README.md`, `requirements.txt`, `neo4j_driver.py`, `import_retailrocket.py`, dan screenshot bukti hasil query. Jangan unggah password, virtual environment `myenv/`, ZIP besar, atau dataset mentah jika tidak diperlukan.
