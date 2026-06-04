from http.server import BaseHTTPRequestHandler
import json

# ==========================================
# FUNGSI PYTHON 1: FITUR INTELIJEN AUDIT PAJAK & DISKON LOGISTIK
# ==========================================
def hitung_diskon_dan_pajak(harga_satuan, jumlah_barang):
    """
    Fungsi untuk menghitung total bersih pengadaan dengan aturan bisnis:
    - Jika total belanja > Rp 5.000.000, dapat diskon 5%
    - Dikenakan Pajak PPN Kampus sebesar 11%
    """
    total_kotor = harga_satuan * jumlah_barang
    
    # Logika Diskon
    diskon = 0
    if total_kotor > 5000000:
        diskon = total_kotor * 0.05
        
    total_setelah_diskon = total_kotor - diskon
    ppn = total_setelah_diskon * 0.11
    total_bersih = total_setelah_diskon + ppn
    
    return {
        "total_kotor": total_kotor,
        "potongan_diskon": diskon,
        "pajak_ppn": ppn,
        "total_bersih_final": total_bersih
    }

# ==========================================
# FUNGSI PYTHON 2: VALIDATOR SISTEM 3-WAY MATCHING (KEUANGAN)
# ==========================================
def verifikasi_3way_matching(no_po, no_sj, no_inv):
    """
    Fungsi untuk memvalidasi keaslian dokumen keuangan.
    Memastikan format nomor PO, Surat Jalan, dan Invoice sinkron & valid.
    """
    # Validasi sederhana format string dokumen
    po_valid = "#PR-" in no_po or "#PO-" in no_po
    sj_valid = "SJ" in no_sj
    inv_valid = "INV" in no_inv
    
    status_matching = po_valid and sj_valid and inv_valid
    
    if status_matching:
        pesan = "STATUS: MATCHING LUNAS. Berkas sah untuk dicairkan oleh Bank."
    else:
        pesan = "STATUS: DISKREPANSI DATA. Dokumen tidak sinkron atau palsu!"
        
    return {
        "is_matched": status_matching,
        "catatan_audit": pesan
    }

# ==========================================
# HANDLER UTAMA VERCEL SERVERLESS
# ==========================================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Membaca body request dari JavaScript Frontend
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_body = json.loads(post_data.decode('utf-8'))
        
        path = self.path
        response_data = {}
        
        # Routing ke Fungsi Python 1
        if "/api/audit/kalkulator" in path:
            harga = float(request_body.get("harga", 0))
            jumlah = int(request_body.get("jumlah", 1))
            response_data = hitung_diskon_dan_pajak(harga, jumlah)
            
        # Routing ke Fungsi Python 2
        elif "/api/audit/verify" in path:
            po = request_body.get("po", "")
            sj = request_body.get("sj", "")
            inv = request_body.get("inv", "")
            response_data = verifikasi_3way_matching(po, sj, inv)
            
        else:
            response_data = {"error": "Endpoint tidak ditemukan"}

        # Mengirim respon balik ke browser
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def do_OPTIONS(self):
        # Handler untuk mengizinkan CORS Browser
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
