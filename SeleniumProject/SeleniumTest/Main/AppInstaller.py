import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os

try:
    from ppadb.client import Client as AdbClient
except ImportError:
    AdbClient = None

# ── Device registry ──────────────────────────────────────────────────────────
USER_DATA = {
    "TCL TV Home":   "192.168.0.160",
    "Fire Cube":     "10.1.92.58",
    "Mi TV":         "10.1.92.59",
    "Chromecast":    "10.1.92.60",
    "Fire TV":       "10.1.92.61",
    "TCL TV":        "10.1.92.46",
    "Philips TV":    "10.1.92.36",
    "Panasonic TV":  "10.1.92.35",
    "Sony TV ME":    "10.1.92.34",
    "Grundig TV":    "10.1.92.41",
    "Telefunken TV": "10.1.92.44",
    "Sony TV HE":    "10.1.92.74",
}

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#0d0f14"
SURFACE = "#161a23"
CARD    = "#1e2433"
BORDER  = "#2a3045"
ACCENT  = "#00c8ff"
ACCENT2 = "#0078d4"
SUCCESS = "#00e676"
WARNING = "#ffab00"
ERROR   = "#ff5252"
TEXT    = "#e8eaf0"
SUBTEXT = "#7a8299"
MONO    = ("Consolas", 9)
UI      = ("Segoe UI", 10)
HEAD    = ("Segoe UI Semibold", 11)
BIG     = ("Segoe UI Light", 22)


class APKInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart TV · APK Installer")
        self.geometry("700x680")
        self.minsize(620, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._client = None
        self._connected_ip = None

        self._build_ui()
        self._run(self._start_daemon)

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="⬡  APK Installer", font=BIG, bg=BG, fg=TEXT).pack(side="left")
        self._dot = tk.Label(hdr, text="●", font=("Segoe UI", 14), bg=BG, fg=SUBTEXT)
        self._dot.pack(side="right", padx=(0, 4))
        self._status_lbl = tk.Label(hdr, text="Initialising…", font=UI, bg=BG, fg=SUBTEXT)
        self._status_lbl.pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # ── Device card ──
        dev = self._card("Device Selection")

        tk.Label(dev, text="Select Device", font=UI, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))

        dd_row = tk.Frame(dev, bg=CARD)
        dd_row.pack(fill="x", pady=(0, 8))
        dd_row.columnconfigure(0, weight=1)

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Dark.TCombobox",
                        fieldbackground=SURFACE, background=SURFACE,
                        foreground=TEXT, arrowcolor=ACCENT,
                        selectbackground=ACCENT2, selectforeground=TEXT,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.map("Dark.TCombobox", fieldbackground=[("readonly", SURFACE)],
                  foreground=[("readonly", TEXT)])
        style.configure("Accent.Horizontal.TProgressbar",
                        troughcolor=SURFACE, background=ACCENT,
                        darkcolor=ACCENT, lightcolor=ACCENT, bordercolor=CARD)

        self._device_var = tk.StringVar()
        self._dropdown = ttk.Combobox(
            dd_row, textvariable=self._device_var,
            values=list(USER_DATA.keys()),
            state="readonly", style="Dark.TCombobox", font=UI
        )
        self._dropdown.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 8))
        self._dropdown.set(list(USER_DATA.keys())[0])
        self._dropdown.bind("<<ComboboxSelected>>", self._on_device_change)

        self._ip_lbl = tk.Label(dd_row, text=list(USER_DATA.values())[0],
                                font=MONO, bg=SURFACE, fg=ACCENT,
                                padx=10, pady=6, relief="flat",
                                highlightthickness=1, highlightbackground=BORDER)
        self._ip_lbl.grid(row=0, column=1)

        # Connect / Disconnect
        btn_row = tk.Frame(dev, bg=CARD)
        btn_row.pack(fill="x", pady=(4, 0))
        self._btn_connect = self._btn(btn_row, "Connect", self._on_connect, ACCENT2)
        self._btn_connect.pack(side="left", padx=(0, 8))
        self._btn_disconnect = self._btn(btn_row, "Disconnect", self._on_disconnect, SURFACE)
        self._btn_disconnect.pack(side="left")
        self._conn_badge = tk.Label(btn_row, text="", font=UI, bg=CARD, fg=SUCCESS)
        self._conn_badge.pack(side="left", padx=12)

        # ── APK card ──
        apk = self._card("APK Install")

        tk.Label(apk, text="Package Name", font=UI, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))
        self._pkg_var = tk.StringVar(value="com.vodafone.vtv.atv")
        self._entry(apk, self._pkg_var).pack(fill="x", ipady=5, pady=(0, 10))

        tk.Label(apk, text="APK File", font=UI, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))
        apk_row = tk.Frame(apk, bg=CARD)
        apk_row.pack(fill="x", pady=(0, 10))
        apk_row.columnconfigure(0, weight=1)
        self._apk_var = tk.StringVar()
        self._entry(apk_row, self._apk_var).grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 8))
        self._btn(apk_row, "Browse…", self._on_browse, SURFACE).grid(row=0, column=1)

        # Options
        opt = tk.Frame(apk, bg=CARD)
        opt.pack(fill="x", pady=(0, 12))
        self._uninstall_first = tk.BooleanVar(value=True)
        self._show_version    = tk.BooleanVar(value=True)
        for text, var in [("Uninstall before installing", self._uninstall_first),
                          ("Show version after install",  self._show_version)]:
            tk.Checkbutton(opt, text=text, variable=var,
                           bg=CARD, fg=TEXT, selectcolor=SURFACE,
                           activebackground=CARD, activeforeground=TEXT,
                           font=UI, cursor="hand2").pack(anchor="w")

        self._btn_install = self._btn(apk, "  ▶  Install APK  ", self._on_install,
                                      ACCENT2, font=("Segoe UI Semibold", 11))
        self._btn_install.pack(fill="x", ipady=8, pady=(4, 0))

        self._progress = ttk.Progressbar(apk, style="Accent.Horizontal.TProgressbar",
                                          mode="indeterminate")
        self._progress.pack(fill="x", pady=(8, 0))

        # ── Log ──
        self._build_log()

    def _card(self, title):
        outer = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="x", padx=24, pady=(0, 12))
        hdr = tk.Frame(outer, bg=CARD)
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(hdr, text=title, font=HEAD, bg=CARD, fg=ACCENT).pack(side="left")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=14)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=10)
        return inner

    def _build_log(self):
        outer = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        hdr = tk.Frame(outer, bg=CARD)
        hdr.pack(fill="x", padx=14, pady=(8, 4))
        tk.Label(hdr, text="Output Log", font=HEAD, bg=CARD, fg=ACCENT).pack(side="left")
        self._btn(hdr, "Clear", self._clear_log, SURFACE).pack(side="right")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=14)
        self._log = scrolledtext.ScrolledText(
            outer, bg=SURFACE, fg=TEXT, font=MONO,
            relief="flat", state="disabled", wrap="word", padx=8, pady=6, height=8
        )
        self._log.pack(fill="both", expand=True, padx=8, pady=8)
        self._log.tag_config("ok",   foreground=SUCCESS)
        self._log.tag_config("err",  foreground=ERROR)
        self._log.tag_config("warn", foreground=WARNING)
        self._log.tag_config("info", foreground=ACCENT)
        self._log.tag_config("dim",  foreground=SUBTEXT)

    def _btn(self, parent, text, cmd, bg, font=UI):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=TEXT, activebackground=ACCENT2,
                         activeforeground=TEXT, font=font,
                         relief="flat", cursor="hand2", padx=12, pady=4, bd=0)

    def _entry(self, parent, var):
        return tk.Entry(parent, textvariable=var, font=UI,
                        bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
                        relief="flat", highlightthickness=1,
                        highlightbackground=BORDER, highlightcolor=ACCENT)

    # ── Logging ───────────────────────────────────────────────────────────────
    def _write(self, msg, tag=""):
        def _do():
            self._log.config(state="normal")
            self._log.insert("end", msg + "\n", tag)
            self._log.see("end")
            self._log.config(state="disabled")
        self.after(0, _do)

    def ok(self, m):   self._write(f"✔  {m}", "ok")
    def err(self, m):  self._write(f"✖  {m}", "err")
    def warn(self, m): self._write(f"⚠  {m}", "warn")
    def info(self, m): self._write(f"›  {m}", "info")
    def dim(self, m):  self._write(f"   {m}", "dim")

    def _set_status(self, text, colour):
        self.after(0, lambda: (
            self._status_lbl.config(text=text, fg=colour),
            self._dot.config(fg=colour)
        ))

    def _clear_log(self):
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.config(state="disabled")

    def _busy(self, on):
        self.after(0, lambda: (
            self._progress.start(12) if on else self._progress.stop(),
            self._btn_install.config(state="disabled" if on else "normal")
        ))

    def _run(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    # ── Event handlers ────────────────────────────────────────────────────────
    def _on_device_change(self, _=None):
        name = self._device_var.get()
        self._ip_lbl.config(text=USER_DATA.get(name, ""))
        if self._connected_ip and self._connected_ip != USER_DATA.get(name):
            self.after(0, lambda: self._conn_badge.config(text=""))

    def _on_browse(self):
        path = filedialog.askopenfilename(
            title="Select APK file",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if path:
            self._apk_var.set(path)

    def _on_connect(self):
        name = self._device_var.get()
        ip   = USER_DATA.get(name)
        if not ip:
            messagebox.showwarning("No Device", "Select a device first.")
            return
        self._run(self._connect_device, ip, name)

    def _connect_device(self, ip, name):
        self.info(f"Connecting to {name} ({ip}:5555) …")
        if not self._client:
            self._init_client()
            if not self._client:
                return
        try:
            self._client.remote_connect(ip, 5555)
            devices = self._client.devices()
            if devices:
                self._connected_ip = ip
                self.ok(f"Connected: {devices[0].serial}")
                self._set_status(f"Connected · {name}", SUCCESS)
                self.after(0, lambda: self._conn_badge.config(text="● Connected", fg=SUCCESS))
            else:
                self.err("No device visible after connect. Check ADB / TV settings.")
        except Exception as e:
            self.err(f"Connection failed: {e}")

    def _on_disconnect(self):
        ip = self._connected_ip or USER_DATA.get(self._device_var.get())
        if not ip:
            messagebox.showinfo("Not Connected", "No active connection to disconnect.")
            return
        self._run(self._disconnect_device, ip)

    def _disconnect_device(self, ip):
        self.info(f"Disconnecting {ip} …")
        try:
            if self._client:
                self._client.remote_disconnect(ip)
            subprocess.run(["adb", "kill-server"], capture_output=True, text=True)
            self._connected_ip = None
            self._client = None
            self.ok("Disconnected. ADB server stopped.")
            self._set_status("Disconnected", WARNING)
            self.after(0, lambda: self._conn_badge.config(text=""))
        except Exception as e:
            self.err(f"Disconnect error: {e}")

    def _on_install(self):
        name = self._device_var.get()
        ip   = USER_DATA.get(name)
        pkg  = self._pkg_var.get().strip()
        apk  = self._apk_var.get().strip()

        if not ip:
            messagebox.showwarning("No Device", "Select a device.")
            return
        if not pkg:
            messagebox.showwarning("Missing Package", "Enter the package name.")
            return
        if not apk or not os.path.isfile(apk):
            messagebox.showwarning("Missing APK", "Browse to a valid .apk file.")
            return

        self._run(self._install_flow, ip, name, pkg, apk,
                  self._uninstall_first.get(), self._show_version.get())

    # ── Core install flow ─────────────────────────────────────────────────────
    def _install_flow(self, ip, name, pkg, apk, uninstall_first, show_version):
        self._busy(True)
        try:
            if not self._client:
                self._init_client()
                if not self._client:
                    return

            self.info(f"Connecting to {name} ({ip}:5555) …")
            self._client.remote_connect(ip, 5555)
            devices = self._client.devices()

            if not devices:
                self.err("No devices found after connect. Check ADB debugging on TV.")
                return

            device = devices[0]
            self._connected_ip = ip
            self.ok(f"Device: {device.serial}")
            self.after(0, lambda: self._conn_badge.config(text="● Connected", fg=SUCCESS))

            # Current version
            try:
                ver = device.shell(f"dumpsys package {pkg} | grep versionName")
                if ver.strip():
                    self.dim(f"Current version → {ver.strip()}")
                else:
                    self.warn(f"Package '{pkg}' not currently installed.")
            except Exception as e:
                self.warn(f"Version check error: {e}")

            # Uninstall first?
            if uninstall_first:
                self.info("Uninstalling existing package…")
                try:
                    device.uninstall(pkg)
                    self.ok("Package uninstalled.")
                except Exception as e:
                    self.warn(f"Uninstall skipped (may not be installed): {e}")

            # Install
            self.info(f"Installing {os.path.basename(apk)} …")
            device.install(apk)

            if device.is_installed(pkg):
                self.ok("Installation successful! ✓")
                # Post-install version
                if show_version:
                    try:
                        new_ver = device.shell(f"dumpsys package {pkg} | grep versionName")
                        if new_ver.strip():
                            self.ok(f"Installed version → {new_ver.strip()}")
                    except Exception:
                        pass
                self._set_status("Install complete ✓", SUCCESS)
            else:
                self.err("Install completed but package not detected — check APK/package name.")
                self._set_status("Install failed", ERROR)

        except Exception as e:
            self.err(f"Install error: {e}")
            self._set_status("Error", ERROR)
        finally:
            self._busy(False)

    # ── ADB helpers ───────────────────────────────────────────────────────────
    def _start_daemon(self):
        self.info("Starting ADB daemon…")
        try:
            subprocess.run(["adb", "start-server"], check=True,
                           capture_output=True, text=True)
            self.ok("ADB daemon started.")
            self._set_status("ADB ready", SUCCESS)
            self._init_client()
        except FileNotFoundError:
            self.err("'adb' not found — add Android platform-tools to PATH.")
            self._set_status("ADB missing", ERROR)
        except subprocess.CalledProcessError as e:
            self.err(f"Daemon error: {e.stderr.strip()}")
            self._set_status("Daemon error", ERROR)

    def _init_client(self):
        if AdbClient is None:
            self.err("ppadb not installed. Run: pip install pure-python-adb")
            return
        try:
            self._client = AdbClient(host="127.0.0.1", port=5037)
        except Exception as e:
            self.err(f"ADB client init failed: {e}")


if __name__ == "__main__":
    app = APKInstallerApp()
    app.mainloop()
