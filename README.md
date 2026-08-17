# 🧙‍♀️ LavaVault: Physical Chaos & Entropy-Based Cryptographic Engine

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Security](https://img.shields.io/badge/Encryption-AES--256--GCM-green.svg)
![Hashing](https://img.shields.io/badge/KDF-HKDF--SHA256-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

**LavaVault**, Cloudflare'ın ünlü **LavaRand** mimarisinden esinlenerek geliştirilmiş, fiziksel ortamdan elde edilen rastgeleliği kriptografik işlemlerde kullanan bir **şifreleme ve güvenli parola üretim motorudur**.

Sistem; lav lambası videoları ve canlı kamera görüntülerinden elde edilen fiziksel entropiyi işleyerek kriptografik olarak güçlü anahtarlar üretir. Bu anahtarlar, parola üretimi ve dosya şifreleme işlemlerinde kullanılabilir.
<img width="1055" height="710" alt="image" src="https://github.com/user-attachments/assets/3f599efb-e64c-4a01-afc2-23af83dd5642" />


---

## 📌 Temel Özellikler

* 🌊 **Fiziksel Entropi Havuzu (True Randomness):**
  Lav lambası videolarındaki termal ve görsel hareketlerden veya canlı kamera görüntülerinden elde edilen piksel verilerini rastgelelik kaynağı olarak kullanır.

* 📹 **Canlı Kamera Desteği (Live Optical Noise):**
  Web kamerasından gerçek zamanlı olarak alınan görüntülerdeki optik gürültü ve piksel değişimlerini entropi kaynağı olarak değerlendirir.

* 🔐 **Askeri Düzeyde Şifreleme (AES-256-GCM):**
  Dosyaları kimlik doğrulamalı ve güvenli **AES-256-GCM** algoritması ile şifreler.

* 🔑 **Akıllı Anahtar Türetme & Kurtarma:**
  Fiziksel entropiden elde edilen tohum, **SHA-256** ve **HKDF** kullanılarak güvenli şifreleme anahtarlarına dönüştürülür.

* 💻 **Zengin Terminal Arayüzü (TUI):**
  `Rich` kütüphanesi kullanılarak geliştirilen renkli ve kullanıcı dostu terminal arayüzü üzerinden tüm işlemler gerçekleştirilebilir.

---

## 🏗️ Mimari ve Çalışma Mantığı

```text
[ Lav Lambası Videoları / Canlı Kamera ]
                    |
                    ▼
      (OpenCV Piksel Okuma & ROI Ayrıştırma)
                    |
                    ▼
             [ Ham Piksel Matrisleri ]
                    |
                    ▼
            (SHA-256 Kriptografik Kıyma)
                    |
                    ▼
               [ 256-bit Tohum ]
                    |
                    ▼
            (HKDF - Key Derivation Function)
                    |
                    ▼
             [ Master Key (AES-256) ]
                 /              \
                ▼                ▼
       [ Parola Üretimi ]   [ Dosya Kilitleme
                              (AES-256-GCM) ]
```

### 🔄 Veri Akışı

1. **Fiziksel ortamdan veri toplama:**
   Lav lambası videosu veya canlı kamera görüntüsü alınır.

2. **Piksel verilerinin işlenmesi:**
   OpenCV kullanılarak görüntüden gerekli bölge (ROI) ayrıştırılır ve ham piksel verileri elde edilir.

3. **Kriptografik karma:**
   Elde edilen ham veriler SHA-256 algoritması ile işlenerek 256-bit bir tohum oluşturulur.

4. **Anahtar türetme:**
   256-bit tohum, HKDF (HMAC-based Key Derivation Function) kullanılarak güvenli bir master key'e dönüştürülür.

5. **Kriptografik işlemler:**
   Elde edilen AES-256 anahtarı kullanılarak güvenli parola üretimi ve dosya şifreleme işlemleri gerçekleştirilir.

---

## 🚀 Kurulum

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/mlkaydemir/LavaVault.git
cd LavaVault
```

### 2. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

---

## 📁 Proje Yapısı

```text
LavaVault/
├── videos/                # Lav lambası videolarının (.mp4 / .mov) bulunduğu dizin
├── keys/                  # Üretilen fiziksel key anahtarları (Git'e eklenmez)
├── lavakey.py             # Ana kriptografik motor ve TUI arayüzü
├── guvenli_kasa.json      # Kasa kayıtları (Git'e eklenmez)
├── requirements.txt       # Python bağımlılıkları
├── .gitignore             # Güvenlik ve gereksiz dosya filtreleri
└── README.md              # Proje dokümantasyonu
```

---

## 💻 Kullanım

Konsol uygulamasını başlatmak için:

```bash
python lavakey.py
```

Uygulama başlatıldığında terminal üzerinden LavaVault'un sunduğu işlemlere erişebilirsiniz.

### Menü Seçenekleri

1. **Yeni Parola Üret**
   Fiziksel entropi kullanarak kriptografik olarak güçlü ve rastgele parolalar oluşturur.

2. **Kayıtlı Parolaları Sil**
   Kasada kayıtlı bulunan parolaları listeler ve seçilen kayıtların silinmesini sağlar.

3. **Dosya Kilitle**
   PDF, DOCX, PNG vb. dosyaları `.lavalock` formatına dönüştürerek AES-256-GCM ile şifreler ve orijinal dosyanın güvenliğini sağlar.

4. **Dosya Kilidini Aç**
   `.lavalock` dosyasını otomatik anahtar eşleştirmesi ile çözerek orijinal dosya formatına geri getirir.

5. **Kilitli Dosya Kaydını Sil**
   Kasada bulunan kilitli dosyalara ait kayıtları temizler.

6. **Kasadaki Parola ve Dosyaları Listele**
   Kasada kayıtlı olan parolaları ve şifrelenmiş dosyaları tablo şeklinde görüntüler.

7. **Tüm Kasayı Sıfırla**
   Kasayı fabrika ayarlarına döndürerek kayıtlı verileri temizler.

---

## 🛡️ Güvenlik

LavaVault, hassas anahtar materyallerinin ve kasa bilgilerinin yanlışlıkla GitHub gibi herkese açık depolara gönderilmesini önlemek için `.gitignore` kullanır.

Özellikle aşağıdaki dosya ve klasörler Git'e dahil edilmemelidir:

```text
keys/
guvenli_kasa.json
```

Bu dosyalar kişisel kriptografik anahtarlar ve kasa kayıtları içerebileceğinden **kesinlikle public depolara yüklenmemelidir.**

> ⚠️ **Önemli:** `.gitignore` dosyasına eklemek, daha önce Git'e commit edilmiş gizli bilgileri otomatik olarak silmez. Hassas bir anahtar yanlışlıkla commit edildiyse ilgili anahtarın yenilenmesi/revoke edilmesi ve Git geçmişinden temizlenmesi gerekir.

---

## 🔐 Kullanılan Kriptografik Yapılar

| Teknoloji            | Kullanım Amacı                                       |
| -------------------- | ---------------------------------------------------- |
| **SHA-256**          | Ham fiziksel verinin kriptografik olarak özetlenmesi |
| **HKDF**             | Güvenli anahtar türetme                              |
| **AES-256-GCM**      | Dosya şifreleme ve bütünlük doğrulama                |
| **Physical Entropy** | Rastgelelik kaynağı                                  |
| **OpenCV**           | Görüntü ve piksel verilerinin işlenmesi              |

---

## 🧩 Kullanılan Teknolojiler

* **Python 3.9+**
* **OpenCV**
* **Cryptography**
* **HKDF**
* **SHA-256**
* **AES-256-GCM**
* **Rich**
* **Git / GitHub**

---

## 🌋 Fiziksel Entropi Yaklaşımı

LavaVault'un temel fikri, bilgisayar tarafından üretilen deterministik rastgeleliğin yanında fiziksel dünyadaki öngörülemez değişimleri de rastgelelik kaynağı olarak kullanmaktır.

Lav lambası gibi sürekli ve karmaşık hareketler üreten fiziksel sistemlerden veya canlı kamera görüntülerindeki optik gürültüden elde edilen piksel değişimleri işlenerek yüksek entropili bir veri kaynağı oluşturulur.

Bu veriler doğrudan şifreleme anahtarı olarak kullanılmaz. Bunun yerine kriptografik hash ve anahtar türetme fonksiyonlarından geçirilerek güvenli anahtar materyali oluşturulur.

---

## 📜 Lisans

Bu proje **MIT Lisansı** altında sunulmaktadır.

---

## ⚠️ Yasal ve Güvenlik Uyarısı

LavaVault eğitimsel ve araştırma amaçlı geliştirilmiş bir kriptografik projedir.

Gerçek ve kritik verileri korumak için kullanmadan önce uygulamanın güvenlik modeli, anahtar yönetimi, rastgelelik kaynağı ve tehdit modeli kapsamlı şekilde değerlendirilmelidir.

Proje anahtarlarını, kasa dosyalarını veya diğer hassas bilgileri public GitHub depolarında paylaşmayın.

---
