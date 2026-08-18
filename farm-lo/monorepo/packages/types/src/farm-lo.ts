/**
 * `@sankit/types` — lớp GIS theo lô: thửa đất, mùa vụ, quan trắc vệ tinh, Issue.
 *
 * Nguồn: bộ dữ liệu 12 lô RiTi Farm (Trường Yên, Hoa Lư, Ninh Bình), kỳ 12/08/2025 –
 * 12/08/2026. Hợp đồng đầy đủ + 12 bất biến:
 * `apps/sk-coop/_prototype/uploads/hop-dong-du-lieu.md`.
 * Ánh xạ sang từ vựng của `sk-shared-contract.md` §2: `apps/sk-coop/FARM_LO_INGEST.md` §3.
 *
 * LƯU Ý — tên trường ở đây giữ nguyên tiếng Việt của bộ dữ liệu gốc để truy được về
 * file CSV/JSON. Nhãn hiện ra màn hình thì theo hợp đồng §2, KHÔNG dùng tên trường.
 */

/** Ngày dạng `YYYY-MM-DD`, KHÔNG kèm múi giờ. Đừng đưa qua `new Date()` rồi format lại. */
export type Ngay = string;
/** Tháng dạng `YYYY-MM`. */
export type Thang = string;

/** Phân định nguồn gốc. Mọi bản ghi đều phải mang một trong ba giá trị này. */
export type Nguon = "that" | "mau" | "dan_xuat";

/** Khoá nối giữa GIS và Sankit. `L01` … `L12`. Cũng là đoạn khu trong mã `SK-C-…`. */
export type LoId = string;

export type MaLoHang = `SK-L-${string}`;
export type MaBich = `SK-B-${string}`;
export type MaCay = `SK-C-${string}`;

export type MaCayTrong = "CUC" | "CCO" | "LAC" | "BCA" | "CHA" | "DAU" | "UOM";
export type MucDichLo = "canh_tac" | "luu_nien" | "cong_trinh" | "dat_nghi" | "vuon_uom";
export type PhaSinhTruong = "ini" | "dev" | "mid" | "end";

// ─────────────────────────────────────────────────────────── lớp ĐO ĐƯỢC (chỉ đọc)

/** Hồ sơ lô đất. Mọi trường đo được — API KHÔNG mở đường ghi (bất biến I8). */
export interface LoDat {
  lo_id: LoId;
  ten: string;
  muc_dich: MucDichLo;
  dien_tich_ha: number;
  /** Diện tích theo nét vẽ tay của chủ farm, trước khi nắn về mép thửa thật. */
  dien_tich_ve_tay_ha: number;
  chenh_dien_tich_pct: number;
  chu_vi_m: number;
  trong_tam: { lat: number; lon: number };
  cao_do_m: number;
  do_doc_deg: number;
  ndvi_trung_binh: number;
  ndvi_min: number;
  ndvi_max: number;
  bien_do_ndvi: number;
  ndmi_trung_binh: number;
  vh_db_trung_binh: number;
  so_ngay_quang: number;
  so_ngay_radar: number;
  /** Nhãn máy suy từ dạng chuỗi 12 tháng — CHƯA đối chiếu thực địa. */
  phan_loai_tu_anh: string;
  ndvi_mua_kho: number;
  ndvi_mua_mua: number;
  lech_so_voi_farm: number;
  xu_huong_thang_cuoi_ky: number;
  trang_thai_cuoi_ky: string;
  so_vu_do_duoc: number;
  so_vu_chac: number;
  nguon: "that";
}

export interface QuanTracQuang {
  ngay: Ngay;
  lo_id: LoId;
  /** Miền [−1, 1]. `null` = lô không đủ 60 % diện tích quang ngày đó. */
  ndvi: number | null;
  ndmi: number | null;
  quang_pct: number;
  /** Rỗng = dùng được. Khác rỗng = ngày đáng ngờ, phải loại trước khi chạy luật. */
  dang_ngo: "" | "mu_khi_quyen" | "thua_lo" | "mu_khi_quyen_va_thua_lo";
  nguon: "that";
}

export interface QuanTracRadar {
  ngay: Ngay;
  lo_id: LoId;
  /** Hai hướng bay lệch nhau cả dB trên cùng một thửa — đừng gộp chung. */
  huong_bay: "asc" | "des";
  vv_db: number;
  vh_db: number;
  rvi: number;
  nguon: "that";
}

export interface KhiHauNgay {
  date: Ngay;
  temperature_2m_max: number;
  temperature_2m_min: number;
  temperature_2m_mean: number;
  relative_humidity_2m_mean: number;
  precipitation_sum: number;
  rain_sum: number;
  precipitation_hours: number;
  et0_fao_evapotranspiration: number;
  shortwave_radiation_sum: number;
  wind_speed_10m_max: number;
}

// ──────────────────────────────────────────────────────────── lớp KHAI BÁO (ghi được)

/**
 * Một VỤ = một chu kỳ trồng (gieo → kết thúc). Một vụ có NHIỀU `DotThu`:
 * cúc chi hái nhiều lượt vì hoa nở dần, bồ công anh cắt nhiều lứa trên cùng gốc,
 * chanh lưu niên thu quả năm này qua năm khác.
 *
 * Gộp `Vu` và `DotThu` làm một là chỗ mô hình gãy — `scripts/kiem_tra.py` bắt
 * bằng bất biến I4 (hai vụ chồng thời gian mà tổng `ti_le_gieo` > 1).
 */
export interface Vu {
  vu_id: string;
  lo_id: LoId;
  ma_cay_trong: MaCayTrong;
  ten_cay_trong: string;
  ten_khoa_hoc: string | null;
  nhom_cay: string;
  luu_nien: boolean;
  ngay_xuong_giong: Ngay;
  /** `tu_ho_so_that` = lấy từ hồ sơ cây có thật trong Sankit/qr, không suy đoán. */
  do_tin_ngay_gieo: "tu_ho_so_that" | "suy_tu_ndvi" | "khong_kiem_duoc";
  /** `null` = vụ còn đang chạy. Cây lưu niên KHÔNG mặc nhiên là null — xem docs/01 §3. */
  ngay_ket_thuc: Ngay | null;
  /** Bao trùm mọi đợt thu của vụ. */
  ngay_thu_tu: Ngay;
  ngay_thu_den: Ngay;
  so_dot_thu: number;
  trang_thai: "dang_sinh_truong" | "dang_thu_hoach" | "da_thu_hoach";
  dien_tich_gieo_ha: number;
  /** Phần diện tích lô mà vụ này chiếm. < 0,6 nghĩa là NDVI trung bình cả lô sẽ không phản ánh vụ này. */
  ti_le_gieo: number;
  phu_kin_lo: boolean;
  san_luong_tuoi_du_kien_tan: number;
  san_luong_kho_du_kien_tan: number;
  kc_fao56: { ini: number; mid: number; end: number };
  /** Mốc NDVI thật mà vụ này neo vào. */
  neo_ndvi: { day: Ngay; ndvi_day: number; dinh: Ngay | null; ndvi_dinh: number | null };
  ghi_chu: string | null;
  nguon: Nguon;
}

/** Một lượt hái trong một vụ. Đơn vị mà `LoHang` và phép đối chiếu vệ tinh bám vào. */
export interface DotThu {
  dot_id: string;
  vu_id: string;
  lo_id: LoId;
  ma_cay_trong: MaCayTrong;
  ngay_thu_tu: Ngay;
  ngay_thu_den: Ngay;
  trang_thai: "chua_toi" | "dang_thu_hoach" | "da_thu_hoach";
  dien_tich_gieo_ha: number;
  san_luong_tuoi_du_kien_tan: number;
  san_luong_kho_du_kien_tan: number;
  neo_ndvi: { day: Ngay; ndvi_day: number; dinh: Ngay | null; ndvi_dinh: number | null };
  ghi_chu: string | null;
  nguon: Nguon;
}

export type LoaiViec =
  | "lam_dat"
  | "bon_lot"
  | "xuong_giong"
  | "bon_thuc"
  | "lam_co"
  | "tuoi"
  | "phong_tru_sinh_hoc"
  | "thu_hoach"
  | "cai_tao_dat";

export interface NhatKy {
  nk_id: string;
  lo_id: LoId;
  vu_id: string | "";
  ngay: Ngay;
  loai_viec: LoaiViec;
  mo_ta: string;
  nguoi_thuc_hien: string;
  vat_tu: string;
  luong: number | "";
  don_vi: string;
  /** Ngăn cách bằng `|`. Ví dụ: `CÂN|GPS|ẢNH|QUÉT MÃ CÂY`. */
  bang_chung: string;
  ghi_chu: string;
  nguon: Nguon;
}

export type TrangThaiLoHang =
  | "dang_thu_hoach"
  | "dang_say"
  | "dang_phan_loai"
  | "dang_dong_goi"
  | "cho_kiem_nghiem"
  | "da_niem_ho_so"
  | "da_giao";

export interface LoHang {
  id: MaLoHang;
  ten: string;
  lo_dat_id: LoId;
  vu_id: string;
  dot_thu_id: string;
  ma_cay_trong: MaCayTrong;
  ten_cay_trong: string;
  ngay_hai_tu: Ngay;
  ngay_hai_den: Ngay;
  khoi_luong_tuoi_kg: number;
  che_bien: {
    cong_nghe: string | null;
    dai_nhiet: string | null;
    thoi_gian_gio: number | null;
    nhat_ky_nhiet_so_hoa: boolean;
    nguon: Nguon;
  };
  khoi_luong_kho_kg: number | null;
  ti_le_thu_hoi: number | null;
  phan_phoi: { b2b_si_kg: number; b2c_le_kg: number; so_bich_20g: number };
  trang_thai: TrangThaiLoHang;
  /** `null` = chưa có phiếu thật. KHÔNG dựng phiếu giả để lấp chỗ này. */
  kiem_nghiem: null;
  ly_do_kiem_nghiem_rong: string;
  nguon_cay: MaCay[];
  /** Ảnh vệ tinh gần ngày thu nhất — chỗ GIS xuất hiện trên trang QR B2B. */
  trang_thai_lo_dat_luc_hai: {
    ngay_anh: Ngay;
    lech_ngay: number;
    ndvi: number;
    ndmi: number;
    nguon: "that";
  } | null;
  /** Khí hậu THẬT tích luỹ cả vụ, từ ngày gieo tới ngày thu. */
  khi_hau_ca_vu: {
    tong_mua_mm: number;
    so_ngay_mua: number;
    tong_et0_mm: number;
    can_bang_nuoc_mm: number;
    gdd_co_so_10c: number;
    t_max_cao_nhat_c: number | null;
    t_min_thap_nhat_c: number | null;
    so_ngay_theo_doi: number;
    nguon: "that";
  };
  nguon: Nguon;
}

export interface Bich {
  id: MaBich;
  lo_hang_id: MaLoHang;
  lo_dat_id: LoId;
  vu_id: string;
  quy_cach: { khoi_luong: string; dang: string };
  ngay_dong_goi: Ngay;
  han_su_dung: Ngay;
  nguon_cay: MaCay[];
  nguon: Nguon;
}

export interface CayCaThe {
  id: MaCay;
  giong: MaCayTrong;
  ten_thuong: string;
  lo_id: LoId;
  so_trong_lo: number;
  /** Hiện là trọng tâm lô — chưa có toạ độ riêng từng cây. Xem `do_chinh_xac_toa_do`. */
  toa_do_uoc: { lat: number; lon: number };
  do_chinh_xac_toa_do: string;
  vu_id: string;
  ngay_xuong_giong: Ngay;
  co_ho_so_that_trong_Sankit: boolean;
  nguon: Nguon;
}

// ────────────────────────────────────────────────────────────────── lớp DẪN XUẤT

/** Một hàng = một (lô, tháng). 12 × 13 = 156 hàng. Nguồn chính của mọi biểu đồ. */
export interface LoThang {
  lo_id: LoId;
  thang: Thang;
  muc_dich: MucDichLo;
  vu_id: string | "";
  /** Chỉ khác rỗng ở tháng đang thu hoạch. */
  dot_thu_id: string | "";
  cay_trong: string;
  pha_sinh_truong: PhaSinhTruong | "";
  ndvi: number | null;
  /** `noi_suy` = tháng đó không có ảnh quang nào. Đừng vẽ nét liền qua chỗ này. */
  nguon_ndvi: "quan_trac" | "noi_suy" | "khong_co";
  ndmi: number | null;
  so_ngay_co_anh_quang: number;
  vh_db: number | null;
  che_phu_uoc_pct: number | null;
  t_khong_khi_max_c: number | null;
  t_khong_khi_min_c: number | null;
  /** ƯỚC TÍNH, không phải đo: Tmax + 9,0 × (1 − FVC). Xem docs/05 §2. */
  t_be_mat_uoc_c: number | null;
  mua_mm: number;
  mua_hieu_qua_mm: number;
  et0_mm: number;
  kc: number;
  etc_mm: number;
  thieu_nuoc_mm: number;
  nuoc_tuoi_can_m3: number;
  nguon_khi_hau: "that";
  nguon_cay_trong: Nguon;
}

export type MaLuat =
  | "R1_THIEU_NUOC"
  | "R2_SUT_NDVI_KHONG_RO_LY_DO"
  | "R3_MAT_DAU_QUANG_HOC"
  | "R4_KEM_MAT_BANG_FARM"
  | "R5_NHAT_KY_KHONG_KHOP_ANH"
  | "R6_CHUOI_NGAY_KHONG_MUA";

export interface CanhBao {
  cb_id: string;
  ma_luat: MaLuat;
  muc_do: "cao" | "trung_binh" | "thap";
  /** `null` khi cảnh báo ở mức farm (mây phủ cả vùng, chuỗi ngày không mưa). */
  lo_id: LoId | null;
  pham_vi: "lo" | "farm";
  ngay: Ngay;
  tieu_de: string;
  chi_tiet: string;
  bang_chung: Record<string, unknown>;
  nguon_du_lieu: "that";
  /** CHƯA có trong bộ dữ liệu — phải thêm khi lên sản xuất. Xem docs/04 §cuối. */
  trang_thai?: "mo" | "da_xem" | "da_xu_ly" | "bo_qua";
}

/** Đối chiếu lời khai với số đo. Đây là sản phẩm mang giá trị thương mại của mô hình. */
export interface DoiChieu {
  lo_id: LoId;
  dot_thu_id: string | null;
  vu_id: string | null;
  ma_cay_trong: MaCayTrong | null;
  so_ngay_hai_khai_bao: number;
  ngay_hai_tu: Ngay;
  ngay_hai_den: Ngay;
  /** `null` = luật không áp dụng cho cây này (hái quả trên cây lưu niên). */
  nguong_sut_ap_dung: number | null;
  anh_dinh_truoc: { ngay: Ngay; ndvi: number } | null;
  anh_day_sau: { ngay: Ngay; ndvi: number } | null;
  sut_ndvi: number | null;
  ket_qua: "khop" | "khong_thay_doi_tren_anh" | "khong_du_du_lieu" | "khong_ap_dung";
  kiem_bang_radar: {
    vh_truoc_db: number;
    vh_sau_db: number;
    thay_doi_db: number;
    ket_qua: "khop" | "khong_thay_doi";
    ghi_chu: string;
  } | null;
  ket_qua_tong_hop:
    | "xac_nhan"
    | "xac_nhan_bang_radar"
    | "can_nguoi_xac_minh"
    | "chua_ket_luan_duoc"
    | "khong_ap_dung";
  dien_giai: string;
}
