import os
import sys
import glob
import json
import time
import hashlib
import cv2
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import print as rprint

console = Console()

root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)

VAULT_FILE = "guvenli_kasa.json"
KEYS_DIR = "keys"
VIDEOS_DIR = "videos"
LOCK_EXT = ".lavalock"

os.makedirs(KEYS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)

BANNER = """[bold magenta]
╦  ┌─┐┬  ┬┌─┐╦  ╦┌─┐┬ ┬┬ ┌┬┐
║  ├─┤└┐┌┘├─┤╚╗╔╝├─┤│ ││  │ 
╩═╝┴ ┴ └┘ ┴ ┴ ╚╝ ┴ ┴└─┘┴─┘┴ 
[/bold magenta][cyan]True Physical Chaos Cryptographic Engine[/cyan]"""

def load_vault() -> dict:
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"parolalar": {}, "sifreli_dosyalar": {}}
    return {"parolalar": {}, "sifreli_dosyalar": {}}

def save_vault(data: dict):
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_entropy_from_videos() -> tuple[bytes, list]:
    video_list = sorted(glob.glob(os.path.join(VIDEOS_DIR, "*.mp4")) + glob.glob(os.path.join(VIDEOS_DIR, "*.mov")))
    if not video_list:
        raise FileNotFoundError(f"'{VIDEOS_DIR}' klasöründe hiç video bulunamadı!")

    hasher = hashlib.sha256()
    total_frames = 0
    used_videos = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="magenta", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Videolardan fiziksel entropi toplanıyor...", total=len(video_list))

        for v_path in video_list:
            cap = cv2.VideoCapture(v_path)
            if not cap.isOpened():
                progress.advance(task)
                continue
            
            v_name = os.path.basename(v_path)
            used_videos.append(v_name)
            frames_from_video = 0

            while frames_from_video < 150:
                ret, frame = cap.read()
                if not ret:
                    break
                frames_from_video += 1
                total_frames += 1
                
                if frames_from_video % 2 == 0:
                    h, w, _ = frame.shape
                    roi = frame[int(h*0.2):int(h*0.8), int(w*0.25):int(w*0.75)]
                    hasher.update(roi.tobytes())
                    hasher.update(total_frames.to_bytes(4, 'big'))

            cap.release()
            progress.advance(task)
            time.sleep(0.05)

    raw_seed = hasher.digest()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"lavakey-tui-core",
    )
    return hkdf.derive(raw_seed), used_videos

def get_entropy_from_camera() -> tuple[bytes, list]:
    console.print("\n[yellow][*] Web kamerası açılıyor... 5 saniyelik foton gürültüsü toplanacak.[/yellow]")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Web kamerası açılamadı veya bulunamadı!")

    hasher = hashlib.sha256()
    start_time = time.time()
    frame_count = 0
    total_pixels_processed = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed >= 5.0:
            break

        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        h, w, _ = frame.shape
        roi = frame[int(h*0.2):int(h*0.8), int(w*0.25):int(w*0.75)]
        
        hasher.update(roi.tobytes())
        hasher.update(frame_count.to_bytes(4, 'big'))
        total_pixels_processed += roi.size

        kalan_sure = max(0.0, 5.0 - elapsed)
        cv2.putText(frame, f"LAVAKEY LIVE ENTROPY STREAM", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Kalan Sure: {kalan_sure:.1f}s | Kare: {frame_count}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Islenen Piksel: {total_pixels_processed:,}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)
        cv2.rectangle(frame, (int(w*0.25), int(h*0.2)), (int(w*0.75), int(h*0.8)), (0, 0, 255), 2)

        cv2.imshow("LavaKey - Fiziksel Optik Entropi Yakalayici", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    raw_seed = hasher.digest()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"lavakey-live-cam",
    )
    
    console.print(f"[green][+] Başarılı: {frame_count} kamera karesi ve {total_pixels_processed:,} ham piksel entropiye dönüştürüldü.[/green]")
    return hkdf.derive(raw_seed), [f"Live Camera ({frame_count} Frames, {total_pixels_processed:,} Pixels)"]

def acquire_entropy() -> tuple[bytes, list]:
    console.print("\n[bold cyan]Entropi Kaynağını Seçin:[/bold cyan]")
    console.print("  [1] [green]Lav Videoları Havuzu (Tüm Videolar)[/green]")
    console.print("  [2] [yellow]Canlı Web Kamerası (5sn Canlı Önizlemeli)[/yellow]")
    
    sec = console.input("\n[bold white]Seçim (1/2, varsayılan 1): [/bold white]").strip()
    if sec == "2":
        return get_entropy_from_camera()
    return get_entropy_from_videos()

def save_key(key: bytes) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    key_path = os.path.join(KEYS_DIR, f"key_lavavault_{timestamp}.key")
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(key.hex())
    return os.path.abspath(key_path)

def dosya_tam_kilitle():
    console.print("\n[bold yellow]Lütfen açılan pencereden kilitlemek istediğiniz dosyayı seçin...[/bold yellow]")
    fpath = filedialog.askopenfilename(title="Kilitlemek İstediğiniz Dosyayı Seçin")
    
    if not fpath:
        console.print("[red][-] Dosya seçimi iptal edildi.[/red]")
        return

    fpath = os.path.abspath(fpath)
    if fpath.endswith(LOCK_EXT) or fpath.endswith(".enc"):
        console.print("[red][-] Bu dosya zaten kilitli bir formatta![/red]")
        return

    try:
        key, sources = acquire_entropy()
    except Exception as e:
        console.print(f"[red][-] Hata: {e}[/red]")
        return

    key_path = save_key(key)

    with open(fpath, "rb") as f:
        data = f.read()

    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    enc_path = fpath + LOCK_EXT
    with open(enc_path, "wb") as f:
        f.write(nonce + ciphertext)

    try:
        os.remove(fpath)
    except Exception:
        pass

    vault = load_vault()
    vault["sifreli_dosyalar"][os.path.normpath(enc_path)] = {
        "orijinal_yol": fpath,
        "key_path": key_path,
        "kaynaklar": sources,
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_vault(vault)

    res_panel = Panel.fit(
        f"[bold green]Kilitli Dosya :[/bold green] {os.path.basename(enc_path)}\n"
        f"[bold green]Kaynaklar     :[/bold green] {', '.join(sources)}\n"
        f"[bold green]Master Key    :[/bold green] {os.path.basename(key_path)}\n"
        f"[bold yellow]Durum         :[/bold yellow] Orijinal açık dosya sistemden güvenle kaldırıldı.",
        title="[bold green]✓ DOSYA BAŞARIYLA KİLİTLENDİ[/bold green]",
        border_style="green"
    )
    console.print(res_panel)

def dosya_tam_kilidini_ac():
    console.print("\n[bold yellow]Lütfen açılan pencereden kilidini açmak istediğiniz dosyayı seçin...[/bold yellow]")
    enc_path = filedialog.askopenfilename(
        title="Kilitli Dosyayı Seçin (.lavalock veya .enc)",
        filetypes=[("Tüm Dosyalar", "*.*"), ("LavaLock Dosyaları", f"*{LOCK_EXT}"), ("ENC Dosyaları", "*.enc")]
    )
    
    if not enc_path:
        console.print("[red][-] Dosya seçilmedi.[/red]")
        return

    enc_path = os.path.abspath(enc_path)
    with open(enc_path, "rb") as f:
        enc_data = f.read()

    if len(enc_data) < 12:
        console.print("[red][-] Hata: Dosya içeriği bozuk veya geçersiz![/red]")
        return

    nonce = enc_data[:12]
    ciphertext = enc_data[12:]

    if enc_path.endswith(LOCK_EXT):
        out_file = enc_path[:-len(LOCK_EXT)]
    elif enc_path.endswith(".enc"):
        out_file = enc_path[:-4]
    else:
        out_file = enc_path + ".dec"

    key_files = glob.glob(os.path.join(KEYS_DIR, "*.key"))
    if not key_files:
        console.print("[red][-] keys/ klasöründe hiç .key dosyası bulunamadı![/red]")
        return

    console.print(f"\n[cyan][*] keys/ klasöründeki {len(key_files)} adet anahtar sırayla deneniyor...[/cyan]")
    
    basarili_key = None
    plaintext = None

    for k_file in key_files:
        try:
            with open(k_file, "r", encoding="utf-8") as f:
                key = bytes.fromhex(f.read().strip())
            
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            basarili_key = os.path.basename(k_file)
            break
        except Exception:
            continue

    if basarili_key and plaintext is not None:
        with open(out_file, "wb") as f:
            f.write(plaintext)

        try:
            os.remove(enc_path)
        except Exception:
            pass

        # Kilidi açılan dosyayı kasadan da temizle
        vault = load_vault()
        sifreli_dosyalar = vault.get("sifreli_dosyalar", {})
        silinecekler = [k for k in sifreli_dosyalar if os.path.basename(k) == os.path.basename(enc_path) or os.path.normpath(k) == os.path.normpath(enc_path)]
        for k in silinecekler:
            del sifreli_dosyalar[k]
        save_vault(vault)

        res_panel = Panel.fit(
            f"[bold green]Kurtarılan Dosya :[/bold green] {out_file}\n"
            f"[bold green]Eşleşen Anahtar  :[/bold green] {basarili_key}\n"
            f"[bold green]Doğrulama        :[/bold green] AES-GCM Mührü Başarılı\n"
            f"[bold yellow]Kasa Durumu      :[/bold yellow] Dosya kaydı kasadan temizlendi.",
            title="[bold green]✓ KİLİT AÇILDI: Dosya Başarıyla Kurtarıldı[/bold green]",
            border_style="green"
        )
        console.print(res_panel)
    else:
        console.print("\n[bold red][-] HATA: Mevcut anahtarların hiçbiri bu dosyayı açamadı![/bold red]\n")

def servis_parolasi_uret():
    servis_adi = console.input("\n[bold white]Hesap / Servis Adı (Örn: Instagram, Wi-Fi, Banka, GitHub): [/bold white]").strip()
    if not servis_adi:
        console.print("[red][-] Servis adı boş bırakılamaz.[/red]")
        return

    try:
        key, sources = acquire_entropy()
    except Exception as e:
        console.print(f"[red][-] Hata: {e}[/red]")
        return

    chars = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*()-_=+"
    parola = "".join(chars[b % len(chars)] for b in key[:24])

    vault = load_vault()
    vault["parolalar"][servis_adi] = {
        "parola": parola,
        "kaynaklar": sources,
        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_vault(vault)

    res_panel = Panel.fit(
        f"[bold cyan]Servis :[/bold cyan] {servis_adi}\n"
        f"[bold green]Parola :[/bold green] [bold white]{parola}[/bold white]\n"
        f"[bold magenta]Kaynak :[/bold magenta] {', '.join(sources)}",
        title="[bold green]✓ MASTER PAROLA ÜRETİLDİ[/bold green]",
        border_style="cyan"
    )
    console.print(res_panel)

def servis_parolasi_sil():
    vault = load_vault()
    parolalar = vault.get("parolalar", {})

    if not parolalar:
        console.print("\n[yellow][!] Kasada silinecek kayıtlı parola bulunmuyor.[/yellow]")
        return

    table = Table(title="[bold red]SİLİNEBİLİR PAROLALAR[/bold red]", border_style="red")
    table.add_column("No", style="bold yellow", justify="center")
    table.add_column("Hesap / Servis", style="bold white")
    table.add_column("Parola", style="dim")
    table.add_column("Tarih", style="dim")

    servis_listesi = list(parolalar.keys())
    for idx, servis in enumerate(servis_listesi, 1):
        info = parolalar[servis]
        table.add_row(str(idx), servis, info.get('parola', ''), info.get('tarih', ''))

    console.print("\n")
    console.print(table)

    secim = console.input("\n[bold red]Silmek istediğiniz numara veya hesap adı (İptal için Enter): [/bold red]").strip()
    if not secim:
        console.print("[dim]Silme işlemi iptal edildi.[/dim]")
        return

    silinecek_servis = None
    if secim.isdigit():
        num = int(secim)
        if 1 <= num <= len(servis_listesi):
            silinecek_servis = servis_listesi[num - 1]
    else:
        if secim in parolalar:
            silinecek_servis = secim

    if not silinecek_servis:
        console.print("[red][-] Geçersiz seçim yapıldı. Parola bulunamadı.[/red]")
        return

    onay = console.input(f"[bold yellow]'{silinecek_servis}' kaydı kasadan kalıcı olarak silinecek. Emin misiniz? (e/h): [/bold yellow]").strip().lower()
    if onay in ["e", "evet", "y", "yes"]:
        del vault["parolalar"][silinecek_servis]
        save_vault(vault)
        console.print(f"[bold green][✓] '{silinecek_servis}' parolası kasadan başarıyla silindi.[/bold green]")
    else:
        console.print("[dim]Silme işlemi iptal edildi.[/dim]")

def kasayi_listele():
    vault = load_vault()
    parolalar = vault.get("parolalar", {})
    dosyalar = vault.get("sifreli_dosyalar", {})

    console.print("\n")
    p_table = Table(title="[bold cyan]KAYITLI GÜÇLÜ PAROLALAR[/bold cyan]", border_style="cyan")
    p_table.add_column("Servis / Hesap", style="bold white")
    p_table.add_column("Parola", style="bold green")
    p_table.add_column("Tarih", style="dim")

    if not parolalar:
        p_table.add_row("Henüz parola kaydı yok.", "-", "-")
    else:
        for servis, info in parolalar.items():
            p_table.add_row(servis, info['parola'], info['tarih'])

    console.print(p_table)
    console.print("\n")

    d_table = Table(title="[bold magenta]KİLİTLENMİŞ DOSYALAR[/bold magenta]", border_style="magenta")
    d_table.add_column("Kilitli Dosya", style="bold yellow")
    d_table.add_column("Anahtar Dosyası", style="dim")
    d_table.add_column("Tarih", style="dim")

    if not dosyalar:
        d_table.add_row("Henüz kilitlenmiş dosya yok.", "-", "-")
    else:
        for enc, info in dosyalar.items():
            d_table.add_row(os.path.basename(enc), os.path.basename(info.get('key_path', '')), info.get('tarih', ''))

    console.print(d_table)
    console.print("\n")

def main():
    while True:
        console.clear()
        rprint(BANNER)
        console.print("\n[bold white]1.[/bold white] [cyan]Yeni Parola Üret[/cyan] [dim](Fiziksel Entropi ile)[/dim]")
        console.print("[bold white]2.[/bold white] [red]Kayıtlı Parola Sil[/red] [dim](Kasadan Parola Kaldır)[/dim]")
        console.print("[bold white]3.[/bold white] [magenta]Dosya Kilitle[/magenta] [dim](Orijinali Silip .lavalock Yapar)[/dim]")
        console.print("[bold white]4.[/bold white] [green]Dosya Kilidini Aç[/green] [dim](Otomatik Kurtarır ve Kasayı Temizler)[/dim]")
        console.print("[bold white]5.[/bold white] [yellow]Kasadaki Parola ve Dosyaları Listele[/yellow]")
        console.print("[bold white]6.[/bold white] [red]Çıkış[/red]")

        secim = console.input("\n[bold cyan]İşlem seçiniz (1-6): [/bold cyan]").strip()

        if secim == "1":
            servis_parolasi_uret()
            console.input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        elif secim == "2":
            servis_parolasi_sil()
            console.input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        elif secim == "3":
            dosya_tam_kilitle()
            console.input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        elif secim == "4":
            dosya_tam_kilidini_ac()
            console.input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        elif secim == "5":
            kasayi_listele()
            console.input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        elif secim == "6":
            console.print("[bold red]\nKasa kapatıldı ve hafıza temizlendi.[/bold red]\n")
            break

if __name__ == "__main__":
    main()