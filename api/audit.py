from http.server import BaseHTTPRequestHandler
import json

# ==========================================
# FUNGSI PYTHON 1: VALIDATOR & FORMATTER HARGA REAL-TIME (ANTI ANGKA 0)
# ==========================================
def validasi_dan_format_harga(harga_vendor, jumlah_barang):
    """
    Fungsi Python untuk memastikan harga yang masuk dari staf pengadaan
    bersifat valid (di atas 0) dan menghitung total harga riil secara aman di server.
    """
    harga = float(harga_vendor) if harga_vendor else 0
    qty = int(jumlah_barang) if jumlah_barang else 1
    
    # Proteksi sistem jika data kosong atau bernilai 0
    if harga <= 0:
        status_validasi = "INVALID: Harga masih kosong atau Rp 0!"
        total_riil = 0
    else:
        status_validasi = "VALID: Harga terverifikasi real-time."
        total_riil = harga * qty
        
    return {
        "status_sistem": status_validasi,
        "harga_satuan": harga,
        "kuantitas": qty,
        "total_harga_riil": total_riil,
        "format_rupiah": f"Rp {total_riil:,.0f}".replace(",", ".")
    }

# ==========================================
# FUNGSI PYTHON 2: AUDITOR INTEGRITAS DOKUMEN (3-WAY MATCHING KELEMBAGAAN)
# ==========================================
def audit_dokumen_logistik(no_po, no_sj, no_inv):
    """
    Fungsi Python untuk mengaudit kecocokan nomor instrumen pengadaan di Keuangan.
    Memastikan berkas PO, Surat Jalan, dan Invoice tidak ada yang kosong.
    """
    # Mengecek apakah semua dokumen fisik logistik sudah lengkap diinput
    po_ada = bool(no_po and no_po != "0000")
    sj_ada = bool(no_sj and no_sj != "SJ-REF" and no_sj != "")
    inv_ada = bool(no_inv and no_inv != "INV-REF" and no_inv != "")
    
    sistem_matching = po_ada and sj_ada and inv_ada
    
    if sistem_matching:
        catatan_audit = "AUDIT SUKSES: Dokumen lengkap (3-Way Matching Terpenuhi). Dana siap dicairkan."
    else:
        catatan_audit = "AUDIT BERKAS GAGAL: Dokumen pengadaan belum lengkap atau masih menggunakan template default!"
        
    return {
        "apakah_matching": sistem_matching,
        "kesimpulan_audit": catatan_audit
    }

# ==========================================
# HANDLER UTAMA VERCEL SERVERLESS
# ==========================================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_body = json.loads(post_data.decode('utf-8'))
        
        path = self.path
        response_data = {}
        
        # Jalur komunikasi ke Fungsi Python 1
        if "/api/audit/kalkulator" in path:
            harga = request_body.get("harga", 0)
            jumlah = request_body.get("jumlah", 1)
            response_data = validasi_dan_format_harga(harga, jumlah)
            
        # Jalur komunikasi ke Fungsi Python 2
        elif "/api/audit/verify" in path:
            po = request_body.get("po", "")
            sj = request_body.get("sj", "")
            inv = request_body.get("inv", "")
            response_data = audit_dokumen_logistik(po, sj, inv)
            
        else:
            response_data = {"error": "Endpoint tidak ditemukan"}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
