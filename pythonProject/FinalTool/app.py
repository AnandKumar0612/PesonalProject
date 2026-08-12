import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os

try:
    from ppadb.client import Client as AdbClient
except ImportError:
    AdbClient = None

# Default target IP fallback if the entry is left blank
DEFAULT_IP = "192.168.0.50"

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#0d0f14"
SURFACE = "#161a23"
CARD    = "#1e2433"
BORDER  = "#2a3045"
ACCENT  = "#00c8ff"
ACCENT2 = "#0078d4"
SUCCESS = "#00e676"
WARNING = "#ffab00"
ERROR   = "#ff5252"
RED_BTN = "#7a1a1a"
TEXT    = "#e8eaf0"
SUBTEXT = "#7a8299"
MONO    = ("Consolas", 9)
UI      = ("Segoe UI", 10)
HEAD    = ("Segoe UI Semibold", 11)
BIG     = ("Segoe UI Light", 20)


class ADBManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart TV · ADB Manager")
        self.geometry("760x820")
        self.minsize(680, 720)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Session state — shared across install & text send
        self._client: AdbClient | None = None
        self._device = None           # active ppadb device object
        self._connected_ip: str | None = None

        self._build_ui()
        self._run(self._start_daemon)

    # ═════════════════════════════ UI BUILD ══════════════════════════════════

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="⬡  Smart TV · ADB Manager", font=BIG,
                 bg=BG, fg=TEXT).pack(side="left")
        self._dot = tk.Label(hdr, text="●", font=("Segoe UI", 14), bg=BG, fg=SUBTEXT)
        self._dot.pack(side="right", padx=(0, 4))
        self._status_lbl = tk.Label(hdr, text="Initialising…", font=UI, bg=BG, fg=SUBTEXT)
        self._status_lbl.pack(side="right")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=10)

        # ── Sections ──
        self._build_device_section()
        self._build_install_section()
        self._build_text_section()
        self._build_log()

    # ── Device card ──────────────────────────────────────────────────────────
    def _build_device_section(self):
        dev = self._card("① Device")

        tk.Label(dev, text="Enter Target IP Address", font=UI, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))
        input_row = tk.Frame(dev, bg=CARD)
        input_row.pack(fill="x", pady=(0, 8))
        input_row.columnconfigure(0, weight=1)

        # Pre-populate entry with your default IP variable
        self._device_var = tk.StringVar(value=DEFAULT_IP)

        self._device_entry = self._entry(input_row, self._device_var)
        self._device_entry.grid(row=0, column=0, sticky="ew", ipady=5)

        # Connect / Disconnect / Stop ADB buttons
        btn_row = tk.Frame(dev, bg=CARD)
        btn_row.pack(fill="x", pady=(4, 0))

        self._btn_connect = self._btn(btn_row, "Connect", self._on_connect, ACCENT2)
        self._btn_connect.pack(side="left", padx=(0, 8))

        self._btn_disconnect = self._btn(btn_row, "Disconnect Device", self._on_disconnect, SURFACE)
        self._btn_disconnect.pack(side="left", padx=(0, 8))

        self._btn_stop_adb = self._btn(btn_row, "⏹  Stop ADB Server", self._on_stop_adb, RED_BTN)
        self._btn_stop_adb.pack(side="left")

        self._conn_badge = tk.Label(btn_row, text="", font=UI, bg=CARD, fg=SUCCESS)
        self._conn_badge.pack(side="left", padx=12)

    # ── Install APK card ──────────────────────────────────────────────────────
    def _build_install_section(self):
        apk = self._card("② Install APK")

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

        opt = tk.Frame(apk, bg=CARD)
        opt.pack(fill="x", pady=(0, 10))
        self._uninstall_first = tk.BooleanVar(value=True)
        self._show_version    = tk.BooleanVar(value=True)
        for label, var in [("Uninstall before installing", self._uninstall_first),
                           ("Show version after install",  self._show_version)]:
            tk.Checkbutton(opt, text=label, variable=var,
                           bg=CARD, fg=TEXT, selectcolor=SURFACE,
                           activebackground=CARD, activeforeground=TEXT,
                           font=UI, cursor="hand2").pack(anchor="w")

        self._btn_install = self._btn(apk, "  ▶  Install APK  ",
                                      self._on_install, ACCENT2,
                                      font=("Segoe UI Semibold", 11))
        self._btn_install.pack(fill="x", ipady=7, pady=(4, 0))

        self._install_progress = ttk.Progressbar(apk,
                                                 style="Accent.Horizontal.TProgressbar",
                                                 mode="indeterminate")
        self._install_progress.pack(fill="x", pady=(6, 0))

    # ── Send Text card ────────────────────────────────────────────────────────
    def _build_text_section(self):
        txt = self._card("③ Send Text  (same session — no reconnect needed)")

        tk.Label(txt, text="Text to Send", font=UI, bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))
        self._text_var = tk.StringVar()
        text_entry = tk.Entry(txt, textvariable=self._text_var,
                              font=("Consolas", 11),
                              bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
                              relief="flat", highlightthickness=1,
                              highlightbackground=BORDER, highlightcolor=ACCENT)
        text_entry.pack(fill="x", ipady=7, pady=(0, 10))
        text_entry.bind("<Return>", lambda e: self._on_send_text())

        self._btn_send = self._btn(txt, "  ▶  Send Text  ",
                                   self._on_send_text, ACCENT2,
                                   font=("Segoe UI Semibold", 11))
        self._btn_send.pack(fill="x", ipady=7)

        self._text_progress = ttk.Progressbar(txt,
                                              style="Accent.Horizontal.TProgressbar",
                                              mode="indeterminate")
        self._text_progress.pack(fill="x", pady=(6, 0))

    # ── Log panel ─────────────────────────────────────────────────────────────
    def _build_log(self):
        outer = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        hdr = tk.Frame(outer, bg=CARD)
        hdr.pack(fill="x", padx=14, pady=(8, 4))
        tk.Label(hdr, text="Session Log", font=HEAD, bg=CARD, fg=ACCENT).pack(side="left")
        self._btn(hdr, "Clear", self._clear_log, SURFACE).pack(side="right")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=14)
        self._log = scrolledtext.ScrolledText(
            outer, bg=SURFACE, fg=TEXT, font=MONO,
            relief="flat", state="disabled", wrap="word", padx=8, pady=6, height=9
        )
        self._log.pack(fill="both", expand=True, padx=8, pady=8)
        self._log.tag_config("ok",   foreground=SUCCESS)
        self._log.tag_config("err",  foreground=ERROR)
        self._log.tag_config("warn", foreground=WARNING)
        self._log.tag_config("info", foreground=ACCENT)
        self._log.tag_config("dim",  foreground=SUBTEXT)
        self._log.tag_config("sep",  foreground=BORDER)

    # ═════════════════════════════ WIDGET HELPERS ════════════════════════════

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Accent.Horizontal.TProgressbar",
                        troughcolor=SURFACE, background=ACCENT,
                        darkcolor=ACCENT, lightcolor=ACCENT, bordercolor=CARD)

    def _card(self, title):
        outer = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="x", padx=24, pady=(0, 10))
        hdr = tk.Frame(outer, bg=CARD)
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(hdr, text=title, font=HEAD, bg=CARD, fg=ACCENT).pack(side="left")
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", padx=14)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=10)
        return inner

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

    # ═════════════════════════════ LOGGING ═══════════════════════════════════

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
    def sep(self):     self._write("─" * 55, "sep")

    def _set_status(self, text, colour):
        self.after(0, lambda: (
            self._status_lbl.config(text=text, fg=colour),
            self._dot.config(fg=colour)
        ))

    def _clear_log(self):
        self._log.config(state="normal")
        self._log.delete("1.0", "end")
        self._log.config(state="disabled")

    def _set_badge(self, text, colour=SUCCESS):
        self.after(0, lambda: self._conn_badge.config(text=text, fg=colour))

    def _busy_install(self, on):
        self.after(0, lambda: (
            self._install_progress.start(12) if on else self._install_progress.stop(),
            self._btn_install.config(state="disabled" if on else "normal")
        ))

    def _busy_text(self, on):
        self.after(0, lambda: (
            self._text_progress.start(12) if on else self._text_progress.stop(),
            self._btn_send.config(state="disabled" if on else "normal")
        ))

    def _run(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    # ═════════════════════════════ EVENT HANDLERS ════════════════════════════

    def _on_browse(self):
        path = filedialog.askopenfilename(
            title="Select APK file",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if path:
            self._apk_var.set(path)

    def _on_connect(self):
        ip = self._device_var.get().strip()
        if not ip:
            messagebox.showwarning("No Target IP", "Please enter a valid IP address.")
            return
        self._run(self._connect_device, ip)

    def _on_disconnect(self):
        if not self._connected_ip:
            messagebox.showinfo("Not Connected", "No active device connection.")
            return
        self._run(self._disconnect_device)

    def _on_stop_adb(self):
        self._run(self._stop_adb_daemon)

    def _on_install(self):
        ip   = self._device_var.get().strip()
        pkg  = self._pkg_var.get().strip()
        apk  = self._apk_var.get().strip()

        if not ip:
            messagebox.showwarning("No Target IP", "Please enter an IP address."); return
        if not pkg:
            messagebox.showwarning("Missing Package", "Enter the package name."); return
        if not apk or not os.path.isfile(apk):
            messagebox.showwarning("Missing APK", "Browse to a valid .apk file."); return

        self._run(self._install_flow, ip, pkg, apk,
                  self._uninstall_first.get(), self._show_version.get())

    def _on_send_text(self):
        text = self._text_var.get().strip()
        if not text:
            messagebox.showwarning("No Text", "Enter text to send."); return

        if self._device and self._connected_ip:
            self._run(self._send_text_on_device, text)
        else:
            ip = self._device_var.get().strip()
            if not ip:
                messagebox.showwarning("No Target IP", "Please enter an IP address."); return
            self._run(self._connect_then_send, ip, text)

    # ═════════════════════════════ ADB LOGIC ═════════════════════════════════

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
            return False
        try:
            self._client = AdbClient(host="127.0.0.1", port=5037)
            return True
        except Exception as e:
            self.err(f"ADB client init failed: {e}")
            return False

    def _ensure_client(self):
        if self._client:
            return True
        return self._init_client()

    def _connect_device(self, ip):
        self.sep()
        self.info(f"Connecting to {ip}:5555 …")
        if not self._ensure_client():
            return False
        try:
            self._client.remote_connect(ip, 5555)
            devices = self._client.devices()
            if not devices:
                self.err("No devices visible after connect. Check ADB debugging on TV.")
                return False
            
            # Find the connected remote device match
            self._device = devices[0]
            self._connected_ip = ip
            self.ok(f"Session open → {self._device.serial}")
            self._set_status(f"Connected · {ip}", SUCCESS)
            self._set_badge("● Connected")
            return True
        except Exception as e:
            self.err(f"Connection failed: {e}")
            return False

    def _disconnect_device(self):
        ip = self._connected_ip
        self.info(f"Disconnecting {ip} …")
        try:
            if self._client and ip:
                self._client.remote_disconnect(ip)
            self._device = None
            self._connected_ip = None
            self.ok("Device disconnected.")
            self._set_status("Disconnected", WARNING)
            self._set_badge("")
        except Exception as e:
            self.err(f"Disconnect error: {e}")

    def _stop_adb_daemon(self):
        self.sep()
        self.info("Stopping ADB server…")
        try:
            subprocess.run(["adb", "kill-server"], capture_output=True,
                           text=True, check=True)
            self._device = None
            self._connected_ip = None
            self._client = None
            self.ok("ADB server stopped. Session ended.")
            self._set_status("ADB stopped", WARNING)
            self._set_badge("")
        except subprocess.CalledProcessError as e:
            self.err(f"Stop error: {e.stderr.strip()}")

    def _install_flow(self, ip, pkg, apk, uninstall_first, show_version):
        self._busy_install(True)
        self.sep()
        self.info(f"=== Install session: {ip} ===")
        try:
            if self._connected_ip != ip:
                if not self._connect_device(ip):
                    return
            else:
                self.dim(f"Reusing existing session → {self._device.serial}")

            device = self._device
            self._check_version(device, pkg, "Pre-install")

            if uninstall_first:
                self.info("Uninstalling existing package…")
                try:
                    device.uninstall(pkg)
                    self.ok("Package uninstalled.")
                except Exception as e:
                    self.warn(f"Uninstall skipped: {e}")

            self.info(f"Installing {os.path.basename(apk)} …")
            device.install(apk)

            if device.is_installed(pkg):
                self.ok("Installation successful! ✓")
                if show_version:
                    self._check_version(device, pkg, "Post-install")
                self._set_status(f"Installed · {ip}", SUCCESS)
                self.info("Session still active — text can be sent without reconnecting.")
            else:
                self.err("Install completed but package not found. Check package name / APK.")
                self._set_status("Install failed", ERROR)

        except Exception as e:
            self.err(f"Install error: {e}")
            self._set_status("Error", ERROR)
        finally:
            self._busy_install(False)

    def _check_version(self, device, pkg, label):
        try:
            ver = device.shell(f"dumpsys package {pkg} | grep versionName")
            if ver.strip():
                self.dim(f"{label} version → {ver.strip()}")
            else:
                self.warn(f"{label}: package '{pkg}' not found on device.")
        except Exception as e:
            self.warn(f"Version check error: {e}")

    def _connect_then_send(self, ip, text):
        if self._connect_device(ip):
            self._send_text_on_device(text)

    def _send_text_on_device(self, text):
        self._busy_text(True)
        self.sep()
        self.info(f"Sending text on {self._connected_ip} …")
        try:
            output = self._device.shell(f'input text "{text}" && echo "success"')
            if "success" in output:
                self.ok(f'Text sent → "{text}"')
                self._set_status(f"Text sent · {self._connected_ip}", SUCCESS)
            else:
                self.err(f"Send failed. Device output: {output.strip() or '(empty)'}")
                self._set_status("Text send failed", ERROR)
        except Exception as e:
            self.err(f"Text send error: {e}")
            self._set_status("Error", ERROR)
        finally:
            self._busy_text(False)


if __name__ == "__main__":
    app = ADBManagerApp()
    app._apply_styles()
    app.mainloop()