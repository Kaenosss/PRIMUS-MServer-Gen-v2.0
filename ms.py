import os
import sys
import json
import hashlib
import subprocess
import threading
import time
import webbrowser
import requests
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import pygame

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

PROPERTIES_TRANSLATIONS = {
    "allow-flight": "Autoriser le vol",
    "difficulty": "Difficulté (paisible, facile, normal, difficile)",
    "gamemode": "Mode de jeu (survie, créatif, aventure, spectateur)",
    "generate-structures": "Générer les structures",
    "hardcore": "Mode hardcore",
    "level-name": "Nom du monde",
    "level-seed": "Graine du monde (Seed)",
    "max-players": "Nombre maximum de joueurs",
    "motd": "Message d'accueil du serveur",
    "online-mode": "Mode en ligne (comptes officiels requis)",
    "server-port": "Port du serveur",
    "simulation-distance": "Distance de simulation",
    "spawn-protection": "Protection du spawn",
    "view-distance": "Distance de vision",
    "white-list": "Activer la liste blanche"
}

class MinecraftFullManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestionnaire automatisé de serveur Minecraft - PRIMUS CORP")
        self.geometry("950x920")
        self.minsize(850, 800)

        self.is_paused = False

        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        try:
            pygame.mixer.init()
            music_path = os.path.join(base_path, "Luxuria.mp3")
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.1)
            else:
                print("Fichier Luxuria.mp3 introuvable.")
        except Exception as e:
            print(f"Erreur d'initialisation audio : {e}")

        try:
            ico_path = os.path.join(base_path, "logo.ico")
            self.iconbitmap(ico_path)
        except Exception as e:
            print(f"Impossible de charger l'icône de la fenêtre : {e}")

        self.logo_img_large = self.load_primus_logo(size=(260, 75))
        self.logo_img_medium = self.load_primus_logo(size=(160, 46))

        self.server_path = ""
        self.widgets_dict = {}

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.show_welcome_screen()

    def load_primus_logo(self, size=(160, 45)):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_path, "PRIMUS.png")
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            except Exception as e:
                print(f"Erreur chargement PRIMUS.png : {e}")
        return None

    def create_music_player_widget(self, parent):
        player_frame = ctk.CTkFrame(parent, fg_color="#181a1c", corner_radius=6, border_width=1, border_color="#2b2d30")
        player_frame.pack(pady=(0, 8))

        btn_stop = ctk.CTkButton(player_frame, text="⏹", width=24, height=20, fg_color="transparent", hover_color="#2b2d30", text_color="#b52b2b", font=("Arial", 12), command=self.stop_music)
        btn_stop.pack(side="right", padx=2, pady=4)

        btn_pause = ctk.CTkButton(player_frame, text="⏸", width=24, height=20, fg_color="transparent", hover_color="#2b2d30", text_color="#b52b2b", font=("Arial", 12), command=self.pause_music)
        btn_pause.pack(side="right", padx=2, pady=4)

        btn_play = ctk.CTkButton(player_frame, text="▶", width=24, height=20, fg_color="transparent", hover_color="#2b2d30", text_color="#b52b2b", font=("Arial", 12), command=self.play_music)
        btn_play.pack(side="right", padx=2, pady=4)

        slider_vol = ctk.CTkSlider(player_frame, from_=0, to=1, number_of_steps=10, width=90, height=12, button_color="#b52b2b", button_hover_color="#8a1f1f", progress_color="#b52b2b", command=self.change_volume)
        slider_vol.set(0.1)
        slider_vol.pack(side="right", padx=6, pady=4)

    def play_music(self):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            music_path = os.path.join(base_path, "Luxuria.mp3")
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            elif not pygame.mixer.music.get_busy():
                if os.path.exists(music_path):
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.1)
                self.is_paused = False
        except Exception as e:
            print(f"Erreur Play : {e}")

    def pause_music(self):
        try:
            pygame.mixer.music.pause()
            self.is_paused = True
        except Exception as e:
            print(f"Erreur Pause : {e}")

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
            self.is_paused = False
        except Exception as e:
            print(f"Erreur Stop : {e}")

    def change_volume(self, value):
        try:
            pygame.mixer.music.set_volume(float(value))
        except Exception as e:
            print(f"Erreur Volume : {e}")

    def show_welcome_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        center_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        if self.logo_img_large:
            lbl_logo = ctk.CTkLabel(center_frame, text="", image=self.logo_img_large)
            lbl_logo.pack(pady=(0, 5))
        else:
            lbl_title_app = ctk.CTkLabel(center_frame, text="PRIMUS", font=("Arial", 28, "bold"), text_color="#e74c3c")
            lbl_title_app.pack(pady=(0, 5))

        lbl_sub = ctk.CTkLabel(center_frame, text="MServer Gen v2.1 - 2026", font=("Arial", 12, "italic"), text_color="gray")
        lbl_sub.pack(pady=(0, 10))

        self.create_music_player_widget(center_frame)

        known_servers = self.scan_for_servers()

        if known_servers:
            lbl_history = ctk.CTkLabel(center_frame, text="Serveurs existants détectés :", font=("Arial", 13, "bold"), text_color="white")
            lbl_history.pack(anchor="w", padx=10, pady=(0, 5))

            scroll_servers = ctk.CTkScrollableFrame(center_frame, width=320, height=120, fg_color="#202225", corner_radius=6)
            scroll_servers.pack(pady=(0, 15))

            for srv_path in known_servers:
                srv_name = os.path.basename(srv_path)
                btn_srv = ctk.CTkButton(scroll_servers, text=srv_name, anchor="w", fg_color="#2c3e50", hover_color="#34495e", text_color="white", height=32, command=lambda p=srv_path: self.select_server_and_build(p))
                btn_srv.pack(fill="x", padx=5, pady=3)

        btn_browse = ctk.CTkButton(center_frame, text="Parcourir dossier existant...", command=self.load_existing_server, fg_color="#e74c3c", hover_color="#962d22", text_color="white", width=280, height=42, font=("Arial", 14, "bold"))
        btn_browse.pack(pady=8)

        btn_create = ctk.CTkButton(center_frame, text="Nouveau serveur", command=self.open_create_wizard, fg_color="#34495e", hover_color="#2c3e50", text_color="white", width=280, height=42, font=("Arial", 14, "bold"))
        btn_create.pack(pady=8)

    def scan_for_servers(self):
        found = []
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path):
                    if os.path.exists(os.path.join(item_path, "server.properties")):
                        found.append(item_path)
        except Exception:
            pass
            
        return found

    def select_server_and_build(self, folder):
        if os.path.exists(os.path.join(folder, "server.properties")):
            self.build_main_interface()
            self.set_active_server(folder)
        else:
            messagebox.showerror("Erreur", "Ce dossier ne contient pas de fichier server.properties valide !")

    def build_main_interface(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(15, 5))

        title_left_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_left_frame.pack(side="left", anchor="w")

        self.lbl_title_app = ctk.CTkLabel(title_left_frame, text="MServer Gen v2.1", font=("Arial", 22, "bold"), text_color="#e74c3c")
        self.lbl_title_app.pack(anchor="w")

        self.lbl_team = ctk.CTkLabel(title_left_frame, text="PRIMUS CORP - 2026", font=("Arial", 11, "italic"), text_color="gray")
        self.lbl_team.pack(anchor="w")

        right_header_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header_container.pack(side="right", anchor="e")

        if self.logo_img_medium:
            lbl_logo_right = ctk.CTkLabel(right_header_container, text="", image=self.logo_img_medium)
            lbl_logo_right.pack(anchor="e", pady=(0, 4))

        self.create_music_player_widget(right_header_container)

        self.top_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=10)

        self.path_info_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.path_info_frame.pack(side="left", fill="x", expand=True)

        self.lbl_path = ctk.CTkLabel(self.path_info_frame, text="Aucun serveur sélectionné", font=("Arial", 12, "italic"), text_color="gray", anchor="w")
        self.lbl_path.pack(anchor="w", padx=5)

        self.lbl_detected_version = ctk.CTkLabel(self.path_info_frame, text="", font=("Arial", 11, "bold"), text_color="#3498db", anchor="w")
        self.lbl_detected_version.pack(anchor="w", padx=5, pady=(2, 0))

        self.btn_change_server = ctk.CTkButton(self.top_frame, text="Changer de serveur", command=self.show_welcome_screen, fg_color="#34495e", hover_color="#2c3e50", text_color="white")
        self.btn_change_server.pack(side="right", padx=5)

        self.tabview = ctk.CTkTabview(self.main_container, segmented_button_selected_color="#e74c3c", segmented_button_selected_hover_color="#c0392b")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_general = self.tabview.add("Paramètres")
        self.tab_advanced = self.tabview.add("Avancé")
        self.tab_java = self.tabview.add("Java")
        self.tab_info = self.tabview.add("A propos")

        self.scroll_general = ctk.CTkScrollableFrame(self.tab_general, fg_color="transparent")
        self.scroll_general.pack(fill="both", expand=True)

        adv_warning_frame = ctk.CTkFrame(self.tab_advanced, fg_color="#c0392b", corner_radius=6)
        adv_warning_frame.pack(fill="x", padx=10, pady=10)
        lbl_adv_warn = ctk.CTkLabel(adv_warning_frame, text="Attention : Paramètres avancés du server.properties.\nÀ ne modifier que si vous savez exactement ce que vous faites !", font=("Arial", 11, "bold"), text_color="white")
        lbl_adv_warn.pack(padx=10, pady=8)

        self.scroll_advanced = ctk.CTkScrollableFrame(self.tab_advanced, fg_color="transparent")
        self.scroll_advanced.pack(fill="both", expand=True)

        self.setup_java_tab()
        self.setup_about_tab()

        self.bottom_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=15)

        self.btn_save = ctk.CTkButton(self.bottom_frame, text="Appliquer", command=self.save_properties, state="disabled", font=("Arial", 13, "bold"), fg_color="#e74c3c", hover_color="#c0392b", text_color="white", height=40, width=280)
        self.btn_save.pack(side="left", padx=(0, 10))

        self.btn_launch = ctk.CTkButton(self.bottom_frame, text="Démarrer", command=self.launch_server_bat, state="disabled", font=("Arial", 13, "bold"), fg_color="#2ecc71", hover_color="#27ae60", text_color="white", height=40, width=280)
        self.btn_launch.pack(side="right", padx=(10, 0))

    def load_existing_server(self):
        folder = filedialog.askdirectory(title="Sélectionnez le dossier de votre serveur Minecraft")
        if folder:
            props_file = os.path.join(folder, "server.properties")
            if not os.path.exists(props_file):
                messagebox.showerror("Erreur", "Aucun fichier server.properties trouvé dans ce dossier ! Ce n'est pas un dossier serveur valide.")
                return
            self.build_main_interface()
            self.set_active_server(folder)

    def detect_minecraft_version(self, folder):
        v_json_path = os.path.join(folder, "version.json")
        if os.path.exists(v_json_path):
            try:
                with open(v_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "name" in data:
                        return f"Version détectée : {data['name']}"
            except Exception:
                pass

        logs_path = os.path.join(folder, "logs", "latest.log")
        if os.path.exists(logs_path):
            try:
                with open(logs_path, "r", encoding="utf-8", errors="ignore") as f:
                    for _ in range(50):
                        line = f.readline()
                        if not line:
                            break
                        if "Starting minecraft server version" in line:
                            parts = line.split("Starting minecraft server version")
                            if len(parts) > 1:
                                v_str = parts[1].strip().split()[0]
                                return f"Version détectée : {v_str}"
            except Exception:
                pass

        jar_path = os.path.join(folder, "server.jar")
        if os.path.exists(jar_path):
            return "Version détectée : Fichier server.jar présent (précision exacte inconnue)"

        return "Version détectée : Inconnue"

    def set_active_server(self, folder):
        self.server_path = folder
        self.lbl_path.configure(text=f"Dossier actif : {folder}", text_color="#2ecc71")
        
        detected_text = self.detect_minecraft_version(folder)
        self.lbl_detected_version.configure(text=detected_text)

        self.btn_save.configure(state="normal")
        self.btn_launch.configure(state="normal")
        
        props_file = os.path.join(self.server_path, "server.properties")
        self.parse_and_display_properties(props_file)

    def launch_server_bat(self):
        if not self.server_path:
            messagebox.showerror("Erreur", "Aucun serveur sélectionné.")
            return
        bat_path = os.path.join(self.server_path, "start.bat")
        if os.path.exists(bat_path):
            subprocess.Popen(f'start cmd /k "{bat_path}"', shell=True)
        else:
            messagebox.showerror("Erreur", "Le fichier de lancement est introuvable.")

    def setup_java_tab(self):
        scroll_java = ctk.CTkScrollableFrame(self.tab_java, fg_color="transparent")
        scroll_java.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll_java, text="Gestionnaire d'environnements Eclipse Temurin", font=("Arial", 16, "bold"), text_color="#e74c3c").pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(scroll_java, text="Téléchargez et assignez la version de Java adaptée à votre version de Minecraft.", font=("Arial", 11), text_color="gray", justify="left").pack(anchor="w", pady=(0, 15))

        java_versions = [
            ("Java 8 (Anciennes versions / Legacy)", "8"),
            ("Java 11 (Versions 1.17)", "11"),
            ("Java 17 (Versions 1.18 - 1.20.4)", "17"),
            ("Java 21 (Versions 1.20.5 - 1.21+)", "21"),
            ("Java 25 (Dernières versions & Futurs)", "25")
        ]

        for desc, v_num in java_versions:
            frame_item = ctk.CTkFrame(scroll_java, fg_color="#202225", corner_radius=6)
            frame_item.pack(fill="x", pady=6, padx=5)

            lbl_desc = ctk.CTkLabel(frame_item, text=desc, font=("Arial", 12, "bold"))
            lbl_desc.pack(side="left", padx=15, pady=12)

            btn_path_assign = ctk.CTkButton(frame_item, text="Utiliser pour ce serveur", width=160, fg_color="#34495e", hover_color="#2c3e50", command=lambda vn=v_num: self.assign_java_version(vn))
            btn_path_assign.pack(side="right", padx=10, pady=12)

            btn_dl = ctk.CTkButton(frame_item, text="Télécharger (PowerShell)", width=170, fg_color="#e74c3c", hover_color="#c0392b", command=lambda vn=v_num: self.download_temurin_ps(vn))
            btn_dl.pack(side="right", padx=5, pady=12)

    def download_temurin_ps(self, version):
        ps_script = f"""
        $version = "{version}"
        $apiUrl = "https://api.adoptium.net/v3/binary/latest/$version/ga/windows/x64/jre/hotspot/normal/eclipse"
        try {{
            Write-Host "Lancement du téléchargement direct pour Java $version..." -ForegroundColor Cyan
            $destDir = "$PSScriptRoot\\java_runtimes\\java$version"
            if (!(Test-Path $destDir)) {{ New-Item -ItemType Directory -Force -Path $destDir | Out-Null }}
            $zipPath = "$env:TEMP\\openjdk-$version-jre.zip"
            $webClient = New-Object System.Net.WebClient
            $webClient.DownloadFile($apiUrl, $zipPath)
            Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\\java_extract" -Force
            $extractedFolder = Get-ChildItem "$env:TEMP\\java_extract" | Select-Object -First 1
            Move-Item "$env:TEMP\\java_extract\\$($extractedFolder.Name)\\*" -Destination $destDir -Force
            Remove-Item $zipPath -Force
            Write-Host "Java $version installé avec succès !" -ForegroundColor Green
        }} catch {{
            Write-Host "Erreur : $_" -ForegroundColor Red
        }}
        pause
        """
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_dir, "dl_java.ps1")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(ps_script)

        subprocess.Popen(f'start powershell -ExecutionPolicy Bypass -File "{script_path}"', shell=True)

    def assign_java_version(self, version):
        if not self.server_path:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un serveur actif.")
            return

        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        java_dir = os.path.join(base_dir, "java_runtimes", f"java{version}")
        java_exe = os.path.join(java_dir, "bin", "java.exe")

        if not os.path.exists(java_exe):
            if messagebox.askyesno("Dossier introuvable", f"Le dossier 'java_runtimes/java{version}' n'est pas installé localement.\nVoulez-vous configurer le start.bat avec la commande globale 'java' ?"):
                java_exe = "java"
            else:
                return

        bat_path = os.path.join(self.server_path, "start.bat")
        if not os.path.exists(bat_path):
            messagebox.showerror("Erreur", "Le fichier start.bat est introuvable dans ce serveur.")
            return

        bat_content = f'@echo off\ncd /d "%~dp0"\n"{java_exe}" -Xms4096M -Xmx4096M -XX:+UseZGC -jar server.jar nogui\npause\n'
        with open(bat_path, "w", encoding="oem") as f:
            f.write(bat_content)

        messagebox.showinfo("Succès", f"Le chemin Java pour ce serveur a été mis à jour vers Java {version} avec succès !")

    def open_create_wizard(self):
        wizard = ctk.CTkToplevel(self)
        wizard.title("Assistant")
        wizard.geometry("520x610")
        wizard.grab_set()

        ctk.CTkLabel(wizard, text="Création du serveur", font=("Arial", 18, "bold")).pack(pady=15)

        ctk.CTkLabel(wizard, text="Nom du dossier du serveur", font=("Arial", 12)).pack(anchor="w", padx=30)
        entry_name = ctk.CTkEntry(wizard, width=440)
        entry_name.insert(0, "server")
        entry_name.pack(padx=30, pady=5)

        ctk.CTkLabel(wizard, text="Version", font=("Arial", 12)).pack(anchor="w", padx=30, pady=(10, 0))
        version_combobox = ctk.CTkComboBox(wizard, width=440, values=["Chargement des versions..."])
        version_combobox.pack(padx=30, pady=5)

        def fetch_versions():
            try:
                res = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json")
                data = res.json()
                valid_releases = [v['id'] for v in data['versions'] if v['type'] == 'release']
                version_combobox.configure(values=valid_releases)
                if valid_releases:
                    version_combobox.set(valid_releases[0])
            except Exception:
                version_combobox.configure(values=["1.21.4"])
                version_combobox.set("1.21.4")

        threading.Thread(target=fetch_versions, daemon=True).start()

        ctk.CTkLabel(wizard, text="Mémoire RAM allouée", font=("Arial", 12)).pack(anchor="w", padx=30, pady=(10, 0))
        ram_label_val = ctk.CTkLabel(wizard, text="4 Go (4096 Mo)", font=("Arial", 12, "bold"), text_color="#e74c3c")
        ram_label_val.pack(padx=30, anchor="w")

        snapping_points = [2048, 4096, 6144, 8192, 10240, 12288, 14336, 16384]

        def update_ram_label(value):
            raw_val = int(value)
            closest_point = min(snapping_points, key=lambda x: abs(x - raw_val))
            ram_slider.set(closest_point)
            val_go = int(closest_point / 1024)
            ram_label_val.configure(text=f"{val_go} Go ({closest_point} Mo)")

        ram_slider = ctk.CTkSlider(wizard, from_=2048, to=16384, number_of_steps=7, command=update_ram_label, width=440)
        ram_slider.set(4096)
        ram_slider.pack(padx=30, pady=5)

        eula_var = ctk.BooleanVar(value=False)
        chk_eula = ctk.CTkCheckBox(wizard, text="Accepter l'EULA (obligatoire)", variable=eula_var)
        chk_eula.pack(padx=30, pady=20)

        def start_generation():
            srv_name = entry_name.get().strip()
            selected_version = version_combobox.get()
            final_ram_mo = int(ram_slider.get())
            ram_arg = f"{final_ram_mo}M"

            if not srv_name:
                messagebox.showerror("Erreur", "Veuillez entrer un nom valide.")
                return
            if not eula_var.get():
                messagebox.showerror("Erreur", "Vous devez accepter les conditions pour continuer.")
                return

            base_dir = filedialog.askdirectory(title="Choisissez l'emplacement où créer le dossier du serveur")
            if not base_dir:
                return

            target_dir = os.path.join(base_dir, srv_name)
            wizard.destroy()

            self.build_main_interface()
            threading.Thread(target=self.generate_server_core, args=(target_dir, selected_version, ram_arg), daemon=True).start()

        btn_go = ctk.CTkButton(wizard, text="Créer", command=start_generation, fg_color="#e74c3c", hover_color="#c0392b", text_color="white", height=40)
        btn_go.pack(padx=30, pady=15, fill="x")

    def generate_server_core(self, target_dir, version_id, ram):
        try:
            os.makedirs(target_dir, exist_ok=True)
            import shutil
            java_path = shutil.which("java") or "java"

            res = requests.get("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json")
            manifest = res.json()

            version_url = next((v['url'] for v in manifest['versions'] if v['id'] == version_id), "")
            v_meta = requests.get(version_url).json()
            server_download = v_meta.get('downloads', {}).get('server', {})
            jar_url = server_download.get('url')
            expected_sha1 = server_download.get('sha1')

            jar_path = os.path.join(target_dir, "server.jar")
            jar_res = requests.get(jar_url)
            with open(jar_path, "wb") as f:
                f.write(jar_res.content)

            sha1 = hashlib.sha1(jar_res.content).hexdigest()
            if sha1 != expected_sha1:
                raise Exception("Erreur d'intégrité sur le fichier téléchargé.")

            with open(os.path.join(target_dir, "eula.txt"), "w", encoding="utf-8") as f:
                f.write("eula=true\n")

            bat_content = f'@echo off\ncd /d "%~dp0"\n"{java_path}" -Xms{ram} -Xmx{ram} -XX:+UseZGC -jar server.jar nogui\npause\n'
            with open(os.path.join(target_dir, "start.bat"), "w", encoding="oem") as f:
                f.write(bat_content)

            cmd_command = f'start "Serveur Minecraft - Initialisation" cmd /c ""{java_path}" -Xms{ram} -Xmx{ram} -XX:+UseZGC -jar server.jar nogui"'
            subprocess.Popen(cmd_command, shell=True, cwd=target_dir)

            log_path = os.path.join(target_dir, "logs", "latest.log")
            while True:
                time.sleep(1)
                if os.path.exists(log_path):
                    try:
                        with open(log_path, "r", encoding="utf-8", errors="ignore") as log_file:
                            if "Done (" in log_file.read() or "For help, type" in log_file.read():
                                time.sleep(2)
                                subprocess.run('taskkill /f /im java.exe', shell=True, capture_output=True)
                                break
                    except Exception:
                        pass

            self.after(0, lambda: self.set_active_server(target_dir))
            self.after(0, lambda: messagebox.showinfo("Succès", f"Serveur version {version_id} installé avec succès !"))
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: messagebox.showerror("Erreur critique", f"Une erreur est survenue :\n{err_msg}"))

    def parse_and_display_properties(self, file_path):
        for widget in self.scroll_general.winfo_children():
            widget.destroy()
        for widget in self.scroll_advanced.winfo_children():
            widget.destroy()
        self.widgets_dict.clear()

        if not os.path.exists(file_path):
            return

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        file_props = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                file_props[k.strip()] = v.strip()

        for key, display_label in PROPERTIES_TRANSLATIONS.items():
            if key not in file_props:
                continue
            is_motd = (key == "motd")
            self.create_property_widget(self.scroll_general, key, display_label, file_props[key], is_link=is_motd)

        for key, val in file_props.items():
            if key not in PROPERTIES_TRANSLATIONS:
                self.create_property_widget(self.scroll_advanced, key, key, val, is_link=False)

    def create_property_widget(self, parent_scroll, key, display_label, val, is_link=False):
        row_frame = ctk.CTkFrame(parent_scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=6, padx=10)

        if is_link:
            lbl = ctk.CTkLabel(row_frame, text=display_label, width=320, anchor="w", font=("Arial", 12, "bold", "underline"), text_color="#3498db", cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e: webbrowser.open("https://minecraft.tools/fr/motd.php"))
        else:
            lbl = ctk.CTkLabel(row_frame, text=display_label, width=320, anchor="w", font=("Arial", 12, "bold"))
            lbl.pack(side="left")

        if val.lower() == "true" or val.lower() == "false":
            var = ctk.BooleanVar(value=(val.lower() == "true"))
            widget = ctk.CTkSwitch(row_frame, text="", variable=var, width=50, progress_color="#e74c3c")
            widget.pack(side="right", padx=10)
            self.widgets_dict[key] = (var, "bool")
        else:
            widget = ctk.CTkEntry(row_frame, width=280, height=30)
            widget.insert(0, val)
            widget.pack(side="right", padx=10)
            self.widgets_dict[key] = (widget, "entry")

    def save_properties(self):
        if not self.server_path:
            return

        props_file = os.path.join(self.server_path, "server.properties")
        with open(props_file, "r", encoding="utf-8", errors="ignore") as f:
            content_lines = f.readlines()

        updated_keys = set()
        new_content = []

        for line in content_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key = stripped.split("=", 1)[0]
                if key in self.widgets_dict:
                    widget, w_type = self.widgets_dict[key]
                    val_str = "true" if (w_type == "bool" and widget.get()) else ("false" if w_type == "bool" else widget.get())
                    new_content.append(f"{key}={val_str}\n")
                    updated_keys.add(key)
                else:
                    new_content.append(line)
            else:
                new_content.append(line)

        for key, (widget, w_type) in self.widgets_dict.items():
            if key not in updated_keys:
                val_str = "true" if (w_type == "bool" and widget.get()) else ("false" if w_type == "bool" else widget.get())
                new_content.append(f"{key}={val_str}\n")

        with open(props_file, "w", encoding="utf-8") as f:
            f.writelines(new_content)

        messagebox.showinfo("Enregistré", "Les modifications ont été enregistrées avec succès !")

    def setup_about_tab(self):
        frame = ctk.CTkFrame(self.tab_info, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="MServer Gen v2.1", font=("Arial", 20, "bold"), text_color="#e74c3c").pack(pady=(0, 5))
        ctk.CTkLabel(frame, text="Outil complet d'automatisation et de gestion de serveurs Minecraft.", font=("Arial", 13), justify="center").pack(pady=(0, 15))

        ctk.CTkLabel(frame, text="Technologies utilisées :", font=("Arial", 14, "bold"), text_color="#3498db").pack(anchor="w", pady=(5, 2))
        techs_text = "- Python\n- CustomTkinter\n- Pygame\n- Requests & Subprocess"
        ctk.CTkLabel(frame, text=techs_text, font=("Arial", 12), justify="left").pack(anchor="w", padx=10, pady=(0, 15))

        ctk.CTkLabel(frame, text="Dépôt officiel du projet :", font=("Arial", 14, "bold"), text_color="#3498db").pack(anchor="w", pady=(5, 2))
        lbl_link = ctk.CTkLabel(frame, text="https://github.com/Kaenosss/PRIMUS-MServer-Gen-v2.0", font=("Arial", 12, "underline"), text_color="#2ecc71", cursor="hand2")
        lbl_link.pack(anchor="w", padx=10, pady=(0, 15))
        lbl_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Kaenosss/PRIMUS-MServer-Gen-v2.0"))

        ctk.CTkLabel(frame, text="Mentions légales & Copyright :", font=("Arial", 14, "bold"), text_color="#3498db").pack(anchor="w", pady=(5, 2))
        legal_text = "© 2026 PRIMUS CORP. Tous droits réservés.\nCe logiciel est un outil non officiel de gestion de serveurs Minecraft.\nMinecraft est une marque déposée de Mojang Synergies AB."
        ctk.CTkLabel(frame, text=legal_text, font=("Arial", 11, "italic"), text_color="gray", justify="left").pack(anchor="w", padx=10, pady=(0, 10))

if __name__ == "__main__":
    try:
        app = MinecraftFullManager()
        app.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("\n[ERREUR CRITIQUE] Le programme a crashé. Appuyez sur Entrée pour quitter...")