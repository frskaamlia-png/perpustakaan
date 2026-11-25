from datetime import date


# ===================== CLASS BUKU =====================
class Buku:
    def __init__(self, judul, penulis, kode_buku, stok, lokasi_rak):
        self.judul = judul              # PUBLIC
        self.penulis = penulis          # PUBLIC
        self.kode_buku = kode_buku      # PUBLIC
        self._stok = stok               # PROTECTED
        self.__lokasi_rak = lokasi_rak  # PRIVATE

    def get_lokasi_rak(self):
        return self.__lokasi_rak

    def set_lokasi_rak(self, lokasi_baru):
        if not lokasi_baru:
            raise ValueError("Lokasi rak tidak boleh kosong.")
        self.__lokasi_rak = lokasi_baru

    def get_stok(self):
        return self._stok

    def set_stok(self, stok_baru):
        if stok_baru < 0:
            raise ValueError("Stok tidak boleh negatif.")
        self._stok = stok_baru

    def tambah_stok(self):
        self._stok += 1

    def kurangi_stok(self):
        if self._stok <= 0:
            raise ValueError("Stok buku habis.")
        self._stok -= 1

    def info(self):
        print(f"[{self.kode_buku}] {self.judul} - {self.penulis}")
        print(f"   Stok: {self._stok} | Rak: {self.__lokasi_rak}")


# ===================== CLASS ANGGOTA =====================
class Anggota:
    def __init__(self, id_anggota, nama, maks_pinjam=3):
        self.id_anggota = id_anggota        # PUBLIC
        self.nama = nama                    # PUBLIC
        self._maks_pinjam = maks_pinjam     # PROTECTED
        self.__status_aktif = True          # PRIVATE
        self.daftar_peminjaman = []         # AGGREGATION

    def get_maks_pinjam(self):
        return self._maks_pinjam

    def set_maks_pinjam(self, jumlah):
        if jumlah < 1:
            raise ValueError("Maksimal pinjam minimal 1.")
        self._maks_pinjam = jumlah

    def get_status_aktif(self):
        return self.__status_aktif

    def set_status_aktif(self, status):
        if not isinstance(status, bool):
            raise ValueError("Status harus True atau False.")
        self.__status_aktif = status

    def jumlah_pinjaman_aktif(self):
        return sum(1 for p in self.daftar_peminjaman if p.get_status() == "Dipinjam")

    def pinjam_buku(self, peminjaman, buku):
        if not self.__status_aktif:
            raise ValueError(f"Anggota {self.nama} tidak aktif.")
        if self.jumlah_pinjaman_aktif() >= self._maks_pinjam:
            raise ValueError(f"{self.nama} sudah mencapai batas maksimal pinjam ({self._maks_pinjam}).")
        if peminjaman.kode_buku != buku.kode_buku:
            raise ValueError("Kode buku tidak sesuai.")
        buku.kurangi_stok()
        self.daftar_peminjaman.append(peminjaman)

    def kembalikan_buku(self, peminjaman, buku, tanggal_kembali):
        denda = peminjaman.kembalikan(tanggal_kembali)
        buku.tambah_stok()
        return denda

    def info(self):
        status = "Aktif" if self.__status_aktif else "Nonaktif"
        print(f"[{self.id_anggota}] {self.nama} | Maks pinjam: {self._maks_pinjam} | Status: {status}")
        print(f"   Peminjaman tercatat: {len(self.daftar_peminjaman)} | Sedang dipinjam: {self.jumlah_pinjaman_aktif()}")


# ===================== CLASS PEMINJAMAN =====================
class Peminjaman:
    BATAS_HARI = 7
    DENDA_PER_HARI = 1000

    def __init__(self, kode_buku, tanggal_pinjam, tanggal_kembali=None):
        self.kode_buku = kode_buku              # PUBLIC (association ke Buku)
        self.tanggal_pinjam = tanggal_pinjam    # PUBLIC
        self.tanggal_kembali = tanggal_kembali  # PUBLIC
        self._status = "Dipinjam"               # PROTECTED

    def get_status(self):
        return self._status

    def set_status(self, status_baru):
        if status_baru not in ("Dipinjam", "Dikembalikan"):
            raise ValueError("Status harus 'Dipinjam' atau 'Dikembalikan'.")
        self._status = status_baru

    def kembalikan(self, tanggal_kembali):
        if self._status == "Dikembalikan":
            raise ValueError("Buku sudah dikembalikan.")
        self.tanggal_kembali = tanggal_kembali
        self.set_status("Dikembalikan")
        lama = (tanggal_kembali - self.tanggal_pinjam).days
        terlambat = max(0, lama - self.BATAS_HARI)
        return terlambat * self.DENDA_PER_HARI

    def info_peminjaman(self):
        kembali = self.tanggal_kembali if self.tanggal_kembali else "-"
        print(f"   [{self.kode_buku}] Pinjam: {self.tanggal_pinjam} | Kembali: {kembali} | Status: {self._status}")


# ===================== CLASS PERPUSTAKAAN =====================
class Perpustakaan:
    def __init__(self, nama):
        self.nama = nama
        self.daftar_buku = []               # COMPOSITION

    def tambah_buku(self, judul, penulis, kode_buku, stok, lokasi_rak):
        buku = Buku(judul, penulis, kode_buku, stok, lokasi_rak)
        self.daftar_buku.append(buku)
        return buku

    def cari_buku(self, kode_buku):
        for b in self.daftar_buku:
            if b.kode_buku == kode_buku:
                return b
        return None


# ===================== FUNGSI BANTU =====================
def pinjam(perpus, anggota, kode_buku, tanggal):
    buku = perpus.cari_buku(kode_buku)
    if buku is None:
        print(f"Gagal   : Buku {kode_buku} tidak ditemukan.")
        return None
    p = Peminjaman(kode_buku, tanggal)
    try:
        anggota.pinjam_buku(p, buku)
        return p
    except ValueError as e:
        print(f"Gagal   : {e}")
        return None


# ===================== PROGRAM UTAMA =====================
if __name__ == "__main__":
    # ---------- INSTANSIASI ----------
    perpus = Perpustakaan("Perpustakaan Kampus")

    # 1) Buat 3 buku
    b1 = perpus.tambah_buku("Pemrograman Python", "Budi Raharjo", "B001", 3, "A-01")
    b2 = perpus.tambah_buku("Basis Data", "Siti Aminah", "B002", 2, "A-02")
    b3 = perpus.tambah_buku("Jaringan Komputer", "Agus Salim", "B003", 2, "B-01")

    # 2) Buat 2 anggota
    a1 = Anggota("A001", "Andi")
    a2 = Anggota("A002", "Rina")

    # 3) Anggota 1 pinjam 2 buku
    p1 = pinjam(perpus, a1, "B001", date(2025, 11, 1))
    p2 = pinjam(perpus, a1, "B002", date(2025, 11, 2))

    # 4) Anggota 2 pinjam 1 buku
    p3 = pinjam(perpus, a2, "B003", date(2025, 11, 3))

    # 5) Pengembalian buku (Andi mengembalikan B001, terlambat 4 hari)
    denda = a1.kembalikan_buku(p1, b1, date(2025, 11, 12))

    # ---------- DEMONSTRASI DENGAN print() ----------
    print("=" * 50)
    print("DEMONSTRASI PROGRAM PERPUSTAKAAN")
    print("=" * 50)

    # DEMO 1) Informasi buku dan stoknya
    print("\n1) INFORMASI BUKU DAN STOKNYA")
    print("-" * 50)
    for b in perpus.daftar_buku:
        b.info()
    # >>> SCREENSHOT 1: bagian "1) INFORMASI BUKU DAN STOKNYA"

    # DEMO 2) Informasi anggota
    print("\n2) INFORMASI ANGGOTA")
    print("-" * 50)
    a1.info()
    a2.info()
    # >>> SCREENSHOT 2: bagian "2) INFORMASI ANGGOTA"

    # DEMO 3) Daftar peminjaman masing-masing anggota
    print("\n3) DAFTAR PEMINJAMAN MASING-MASING ANGGOTA")
    print("-" * 50)
    for a in (a1, a2):
        print(f"{a.nama} ({a.id_anggota}):")
        for p in a.daftar_peminjaman:
            p.info_peminjaman()
    print(f"\nDenda Andi untuk buku B001: Rp{denda}")
    # >>> SCREENSHOT 3: bagian "3) DAFTAR PEMINJAMAN MASING-MASING ANGGOTA"